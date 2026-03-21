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
        "papel": _clean_text(raw.get("Papel", "")),
        "segmento": _clean_text(raw.get("Segmento", "")),
        "cotacao": parse_br_number(raw.get("Cotação", "")),
        "ffo_yield": parse_br_percent(raw.get("FFO Yield", "")),
        "dividend_yield": parse_br_percent(raw.get("Dividend Yield", "")),
        "p_vp": parse_br_number(raw.get("P/VP", "")),
        "valor_mercado": parse_br_number(raw.get("Valor de Mercado", "")),
        "liquidez": parse_br_number(raw.get("Liquidez", "")),
        "qtd_imoveis": parse_br_int(raw.get("Qtd de imóveis", "")),
        "preco_m2": parse_br_number(raw.get("Preço do m2", "")),
        "aluguel_m2": parse_br_number(raw.get("Aluguel por m2", "")),
        "cap_rate": parse_br_percent(raw.get("Cap Rate", "")),
        "vacancia_media": parse_br_percent(raw.get("Vacância Média", "")),
    }


def _first(values: list[str] | None, idx: int = 0) -> str:
    if not values or idx >= len(values):
        return ""
    return _clean_text(values[idx])


def normalize_fii_detail(raw_detail: dict[str, Any]) -> dict[str, Any]:
    labels: dict[str, list[str]] = raw_detail.get("raw_labels", {}) or {}

    return {
        "papel": _clean_text(raw_detail.get("papel", "")),
        "detalhe_url": _clean_text(raw_detail.get("detalhe_url", "")),
        "status_coleta": _clean_text(raw_detail.get("status_coleta", "")),
        "identificacao": {
            "nome": _first(labels.get("Nome")),
            "segmento": _first(labels.get("Segmento")),
            "mandato": _first(labels.get("Mandato")),
            "gestao": _first(labels.get("Gestão")),
        },
        "mercado": {
            "cotacao": parse_br_number(_first(labels.get("Cotação"))),
            "data_ult_cot": _first(labels.get("Data últ cot")),
            "min_52_sem": parse_br_number(_first(labels.get("Min 52 sem"))),
            "max_52_sem": parse_br_number(_first(labels.get("Max 52 sem"))),
            "vol_medio_2m": parse_br_number(_first(labels.get("Vol $ méd (2m)"))),
            "valor_mercado": parse_br_number(_first(labels.get("Valor de mercado"))),
            "numero_cotas": parse_br_number(_first(labels.get("Nro. Cotas"))),
            "data_relatorio": _first(labels.get("Relatório")),
            "ult_info_trimestral": _first(labels.get("Últ Info Trimestral")),
        },
        "indicadores": {
            "ffo_yield": parse_br_percent(_first(labels.get("FFO Yield"))),
            "ffo_cota": parse_br_number(_first(labels.get("FFO/Cota"))),
            "dividend_yield": parse_br_percent(_first(labels.get("Div. Yield"))),
            "dividendo_cota": parse_br_number(_first(labels.get("Dividendo/cota"))),
            "p_vp": parse_br_number(_first(labels.get("P/VP"))),
            "vp_cota": parse_br_number(_first(labels.get("VP/Cota"))),
        },
        "resultado": {
            "ult_12m_receita": parse_br_number(_first(labels.get("Receita"), 0)),
            "ult_3m_receita": parse_br_number(_first(labels.get("Receita"), 1)),
            "ult_12m_venda_ativos": parse_br_number(_first(labels.get("Venda de ativos"), 0)),
            "ult_3m_venda_ativos": parse_br_number(_first(labels.get("Venda de ativos"), 1)),
            "ult_12m_ffo": parse_br_number(_first(labels.get("FFO"), 0)),
            "ult_3m_ffo": parse_br_number(_first(labels.get("FFO"), 1)),
            "ult_12m_rend_distribuido": parse_br_number(_first(labels.get("Rend. Distribuído"), 0)),
            "ult_3m_rend_distribuido": parse_br_number(_first(labels.get("Rend. Distribuído"), 1)),
        },
        "balanco": {
            "ativos": parse_br_number(_first(labels.get("Ativos"))),
            "patrimonio_liquido": parse_br_number(_first(labels.get("Patrim Líquido"))),
        },
        "imoveis": {
            "qtd_imoveis": parse_br_int(_first(labels.get("Qtd imóveis"))),
            "qtd_unidades": parse_br_int(_first(labels.get("Qtd Unidades"))),
            "area_m2": parse_br_number(_first(labels.get("Área (m2)"))),
            "preco_m2": parse_br_number(_first(labels.get("Preço do m2"))),
            "aluguel_m2": parse_br_number(_first(labels.get("Aluguel/m2"))),
            "cap_rate": parse_br_percent(_first(labels.get("Cap Rate"))),
            "vacancia_media": parse_br_percent(_first(labels.get("Vacância Média"))),
            "imoveis_pl_percent": parse_br_percent(_first(labels.get("Imóveis/PL do FII"))),
        },
    }
