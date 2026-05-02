from decimal import Decimal, InvalidOperation

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import RealEstateFund
from api.serializers import (
    DashboardResponseSerializer,
    FundDetailResponseSerializer,
    FundListResponseSerializer,
)
from api.services import (
    build_filters,
    dashboard_payload,
    filtered_funds,
    fund_card,
    fund_detail_payload,
    parse_limit,
    rank_funds,
)


FILTER_PARAMETERS = [
    OpenApiParameter(
        name="segment",
        description="Filtra por segmento do FII.",
        required=False,
        type=str,
    ),
    OpenApiParameter(
        name="min_dividend_yield",
        description="Dividend Yield minimo em percentual. Exemplo: 8.5.",
        required=False,
        type=Decimal,
    ),
    OpenApiParameter(
        name="max_price_to_book",
        description="P/VP maximo. Exemplo: 1.0.",
        required=False,
        type=Decimal,
    ),
    OpenApiParameter(
        name="min_liquidity",
        description="Liquidez minima. Exemplo: 500000.",
        required=False,
        type=Decimal,
    ),
    OpenApiParameter(
        name="limit",
        description="Quantidade de itens por bloco do dashboard. Valor maximo: 50.",
        required=False,
        type=int,
    ),
]


class InitialDashboardView(APIView):
    @extend_schema(
        tags=["Investments"],
        operation_id="investments_dashboard_initial",
        summary="Initial FII dashboard",
        description=(
            "Returns an initial dashboard payload for the frontend, including opportunity ranking, "
            "summary cards, high dividend funds, discounted funds, liquid funds and segment summaries."
        ),
        parameters=FILTER_PARAMETERS,
        responses={200: DashboardResponseSerializer},
    )
    def get(self, request):
        try:
            filters = build_filters(request.query_params)
        except (InvalidOperation, ValueError):
            return Response(
                {"detail": "Invalid filter value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(dashboard_payload(filters))


class FundListView(APIView):
    @extend_schema(
        tags=["Investments"],
        operation_id="investments_funds_list",
        summary="List FIIs",
        description="Returns FIIs with the same ranking score used by the initial dashboard.",
        parameters=FILTER_PARAMETERS,
        responses={200: FundListResponseSerializer},
    )
    def get(self, request):
        try:
            filters = build_filters(request.query_params)
        except (InvalidOperation, ValueError):
            return Response(
                {"detail": "Invalid filter value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        funds = list(filtered_funds(filters))
        ranked_by_ticker = {item["ticker"]: item for item in rank_funds(funds)}
        results = []
        for fund in funds:
            results.append(ranked_by_ticker.get(fund.ticker, fund_card(fund)))

        results.sort(
            key=lambda item: (
                item.get("score", -1),
                item.get("dividend_yield") or 0,
                item.get("liquidity") or 0,
            ),
            reverse=True,
        )

        return Response(
            {
                "count": len(results),
                "results": results[: parse_limit(request.query_params.get("limit"))],
            }
        )


class FundDetailView(APIView):
    @extend_schema(
        tags=["Investments"],
        operation_id="investments_funds_detail",
        summary="Get FII detail",
        description="Returns consolidated general and detailed Fundamentus data for a single FII.",
        responses={200: FundDetailResponseSerializer},
    )
    def get(self, request, ticker: str):
        fund = get_object_or_404(
            RealEstateFund.objects.select_related("detail"),
            ticker__iexact=ticker,
        )
        return Response(fund_detail_payload(fund))
