from typing import Any, Optional


def _clean_text(value: str) -> str:
    return value.strip().replace("\xa0", " ")


def parse_br_number(value: str) -> Optional[float]:
    raw = _clean_text(value)
    if not raw or raw == "-":
        return None

    normalized = raw.replace(".", "").replace(",", ".")
    try:
        return float(normalized)
    except ValueError:
        return None


def parse_br_int(value: str) -> Optional[int]:
    parsed = parse_br_number(value)
    if parsed is None:
        return None
    return int(parsed)


def parse_br_percent(value: str) -> Optional[float]:
    raw = _clean_text(value).replace("%", "")
    if not raw or raw == "-":
        return None
    return parse_br_number(raw)


def normalize_fii_row(raw: dict[str, str]) -> dict[str, Any]:
    return {
        "ticker": _clean_text(raw.get("Papel", "")),
        "segment": _clean_text(raw.get("Segmento", "")),
        "price": parse_br_number(raw.get("Cotação", "")),
        "ffo_yield": parse_br_percent(raw.get("FFO Yield", "")),
        "dividend_yield": parse_br_percent(raw.get("Dividend Yield", "")),
        "price_to_book": parse_br_number(raw.get("P/VP", "")),
        "market_value": parse_br_number(raw.get("Valor de Mercado", "")),
        "liquidity": parse_br_number(raw.get("Liquidez", "")),
        "property_count": parse_br_int(raw.get("Qtd de imóveis", "")),
        "price_per_sqm": parse_br_number(raw.get("Preço do m2", "")),
        "rent_per_sqm": parse_br_number(raw.get("Aluguel por m2", "")),
        "cap_rate": parse_br_percent(raw.get("Cap Rate", "")),
        "avg_vacancy": parse_br_percent(raw.get("Vacância Média", "")),
    }


def _first(values: list[str] | None, idx: int = 0) -> str:
    if not values or idx >= len(values):
        return ""
    return _clean_text(values[idx])


def _parse_oscillations(labels: dict[str, list[str]]) -> dict[str, Any]:
    yearly: dict[str, float | None] = {}
    for label, values in labels.items():
        clean_label = _clean_text(label)
        if len(clean_label) == 4 and clean_label.isdigit():
            yearly[clean_label] = parse_br_percent(_first(values))

    latest_year = max(yearly.keys(), default=None)
    return {
        "day": parse_br_percent(_first(labels.get("Dia"))),
        "month": parse_br_percent(_first(labels.get("Mês"))),
        "days_30": parse_br_percent(_first(labels.get("30 dias"))),
        "months_12": parse_br_percent(_first(labels.get("12 meses"))),
        "year_to_date": yearly.get(latest_year) if latest_year else None,
        "yearly": yearly,
    }


def normalize_fii_detail(raw_detail: dict[str, Any]) -> dict[str, Any]:
    labels: dict[str, list[str]] = raw_detail.get("raw_labels", {}) or {}

    return {
        "ticker": _clean_text(raw_detail.get("ticker", "")),
        "detail_url": _clean_text(raw_detail.get("detail_url", "")),
        "collection_status": _clean_text(raw_detail.get("collection_status", "")),
        "identification": {
            "name": _first(labels.get("Nome")),
            "segment": _first(labels.get("Segmento")),
            "mandate": _first(labels.get("Mandato")),
            "management": _first(labels.get("Gestão")),
        },
        "market": {
            "price": parse_br_number(_first(labels.get("Cotação"))),
            "last_quote_date": _first(labels.get("Data últ cot")),
            "low_52w": parse_br_number(_first(labels.get("Min 52 sem"))),
            "high_52w": parse_br_number(_first(labels.get("Max 52 sem"))),
            "avg_volume_2m": parse_br_number(_first(labels.get("Vol $ méd (2m)"))),
            "market_value": parse_br_number(_first(labels.get("Valor de mercado"))),
            "share_count": parse_br_number(_first(labels.get("Nro. Cotas"))),
            "report_date": _first(labels.get("Relatório")),
            "last_quarter_info_date": _first(labels.get("Últ Info Trimestral")),
        },
        "oscillations": _parse_oscillations(labels),
        "indicators": {
            "ffo_yield": parse_br_percent(_first(labels.get("FFO Yield"))),
            "ffo_per_share": parse_br_number(_first(labels.get("FFO/Cota"))),
            "dividend_yield": parse_br_percent(_first(labels.get("Div. Yield"))),
            "dividend_per_share": parse_br_number(_first(labels.get("Dividendo/cota"))),
            "price_to_book": parse_br_number(_first(labels.get("P/VP"))),
            "book_value_per_share": parse_br_number(_first(labels.get("VP/Cota"))),
        },
        "results": {
            "last_12m_revenue": parse_br_number(_first(labels.get("Receita"), 0)),
            "last_3m_revenue": parse_br_number(_first(labels.get("Receita"), 1)),
            "last_12m_asset_sales": parse_br_number(_first(labels.get("Venda de ativos"), 0)),
            "last_3m_asset_sales": parse_br_number(_first(labels.get("Venda de ativos"), 1)),
            "last_12m_ffo": parse_br_number(_first(labels.get("FFO"), 0)),
            "last_3m_ffo": parse_br_number(_first(labels.get("FFO"), 1)),
            "last_12m_distributed_income": parse_br_number(_first(labels.get("Rend. Distribuído"), 0)),
            "last_3m_distributed_income": parse_br_number(_first(labels.get("Rend. Distribuído"), 1)),
        },
        "balance_sheet": {
            "assets": parse_br_number(_first(labels.get("Ativos"))),
            "net_equity": parse_br_number(_first(labels.get("Patrim Líquido"))),
        },
        "properties": {
            "property_count": parse_br_int(_first(labels.get("Qtd imóveis"))),
            "unit_count": parse_br_int(_first(labels.get("Qtd Unidades"))),
            "area_sqm": parse_br_number(_first(labels.get("Área (m2)"))),
            "price_per_sqm": parse_br_number(_first(labels.get("Preço do m2"))),
            "rent_per_sqm": parse_br_number(_first(labels.get("Aluguel/m2"))),
            "cap_rate": parse_br_percent(_first(labels.get("Cap Rate"))),
            "avg_vacancy": parse_br_percent(_first(labels.get("Vacância Média"))),
            "properties_to_equity_percent": parse_br_percent(_first(labels.get("Imóveis/PL do FII"))),
        },
    }
