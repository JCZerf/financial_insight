from django.db import models
import uuid


class RealEstateFund(models.Model):
    """Dados gerais extraídos de fii_resultado.php (snapshot geral)."""

    run_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    source = models.CharField(max_length=120)
    url = models.URLField(max_length=500)
    collected_at_utc = models.DateTimeField(db_index=True)

    ticker = models.CharField(max_length=20, db_index=True, unique=True)
    segment = models.CharField(max_length=120, blank=True, null=True)

    price = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    ffo_yield = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    dividend_yield = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    price_to_book = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)

    market_value = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    liquidity = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)

    property_count = models.PositiveIntegerField(blank=True, null=True)
    price_per_sqm = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    rent_per_sqm = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    cap_rate = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    avg_vacancy = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "real_estate_fund"
        indexes = [
            models.Index(fields=["ticker", "collected_at_utc"], name="idx_ref_ticker_collected"),
        ]

    def __str__(self) -> str:
        return f"{self.ticker} ({self.run_id})"


class RealEstateFundDetail(models.Model):
    """Dados detalhados extraídos de detalhes.php?papel=... (snapshot detalhado)."""

    fund = models.OneToOneField(
        RealEstateFund,
        on_delete=models.CASCADE,
        related_name="detail",
    )

    run_id = models.UUIDField(db_index=True)
    source = models.CharField(max_length=120)
    url = models.URLField(max_length=500)
    detail_url = models.URLField(max_length=500, blank=True, null=True)
    collected_at_utc = models.DateTimeField(db_index=True)
    collection_status = models.CharField(max_length=32, blank=True, null=True)

    # identification
    identification_name = models.TextField(blank=True, null=True)
    identification_segment = models.CharField(max_length=120, blank=True, null=True)
    identification_mandate = models.CharField(max_length=120, blank=True, null=True)
    identification_management = models.CharField(max_length=120, blank=True, null=True)

    # market
    market_price = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    market_last_quote_date = models.CharField(max_length=32, blank=True, null=True)
    market_low_52w = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    market_high_52w = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    market_avg_volume_2m = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    market_market_value = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    market_share_count = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    market_report_date = models.CharField(max_length=32, blank=True, null=True)
    market_last_quarter_info_date = models.CharField(max_length=32, blank=True, null=True)
    oscillations = models.JSONField(blank=True, null=True)

    # indicators
    indicators_ffo_yield = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    indicators_ffo_per_share = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    indicators_dividend_yield = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    indicators_dividend_per_share = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    indicators_price_to_book = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    indicators_book_value_per_share = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)

    # results
    results_last_12m_revenue = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    results_last_3m_revenue = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    results_last_12m_asset_sales = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    results_last_3m_asset_sales = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    results_last_12m_ffo = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    results_last_3m_ffo = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    results_last_12m_distributed_income = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    results_last_3m_distributed_income = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)

    # balance sheet
    balance_sheet_assets = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)
    balance_sheet_net_equity = models.DecimalField(max_digits=24, decimal_places=2, blank=True, null=True)

    # properties
    properties_property_count = models.PositiveIntegerField(blank=True, null=True)
    properties_unit_count = models.PositiveIntegerField(blank=True, null=True)
    properties_area_sqm = models.DecimalField(max_digits=24, decimal_places=4, blank=True, null=True)
    properties_price_per_sqm = models.DecimalField(max_digits=24, decimal_places=4, blank=True, null=True)
    properties_rent_per_sqm = models.DecimalField(max_digits=24, decimal_places=4, blank=True, null=True)
    properties_cap_rate = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    properties_avg_vacancy = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    properties_to_equity_percent = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "real_estate_fund_detail"
        indexes = [
            models.Index(fields=["run_id", "collection_status"], name="idx_ref_detail_run_status"),
        ]

    def __str__(self) -> str:
        return f"Detail {self.fund.ticker} ({self.run_id})"
