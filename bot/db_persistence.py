import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


GENERAL_COLUMNS = [
    "run_id",
    "source",
    "url",
    "collected_at_utc",
    "papel",
    "segmento",
    "cotacao",
    "ffo_yield",
    "dividend_yield",
    "p_vp",
    "valor_mercado",
    "liquidez",
    "qtd_imoveis",
    "preco_m2",
    "aluguel_m2",
    "cap_rate",
    "vacancia_media",
    "created_at",
    "updated_at",
]

DETAIL_COLUMNS = [
    "fund_id",
    "run_id",
    "source",
    "url",
    "detalhe_url",
    "collected_at_utc",
    "status_coleta",
    "identificacao_nome",
    "identificacao_segmento",
    "identificacao_mandato",
    "identificacao_gestao",
    "mercado_cotacao",
    "mercado_data_ult_cot",
    "mercado_min_52_sem",
    "mercado_max_52_sem",
    "mercado_vol_medio_2m",
    "mercado_valor_mercado",
    "mercado_numero_cotas",
    "mercado_data_relatorio",
    "mercado_ult_info_trimestral",
    "indicadores_ffo_yield",
    "indicadores_ffo_cota",
    "indicadores_dividend_yield",
    "indicadores_dividendo_cota",
    "indicadores_p_vp",
    "indicadores_vp_cota",
    "resultado_ult_12m_receita",
    "resultado_ult_3m_receita",
    "resultado_ult_12m_venda_ativos",
    "resultado_ult_3m_venda_ativos",
    "resultado_ult_12m_ffo",
    "resultado_ult_3m_ffo",
    "resultado_ult_12m_rend_distribuido",
    "resultado_ult_3m_rend_distribuido",
    "balanco_ativos",
    "balanco_patrimonio_liquido",
    "imoveis_qtd_imoveis",
    "imoveis_qtd_unidades",
    "imoveis_area_m2",
    "imoveis_preco_m2",
    "imoveis_aluguel_m2",
    "imoveis_cap_rate",
    "imoveis_vacancia_media",
    "imoveis_imoveis_pl_percent",
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
        return {"upserted": 0}

    now_dt = datetime.now(timezone.utc)
    values = [
        (
            run_id,
            source,
            url,
            _to_dt(collected_at_utc),
            row.get("papel"),
            row.get("segmento"),
            row.get("cotacao"),
            row.get("ffo_yield"),
            row.get("dividend_yield"),
            row.get("p_vp"),
            row.get("valor_mercado"),
            row.get("liquidez"),
            row.get("qtd_imoveis"),
            row.get("preco_m2"),
            row.get("aluguel_m2"),
            row.get("cap_rate"),
            row.get("vacancia_media"),
            now_dt,
            now_dt,
        )
        for row in rows
    ]

    insert_sql = f"""
        INSERT INTO real_estate_fund ({", ".join(GENERAL_COLUMNS)})
        VALUES %s
        ON CONFLICT (papel) DO UPDATE SET
            run_id = EXCLUDED.run_id,
            source = EXCLUDED.source,
            url = EXCLUDED.url,
            collected_at_utc = EXCLUDED.collected_at_utc,
            segmento = EXCLUDED.segmento,
            cotacao = EXCLUDED.cotacao,
            ffo_yield = EXCLUDED.ffo_yield,
            dividend_yield = EXCLUDED.dividend_yield,
            p_vp = EXCLUDED.p_vp,
            valor_mercado = EXCLUDED.valor_mercado,
            liquidez = EXCLUDED.liquidez,
            qtd_imoveis = EXCLUDED.qtd_imoveis,
            preco_m2 = EXCLUDED.preco_m2,
            aluguel_m2 = EXCLUDED.aluguel_m2,
            cap_rate = EXCLUDED.cap_rate,
            vacancia_media = EXCLUDED.vacancia_media,
            updated_at = NOW()
    """

    with _conn() as conn:
        with conn.cursor() as cur:
            execute_values(cur, insert_sql, values, page_size=500)
        conn.commit()

    return {"upserted": len(rows)}


def _detail_tuple(
    *,
    fund_id: int,
    run_id: str,
    source: str,
    url: str,
    collected_at_utc: str,
    row: dict[str, Any],
) -> tuple[Any, ...]:
    identificacao = row.get("identificacao", {}) or {}
    mercado = row.get("mercado", {}) or {}
    indicadores = row.get("indicadores", {}) or {}
    resultado = row.get("resultado", {}) or {}
    balanco = row.get("balanco", {}) or {}
    imoveis = row.get("imoveis", {}) or {}

    now_dt = datetime.now(timezone.utc)
    return (
        fund_id,
        run_id,
        source,
        url,
        row.get("detalhe_url"),
        _to_dt(collected_at_utc),
        row.get("status_coleta"),
        identificacao.get("nome"),
        identificacao.get("segmento"),
        identificacao.get("mandato"),
        identificacao.get("gestao"),
        mercado.get("cotacao"),
        mercado.get("data_ult_cot"),
        mercado.get("min_52_sem"),
        mercado.get("max_52_sem"),
        mercado.get("vol_medio_2m"),
        mercado.get("valor_mercado"),
        mercado.get("numero_cotas"),
        mercado.get("data_relatorio"),
        mercado.get("ult_info_trimestral"),
        indicadores.get("ffo_yield"),
        indicadores.get("ffo_cota"),
        indicadores.get("dividend_yield"),
        indicadores.get("dividendo_cota"),
        indicadores.get("p_vp"),
        indicadores.get("vp_cota"),
        resultado.get("ult_12m_receita"),
        resultado.get("ult_3m_receita"),
        resultado.get("ult_12m_venda_ativos"),
        resultado.get("ult_3m_venda_ativos"),
        resultado.get("ult_12m_ffo"),
        resultado.get("ult_3m_ffo"),
        resultado.get("ult_12m_rend_distribuido"),
        resultado.get("ult_3m_rend_distribuido"),
        balanco.get("ativos"),
        balanco.get("patrimonio_liquido"),
        imoveis.get("qtd_imoveis"),
        imoveis.get("qtd_unidades"),
        imoveis.get("area_m2"),
        imoveis.get("preco_m2"),
        imoveis.get("aluguel_m2"),
        imoveis.get("cap_rate"),
        imoveis.get("vacancia_media"),
        imoveis.get("imoveis_pl_percent"),
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
        return {"upserted": 0, "skipped": 0}

    papeis = [row.get("papel") for row in rows if row.get("papel")]
    if not papeis:
        return {"upserted": 0, "skipped": len(rows)}

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, papel FROM real_estate_fund WHERE papel = ANY(%s)",
                (papeis,),
            )
            mapping = {papel: fund_id for fund_id, papel in cur.fetchall()}

            values: list[tuple[Any, ...]] = []
            skipped = 0
            for row in rows:
                papel = row.get("papel")
                fund_id = mapping.get(papel)
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

            if values:
                insert_sql = f"""
                    INSERT INTO real_estate_fund_detail ({", ".join(DETAIL_COLUMNS)})
                    VALUES %s
                    ON CONFLICT (fund_id) DO UPDATE SET
                        run_id = EXCLUDED.run_id,
                        source = EXCLUDED.source,
                        url = EXCLUDED.url,
                        detalhe_url = EXCLUDED.detalhe_url,
                        collected_at_utc = EXCLUDED.collected_at_utc,
                        status_coleta = EXCLUDED.status_coleta,
                        identificacao_nome = EXCLUDED.identificacao_nome,
                        identificacao_segmento = EXCLUDED.identificacao_segmento,
                        identificacao_mandato = EXCLUDED.identificacao_mandato,
                        identificacao_gestao = EXCLUDED.identificacao_gestao,
                        mercado_cotacao = EXCLUDED.mercado_cotacao,
                        mercado_data_ult_cot = EXCLUDED.mercado_data_ult_cot,
                        mercado_min_52_sem = EXCLUDED.mercado_min_52_sem,
                        mercado_max_52_sem = EXCLUDED.mercado_max_52_sem,
                        mercado_vol_medio_2m = EXCLUDED.mercado_vol_medio_2m,
                        mercado_valor_mercado = EXCLUDED.mercado_valor_mercado,
                        mercado_numero_cotas = EXCLUDED.mercado_numero_cotas,
                        mercado_data_relatorio = EXCLUDED.mercado_data_relatorio,
                        mercado_ult_info_trimestral = EXCLUDED.mercado_ult_info_trimestral,
                        indicadores_ffo_yield = EXCLUDED.indicadores_ffo_yield,
                        indicadores_ffo_cota = EXCLUDED.indicadores_ffo_cota,
                        indicadores_dividend_yield = EXCLUDED.indicadores_dividend_yield,
                        indicadores_dividendo_cota = EXCLUDED.indicadores_dividendo_cota,
                        indicadores_p_vp = EXCLUDED.indicadores_p_vp,
                        indicadores_vp_cota = EXCLUDED.indicadores_vp_cota,
                        resultado_ult_12m_receita = EXCLUDED.resultado_ult_12m_receita,
                        resultado_ult_3m_receita = EXCLUDED.resultado_ult_3m_receita,
                        resultado_ult_12m_venda_ativos = EXCLUDED.resultado_ult_12m_venda_ativos,
                        resultado_ult_3m_venda_ativos = EXCLUDED.resultado_ult_3m_venda_ativos,
                        resultado_ult_12m_ffo = EXCLUDED.resultado_ult_12m_ffo,
                        resultado_ult_3m_ffo = EXCLUDED.resultado_ult_3m_ffo,
                        resultado_ult_12m_rend_distribuido = EXCLUDED.resultado_ult_12m_rend_distribuido,
                        resultado_ult_3m_rend_distribuido = EXCLUDED.resultado_ult_3m_rend_distribuido,
                        balanco_ativos = EXCLUDED.balanco_ativos,
                        balanco_patrimonio_liquido = EXCLUDED.balanco_patrimonio_liquido,
                        imoveis_qtd_imoveis = EXCLUDED.imoveis_qtd_imoveis,
                        imoveis_qtd_unidades = EXCLUDED.imoveis_qtd_unidades,
                        imoveis_area_m2 = EXCLUDED.imoveis_area_m2,
                        imoveis_preco_m2 = EXCLUDED.imoveis_preco_m2,
                        imoveis_aluguel_m2 = EXCLUDED.imoveis_aluguel_m2,
                        imoveis_cap_rate = EXCLUDED.imoveis_cap_rate,
                        imoveis_vacancia_media = EXCLUDED.imoveis_vacancia_media,
                        imoveis_imoveis_pl_percent = EXCLUDED.imoveis_imoveis_pl_percent,
                        updated_at = NOW()
                """
                execute_values(cur, insert_sql, values, page_size=500)
            else:
                skipped = len(rows)

        conn.commit()

    return {"upserted": len(values), "skipped": skipped}
