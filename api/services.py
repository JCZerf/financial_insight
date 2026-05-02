from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from statistics import median
from typing import Iterable

from django.db.models import Avg, Count, Max, Q

from api.models import RealEstateFund


DEFAULT_DASHBOARD_LIMIT = 10
MAX_DASHBOARD_LIMIT = 50


@dataclass(frozen=True)
class FundFilters:
    segment: str | None = None
    min_dividend_yield: Decimal | None = None
    max_price_to_book: Decimal | None = None
    min_liquidity: Decimal | None = None
    limit: int = DEFAULT_DASHBOARD_LIMIT


def parse_decimal(value: str | None) -> Decimal | None:
    if value in (None, ""):
        return None
    return Decimal(str(value).replace(",", "."))


def parse_limit(value: str | None, default: int = DEFAULT_DASHBOARD_LIMIT) -> int:
    if value in (None, ""):
        return default
    return min(max(int(value), 1), MAX_DASHBOARD_LIMIT)


def build_filters(params) -> FundFilters:
    return FundFilters(
        segment=params.get("segment") or None,
        min_dividend_yield=parse_decimal(params.get("min_dividend_yield")),
        max_price_to_book=parse_decimal(params.get("max_price_to_book")),
        min_liquidity=parse_decimal(params.get("min_liquidity")),
        limit=parse_limit(params.get("limit")),
    )


def filtered_funds(filters: FundFilters):
    queryset = RealEstateFund.objects.select_related("detail").all()

    if filters.segment:
        queryset = queryset.filter(
            Q(segment__iexact=filters.segment)
            | Q(detail__identification_segment__iexact=filters.segment)
        )
    if filters.min_dividend_yield is not None:
        queryset = queryset.filter(dividend_yield__gte=filters.min_dividend_yield)
    if filters.max_price_to_book is not None:
        queryset = queryset.filter(price_to_book__lte=filters.max_price_to_book)
    if filters.min_liquidity is not None:
        queryset = queryset.filter(liquidity__gte=filters.min_liquidity)

    return queryset


def dashboard_payload(filters: FundFilters) -> dict:
    queryset = filtered_funds(filters)
    funds = list(queryset)
    ranked = rank_funds(funds)
    opportunities = ranked[: filters.limit]

    return {
        "metadata": build_metadata(funds, ranked),
        "summary": build_summary(funds, ranked),
        "opportunities": opportunities,
        "high_dividend": top_funds(ranked, "dividend_yield", filters.limit),
        "discounted": discounted_funds(ranked, filters.limit),
        "most_liquid": top_funds(ranked, "liquidity", filters.limit),
        "segments": segment_summary(queryset),
        "applied_filters": {
            "segment": filters.segment,
            "min_dividend_yield": decimal_to_float(filters.min_dividend_yield),
            "max_price_to_book": decimal_to_float(filters.max_price_to_book),
            "min_liquidity": decimal_to_float(filters.min_liquidity),
            "limit": filters.limit,
        },
    }


def fund_detail_payload(fund: RealEstateFund) -> dict:
    item = fund_card(fund)
    detail = getattr(fund, "detail", None)

    if not detail:
        item["detail"] = None
        return item

    item["detail"] = {
        "identification": {
            "name": detail.identification_name,
            "segment": detail.identification_segment,
            "mandate": detail.identification_mandate,
            "management": detail.identification_management,
        },
        "market": {
            "price": decimal_to_float(detail.market_price),
            "last_quote_date": detail.market_last_quote_date,
            "low_52w": decimal_to_float(detail.market_low_52w),
            "high_52w": decimal_to_float(detail.market_high_52w),
            "avg_volume_2m": decimal_to_float(detail.market_avg_volume_2m),
            "market_value": decimal_to_float(detail.market_market_value),
            "share_count": decimal_to_float(detail.market_share_count),
            "report_date": detail.market_report_date,
            "last_quarter_info_date": detail.market_last_quarter_info_date,
            "oscillations": detail.oscillations,
        },
        "indicators": {
            "ffo_yield": decimal_to_float(detail.indicators_ffo_yield),
            "ffo_per_share": decimal_to_float(detail.indicators_ffo_per_share),
            "dividend_yield": decimal_to_float(detail.indicators_dividend_yield),
            "dividend_per_share": decimal_to_float(detail.indicators_dividend_per_share),
            "price_to_book": decimal_to_float(detail.indicators_price_to_book),
            "book_value_per_share": decimal_to_float(detail.indicators_book_value_per_share),
        },
        "results": {
            "last_12m_revenue": decimal_to_float(detail.results_last_12m_revenue),
            "last_3m_revenue": decimal_to_float(detail.results_last_3m_revenue),
            "last_12m_asset_sales": decimal_to_float(detail.results_last_12m_asset_sales),
            "last_3m_asset_sales": decimal_to_float(detail.results_last_3m_asset_sales),
            "last_12m_ffo": decimal_to_float(detail.results_last_12m_ffo),
            "last_3m_ffo": decimal_to_float(detail.results_last_3m_ffo),
            "last_12m_distributed_income": decimal_to_float(detail.results_last_12m_distributed_income),
            "last_3m_distributed_income": decimal_to_float(detail.results_last_3m_distributed_income),
        },
        "balance_sheet": {
            "assets": decimal_to_float(detail.balance_sheet_assets),
            "net_equity": decimal_to_float(detail.balance_sheet_net_equity),
        },
        "properties": {
            "property_count": detail.properties_property_count,
            "unit_count": detail.properties_unit_count,
            "area_sqm": decimal_to_float(detail.properties_area_sqm),
            "price_per_sqm": decimal_to_float(detail.properties_price_per_sqm),
            "rent_per_sqm": decimal_to_float(detail.properties_rent_per_sqm),
            "cap_rate": decimal_to_float(detail.properties_cap_rate),
            "avg_vacancy": decimal_to_float(detail.properties_avg_vacancy),
            "to_equity_percent": decimal_to_float(detail.properties_to_equity_percent),
        },
    }
    return item


def build_metadata(funds: list[RealEstateFund], ranked: list[dict]) -> dict:
    collected_at_values = [fund.collected_at_utc for fund in funds if fund.collected_at_utc]
    return {
        "asset_class": "FII",
        "total_funds": len(funds),
        "ranked_funds": len(ranked),
        "latest_collected_at_utc": max(collected_at_values).isoformat() if collected_at_values else None,
        "scoring": {
            "dividend_yield_weight": 0.45,
            "price_to_book_weight": 0.35,
            "liquidity_weight": 0.20,
            "note": "Pontuacao objetiva para triagem inicial; nao representa recomendacao personalizada.",
        },
    }


def build_summary(funds: list[RealEstateFund], ranked: list[dict]) -> dict:
    dividend_yields = [fund.dividend_yield for fund in funds if fund.dividend_yield is not None]
    price_to_books = [fund.price_to_book for fund in funds if fund.price_to_book is not None]
    liquidities = [fund.liquidity for fund in funds if fund.liquidity is not None]
    best = ranked[0] if ranked else None

    return {
        "best_opportunity": best,
        "average_dividend_yield": average(dividend_yields),
        "median_price_to_book": decimal_to_float(median(price_to_books)) if price_to_books else None,
        "average_liquidity": average(liquidities),
        "discounted_funds_count": sum(1 for fund in funds if fund.price_to_book is not None and fund.price_to_book <= 1),
        "funds_with_details_count": sum(1 for fund in funds if hasattr(fund, "detail")),
    }


def rank_funds(funds: Iterable[RealEstateFund]) -> list[dict]:
    ranked = []
    for fund in funds:
        if not has_ranking_inputs(fund):
            continue
        score, factors = opportunity_score(fund)
        item = fund_card(fund)
        item["score"] = score
        item["score_factors"] = factors
        item["flags"] = opportunity_flags(fund)
        ranked.append(item)

    ranked.sort(
        key=lambda item: (
            item["score"],
            item["dividend_yield"] or 0,
            item["liquidity"] or 0,
        ),
        reverse=True,
    )
    for position, item in enumerate(ranked, start=1):
        item["rank"] = position
    return ranked


def fund_card(fund: RealEstateFund) -> dict:
    detail = getattr(fund, "detail", None)
    return {
        "ticker": fund.ticker,
        "name": detail.identification_name if detail else None,
        "segment": fund.segment or (detail.identification_segment if detail else None),
        "price": decimal_to_float(fund.price),
        "ffo_yield": decimal_to_float(fund.ffo_yield),
        "dividend_yield": decimal_to_float(fund.dividend_yield),
        "price_to_book": decimal_to_float(fund.price_to_book),
        "liquidity": decimal_to_float(fund.liquidity),
        "market_value": decimal_to_float(fund.market_value),
        "property_count": fund.property_count,
        "price_per_sqm": decimal_to_float(fund.price_per_sqm),
        "rent_per_sqm": decimal_to_float(fund.rent_per_sqm),
        "cap_rate": decimal_to_float(fund.cap_rate),
        "avg_vacancy": decimal_to_float(fund.avg_vacancy),
        "detail_available": detail is not None,
        "collected_at_utc": fund.collected_at_utc.isoformat() if fund.collected_at_utc else None,
    }


def has_ranking_inputs(fund: RealEstateFund) -> bool:
    return (
        fund.dividend_yield is not None
        and fund.price_to_book is not None
        and fund.liquidity is not None
        and fund.dividend_yield > 0
        and fund.price_to_book > 0
        and fund.liquidity > 0
    )


def opportunity_score(fund: RealEstateFund) -> tuple[float, dict]:
    dividend_score = clamp(float(fund.dividend_yield) / 12)
    price_to_book_score = clamp((1.25 - float(fund.price_to_book)) / 0.75)
    liquidity_score = clamp(float(fund.liquidity) / 1_000_000)

    score = (dividend_score * 0.45) + (price_to_book_score * 0.35) + (liquidity_score * 0.20)
    return round(score * 100, 2), {
        "dividend_yield": round(dividend_score * 100, 2),
        "price_to_book": round(price_to_book_score * 100, 2),
        "liquidity": round(liquidity_score * 100, 2),
    }


def opportunity_flags(fund: RealEstateFund) -> list[str]:
    flags = []
    if fund.dividend_yield is not None and fund.dividend_yield >= Decimal("10"):
        flags.append("high_dividend_yield")
    if fund.price_to_book is not None and fund.price_to_book <= Decimal("1"):
        flags.append("trading_below_book_value")
    if fund.liquidity is not None and fund.liquidity >= Decimal("1000000"):
        flags.append("high_liquidity")
    if fund.avg_vacancy is not None and fund.avg_vacancy <= Decimal("5"):
        flags.append("low_vacancy")
    return flags


def top_funds(ranked: list[dict], field: str, limit: int) -> list[dict]:
    return sorted(
        [item for item in ranked if item.get(field) is not None],
        key=lambda item: item[field],
        reverse=True,
    )[:limit]


def discounted_funds(ranked: list[dict], limit: int) -> list[dict]:
    return sorted(
        [item for item in ranked if item.get("price_to_book") is not None and item["price_to_book"] <= 1],
        key=lambda item: (item["price_to_book"], -item["score"]),
    )[:limit]


def segment_summary(queryset) -> list[dict]:
    rows = list(
        queryset.exclude(segment__isnull=True)
        .exclude(segment="")
        .values("segment")
        .annotate(
            funds_count=Count("id"),
            average_dividend_yield=Avg("dividend_yield"),
            average_price_to_book=Avg("price_to_book"),
            max_liquidity=Max("liquidity"),
        )
        .order_by("-funds_count", "segment")[:8]
    )
    for row in rows:
        row["average_dividend_yield"] = decimal_to_float(row["average_dividend_yield"])
        row["average_price_to_book"] = decimal_to_float(row["average_price_to_book"])
        row["max_liquidity"] = decimal_to_float(row["max_liquidity"])
    return rows


def average(values: list[Decimal]) -> float | None:
    if not values:
        return None
    return decimal_to_float(sum(values) / len(values))


def decimal_to_float(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


def clamp(value: float, minimum: float = 0, maximum: float = 1) -> float:
    return max(minimum, min(maximum, value))
