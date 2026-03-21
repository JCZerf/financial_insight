import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import Json, execute_values

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


GENERAL_COLUMNS = [
    "run_id",
    "source",
    "url",
    "collected_at_utc",
    "ticker",
    "segment",
    "price",
    "ffo_yield",
    "dividend_yield",
    "price_to_book",
    "market_value",
    "liquidity",
    "property_count",
    "price_per_sqm",
    "rent_per_sqm",
    "cap_rate",
    "avg_vacancy",
    "created_at",
    "updated_at",
]

DETAIL_COLUMNS = [
    "fund_id",
    "run_id",
    "source",
    "url",
    "detail_url",
    "collected_at_utc",
    "collection_status",
    "identification_name",
    "identification_segment",
    "identification_mandate",
    "identification_management",
    "market_price",
    "market_last_quote_date",
    "market_low_52w",
    "market_high_52w",
    "market_avg_volume_2m",
    "market_market_value",
    "market_share_count",
    "market_report_date",
    "market_last_quarter_info_date",
    "oscillations",
    "indicators_ffo_yield",
    "indicators_ffo_per_share",
    "indicators_dividend_yield",
    "indicators_dividend_per_share",
    "indicators_price_to_book",
    "indicators_book_value_per_share",
    "results_last_12m_revenue",
    "results_last_3m_revenue",
    "results_last_12m_asset_sales",
    "results_last_3m_asset_sales",
    "results_last_12m_ffo",
    "results_last_3m_ffo",
    "results_last_12m_distributed_income",
    "results_last_3m_distributed_income",
    "balance_sheet_assets",
    "balance_sheet_net_equity",
    "properties_property_count",
    "properties_unit_count",
    "properties_area_sqm",
    "properties_price_per_sqm",
    "properties_rent_per_sqm",
    "properties_cap_rate",
    "properties_avg_vacancy",
    "properties_to_equity_percent",
    "created_at",
    "updated_at",
]


def _conn() -> Any:
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "financial_insight"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )


def _to_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def upsert_general_rows(
    *,
    run_id: str,
    source: str,
    url: str,
    collected_at_utc: str,
    rows: list[dict[str, Any]],
) -> dict[str, int]:
    if not rows:
        return {"upserted": 0, "posted": 0, "updated": 0}

    now_dt = datetime.now(timezone.utc)
    values = [
        (
            run_id,
            source,
            url,
            _to_dt(collected_at_utc),
            row.get("ticker"),
            row.get("segment"),
            row.get("price"),
            row.get("ffo_yield"),
            row.get("dividend_yield"),
            row.get("price_to_book"),
            row.get("market_value"),
            row.get("liquidity"),
            row.get("property_count"),
            row.get("price_per_sqm"),
            row.get("rent_per_sqm"),
            row.get("cap_rate"),
            row.get("avg_vacancy"),
            now_dt,
            now_dt,
        )
        for row in rows
    ]

    insert_sql = f"""
        INSERT INTO real_estate_fund ({", ".join(GENERAL_COLUMNS)})
        VALUES %s
        ON CONFLICT (ticker) DO UPDATE SET
            run_id = EXCLUDED.run_id,
            source = EXCLUDED.source,
            url = EXCLUDED.url,
            collected_at_utc = EXCLUDED.collected_at_utc,
            segment = EXCLUDED.segment,
            price = EXCLUDED.price,
            ffo_yield = EXCLUDED.ffo_yield,
            dividend_yield = EXCLUDED.dividend_yield,
            price_to_book = EXCLUDED.price_to_book,
            market_value = EXCLUDED.market_value,
            liquidity = EXCLUDED.liquidity,
            property_count = EXCLUDED.property_count,
            price_per_sqm = EXCLUDED.price_per_sqm,
            rent_per_sqm = EXCLUDED.rent_per_sqm,
            cap_rate = EXCLUDED.cap_rate,
            avg_vacancy = EXCLUDED.avg_vacancy,
            updated_at = NOW()
        RETURNING (xmax = 0) AS posted
    """

    with _conn() as conn:
        with conn.cursor() as cur:
            upsert_rows = execute_values(cur, insert_sql, values, page_size=500, fetch=True)
        conn.commit()

    posted = sum(1 for row in upsert_rows if row[0])
    updated = len(upsert_rows) - posted
    return {"upserted": len(rows), "posted": posted, "updated": updated}


def _detail_tuple(
    *,
    fund_id: int,
    run_id: str,
    source: str,
    url: str,
    collected_at_utc: str,
    row: dict[str, Any],
) -> tuple[Any, ...]:
    identification = row.get("identification", {}) or {}
    market = row.get("market", {}) or {}
    indicators = row.get("indicators", {}) or {}
    oscillations = row.get("oscillations")
    results = row.get("results", {}) or {}
    balance_sheet = row.get("balance_sheet", {}) or {}
    properties = row.get("properties", {}) or {}

    now_dt = datetime.now(timezone.utc)
    return (
        fund_id,
        run_id,
        source,
        url,
        row.get("detail_url"),
        _to_dt(collected_at_utc),
        row.get("collection_status"),
        identification.get("name"),
        identification.get("segment"),
        identification.get("mandate"),
        identification.get("management"),
        market.get("price"),
        market.get("last_quote_date"),
        market.get("low_52w"),
        market.get("high_52w"),
        market.get("avg_volume_2m"),
        market.get("market_value"),
        market.get("share_count"),
        market.get("report_date"),
        market.get("last_quarter_info_date"),
        Json(oscillations) if oscillations is not None else None,
        indicators.get("ffo_yield"),
        indicators.get("ffo_per_share"),
        indicators.get("dividend_yield"),
        indicators.get("dividend_per_share"),
        indicators.get("price_to_book"),
        indicators.get("book_value_per_share"),
        results.get("last_12m_revenue"),
        results.get("last_3m_revenue"),
        results.get("last_12m_asset_sales"),
        results.get("last_3m_asset_sales"),
        results.get("last_12m_ffo"),
        results.get("last_3m_ffo"),
        results.get("last_12m_distributed_income"),
        results.get("last_3m_distributed_income"),
        balance_sheet.get("assets"),
        balance_sheet.get("net_equity"),
        properties.get("property_count"),
        properties.get("unit_count"),
        properties.get("area_sqm"),
        properties.get("price_per_sqm"),
        properties.get("rent_per_sqm"),
        properties.get("cap_rate"),
        properties.get("avg_vacancy"),
        properties.get("properties_to_equity_percent"),
        now_dt,
        now_dt,
    )


def upsert_detail_rows(
    *,
    run_id: str,
    source: str,
    url: str,
    collected_at_utc: str,
    rows: list[dict[str, Any]],
) -> dict[str, int]:
    if not rows:
        return {"upserted": 0, "posted": 0, "updated": 0, "skipped": 0}

    tickers = [row.get("ticker") for row in rows if row.get("ticker")]
    if not tickers:
        return {"upserted": 0, "posted": 0, "updated": 0, "skipped": len(rows)}

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, ticker FROM real_estate_fund WHERE ticker = ANY(%s)",
                (tickers,),
            )
            mapping = {ticker: fund_id for fund_id, ticker in cur.fetchall()}

            values: list[tuple[Any, ...]] = []
            skipped = 0
            for row in rows:
                ticker = row.get("ticker")
                fund_id = mapping.get(ticker)
                if not fund_id:
                    skipped += 1
                    continue
                values.append(
                    _detail_tuple(
                        fund_id=fund_id,
                        run_id=run_id,
                        source=source,
                        url=url,
                        collected_at_utc=collected_at_utc,
                        row=row,
                    )
                )

            upsert_rows: list[tuple[bool]] = []
            if values:
                insert_sql = f"""
                    INSERT INTO real_estate_fund_detail ({", ".join(DETAIL_COLUMNS)})
                    VALUES %s
                    ON CONFLICT (fund_id) DO UPDATE SET
                        run_id = EXCLUDED.run_id,
                        source = EXCLUDED.source,
                        url = EXCLUDED.url,
                        detail_url = EXCLUDED.detail_url,
                        collected_at_utc = EXCLUDED.collected_at_utc,
                        collection_status = EXCLUDED.collection_status,
                        identification_name = EXCLUDED.identification_name,
                        identification_segment = EXCLUDED.identification_segment,
                        identification_mandate = EXCLUDED.identification_mandate,
                        identification_management = EXCLUDED.identification_management,
                        market_price = EXCLUDED.market_price,
                        market_last_quote_date = EXCLUDED.market_last_quote_date,
                        market_low_52w = EXCLUDED.market_low_52w,
                        market_high_52w = EXCLUDED.market_high_52w,
                        market_avg_volume_2m = EXCLUDED.market_avg_volume_2m,
                        market_market_value = EXCLUDED.market_market_value,
                        market_share_count = EXCLUDED.market_share_count,
                        market_report_date = EXCLUDED.market_report_date,
                        market_last_quarter_info_date = EXCLUDED.market_last_quarter_info_date,
                        oscillations = EXCLUDED.oscillations,
                        indicators_ffo_yield = EXCLUDED.indicators_ffo_yield,
                        indicators_ffo_per_share = EXCLUDED.indicators_ffo_per_share,
                        indicators_dividend_yield = EXCLUDED.indicators_dividend_yield,
                        indicators_dividend_per_share = EXCLUDED.indicators_dividend_per_share,
                        indicators_price_to_book = EXCLUDED.indicators_price_to_book,
                        indicators_book_value_per_share = EXCLUDED.indicators_book_value_per_share,
                        results_last_12m_revenue = EXCLUDED.results_last_12m_revenue,
                        results_last_3m_revenue = EXCLUDED.results_last_3m_revenue,
                        results_last_12m_asset_sales = EXCLUDED.results_last_12m_asset_sales,
                        results_last_3m_asset_sales = EXCLUDED.results_last_3m_asset_sales,
                        results_last_12m_ffo = EXCLUDED.results_last_12m_ffo,
                        results_last_3m_ffo = EXCLUDED.results_last_3m_ffo,
                        results_last_12m_distributed_income = EXCLUDED.results_last_12m_distributed_income,
                        results_last_3m_distributed_income = EXCLUDED.results_last_3m_distributed_income,
                        balance_sheet_assets = EXCLUDED.balance_sheet_assets,
                        balance_sheet_net_equity = EXCLUDED.balance_sheet_net_equity,
                        properties_property_count = EXCLUDED.properties_property_count,
                        properties_unit_count = EXCLUDED.properties_unit_count,
                        properties_area_sqm = EXCLUDED.properties_area_sqm,
                        properties_price_per_sqm = EXCLUDED.properties_price_per_sqm,
                        properties_rent_per_sqm = EXCLUDED.properties_rent_per_sqm,
                        properties_cap_rate = EXCLUDED.properties_cap_rate,
                        properties_avg_vacancy = EXCLUDED.properties_avg_vacancy,
                        properties_to_equity_percent = EXCLUDED.properties_to_equity_percent,
                        updated_at = NOW()
                    RETURNING (xmax = 0) AS posted
                """
                upsert_rows = execute_values(cur, insert_sql, values, page_size=500, fetch=True)
            else:
                skipped = len(rows)

        conn.commit()

    posted = sum(1 for row in upsert_rows if row[0])
    updated = len(upsert_rows) - posted
    return {"upserted": len(values), "posted": posted, "updated": updated, "skipped": skipped}
