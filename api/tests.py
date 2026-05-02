from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from api.models import RealEstateFund, RealEstateFundDetail


class DashboardApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="investidor@example.com",
            name="Investidor Teste",
            birth_date="1990-01-01",
            cpf="12345678909",
            password="StrongPassword123!",
        )
        self.client.force_authenticate(self.user)

        self.good_fund = self.create_fund(
            ticker="GOOD11",
            segment="Logistica",
            dividend_yield="11.50",
            price_to_book="0.92",
            liquidity="1500000",
            avg_vacancy="3.50",
        )
        RealEstateFundDetail.objects.create(
            fund=self.good_fund,
            run_id=self.good_fund.run_id,
            source="fundamentus_detalhes_fii",
            url="https://www.fundamentus.com.br/detalhes.php?papel=GOOD11",
            detail_url="https://www.fundamentus.com.br/detalhes.php?papel=GOOD11",
            collected_at_utc=timezone.now(),
            collection_status="success",
            identification_name="Good Fundo Imobiliario",
            identification_segment="Logistica",
            indicators_dividend_yield=Decimal("11.50"),
            indicators_price_to_book=Decimal("0.92"),
        )

        self.create_fund(
            ticker="MID11",
            segment="Lajes Corporativas",
            dividend_yield="8.00",
            price_to_book="1.05",
            liquidity="600000",
        )
        self.create_fund(
            ticker="WEAK11",
            segment="Logistica",
            dividend_yield="4.00",
            price_to_book="1.40",
            liquidity="100000",
        )

    def test_dashboard_requires_authentication(self):
        client = APIClient()

        response = client.get("/api/dashboard/initial/")

        self.assertEqual(response.status_code, 401)

    def test_dashboard_returns_ranked_opportunities(self):
        response = self.client.get("/api/dashboard/initial/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["metadata"]["total_funds"], 3)
        self.assertEqual(payload["metadata"]["ranked_funds"], 3)
        self.assertEqual(payload["opportunities"][0]["ticker"], "GOOD11")
        self.assertIn("high_dividend_yield", payload["opportunities"][0]["flags"])
        self.assertIn("trading_below_book_value", payload["opportunities"][0]["flags"])
        self.assertEqual(payload["summary"]["best_opportunity"]["ticker"], "GOOD11")

    def test_dashboard_applies_filters(self):
        response = self.client.get(
            "/api/dashboard/initial/",
            {
                "segment": "Logistica",
                "min_dividend_yield": "10",
                "max_price_to_book": "1",
                "min_liquidity": "1000000",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["metadata"]["total_funds"], 1)
        self.assertEqual(payload["opportunities"][0]["ticker"], "GOOD11")
        self.assertEqual(payload["applied_filters"]["segment"], "Logistica")

    def test_fund_detail_returns_consolidated_detail(self):
        response = self.client.get("/api/funds/good11/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["ticker"], "GOOD11")
        self.assertEqual(payload["detail"]["identification"]["name"], "Good Fundo Imobiliario")
        self.assertEqual(payload["detail"]["indicators"]["price_to_book"], 0.92)

    def test_admin_ingestion_requires_superuser(self):
        response = self.client.post(
            "/api/admin/ingestion/run/",
            {"mode": "basic"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    @patch("api.views.run_manual_ingestion")
    def test_superuser_can_run_admin_ingestion(self, run_manual_ingestion_mock):
        superuser = get_user_model().objects.create_superuser(
            email="admin@example.com",
            name="Admin Teste",
            birth_date="1990-01-01",
            cpf="98765432100",
            password="StrongPassword123!",
        )
        self.client.force_authenticate(superuser)
        run_manual_ingestion_mock.return_value = {
            "mode": "detailed",
            "run_id": "run-123",
            "total_raw_rows": 3,
            "general_total": 3,
            "details_total": 3,
        }

        response = self.client.post(
            "/api/admin/ingestion/run/",
            {"mode": "detailed", "limit": 3},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["run_id"], "run-123")
        run_manual_ingestion_mock.assert_called_once_with(detailed=True, limit=3)

    def create_fund(
        self,
        *,
        ticker: str,
        segment: str,
        dividend_yield: str,
        price_to_book: str,
        liquidity: str,
        avg_vacancy: str | None = None,
    ) -> RealEstateFund:
        return RealEstateFund.objects.create(
            source="fundamentus_fii_resultado",
            url="https://www.fundamentus.com.br/fii_resultado.php",
            collected_at_utc=timezone.now(),
            ticker=ticker,
            segment=segment,
            price=Decimal("100.00"),
            dividend_yield=Decimal(dividend_yield),
            price_to_book=Decimal(price_to_book),
            market_value=Decimal("100000000.00"),
            liquidity=Decimal(liquidity),
            property_count=10,
            avg_vacancy=Decimal(avg_vacancy) if avg_vacancy else None,
        )
