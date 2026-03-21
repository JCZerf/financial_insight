import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

try:
    from bot.fundamentus_details_extractor import extract_fii_details_in_parallel
    from bot.fundamentus_extractor import extract_fii_table_raw
    from bot.logging_utils import audit_event, setup_logging
    from bot.normalizers import normalize_fii_detail, normalize_fii_row
except ModuleNotFoundError:
    from fundamentus_details_extractor import extract_fii_details_in_parallel
    from fundamentus_extractor import extract_fii_table_raw
    from logging_utils import audit_event, setup_logging
    from normalizers import normalize_fii_detail, normalize_fii_row

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GENERAL_SNAPSHOT_PATH = PROJECT_ROOT / "data" / "fii_general_snapshot.json"
DEFAULT_DETAILS_SNAPSHOT_PATH = PROJECT_ROOT / "data" / "fii_details_snapshot.json"
DEFAULT_LOG_DIR = PROJECT_ROOT / "data" / "logs"
logger = logging.getLogger(__name__)


def save_snapshot(payload: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


async def main() -> None:
    await run_ingestion()


async def run_ingestion(
    *,
    detailed: bool = True,
    details_only: bool = False,
    headless: bool = True,
    concurrency: int = 8,
    limit: int | None = None,
) -> dict[str, Any]:
    setup_logging(log_dir=DEFAULT_LOG_DIR, level=logging.INFO)
    run_id = str(uuid4())
    logger.info("Iniciando pipeline de ingestao de FIIs.")
    audit_event(
        "pipeline_started",
        {
            "run_id": run_id,
            "source": "fundamentus_fii_resultado",
            "detailed": detailed,
            "details_only": details_only,
            "headless": headless,
            "concurrency": concurrency,
            "limit": limit,
        },
    )

    raw_rows = await extract_fii_table_raw(headless=headless)
    if limit is not None and limit > 0:
        raw_rows = raw_rows[:limit]
        logger.info("Limite aplicado. Linhas consideradas: %s", len(raw_rows))
        audit_event("limit_applied", {"run_id": run_id, "limit": limit, "rows_used": len(raw_rows)})

    logger.info("Extracao bruta concluida. Total de linhas: %s", len(raw_rows))
    audit_event("raw_rows_collected", {"run_id": run_id, "total_rows": len(raw_rows)})

    collected_at = datetime.now(timezone.utc).isoformat()
    normalized_general_rows: list[dict[str, Any]] = []
    normalized_detail_rows: list[dict[str, Any]] = []

    should_collect_general = not details_only
    should_collect_details = detailed or details_only

    if should_collect_general:
        normalized_general_rows = [normalize_fii_row(row) for row in raw_rows]
        logger.info(
            "Normalizacao de dados gerais concluida. Total de linhas: %s",
            len(normalized_general_rows),
        )

        for idx, row in enumerate(normalized_general_rows):
            audit_event(
                "general_row_normalized",
                {
                    "run_id": run_id,
                    "row_index": idx,
                    "papel": row.get("papel", ""),
                    "row": row,
                },
            )

        general_snapshot = {
            "source": "fundamentus_fii_resultado",
            "run_id": run_id,
            "url": "https://www.fundamentus.com.br/fii_resultado.php",
            "collected_at_utc": collected_at,
            "total": len(normalized_general_rows),
            "items": normalized_general_rows,
        }
        save_snapshot(general_snapshot, DEFAULT_GENERAL_SNAPSHOT_PATH)
        logger.info("Snapshot geral salvo em %s", DEFAULT_GENERAL_SNAPSHOT_PATH)
        audit_event(
            "general_snapshot_saved",
            {
                "run_id": run_id,
                "path": str(DEFAULT_GENERAL_SNAPSHOT_PATH),
                "total": len(normalized_general_rows),
                "collected_at_utc": collected_at,
            },
        )

    if should_collect_details:
        raw_detail_rows = await extract_fii_details_in_parallel(
            raw_rows,
            headless=headless,
            concurrency=concurrency,
        )
        normalized_detail_rows = [normalize_fii_detail(item) for item in raw_detail_rows]
        logger.info(
            "Normalizacao de dados detalhados concluida. Total de linhas: %s",
            len(normalized_detail_rows),
        )

        for idx, row in enumerate(normalized_detail_rows):
            audit_event(
                "detail_row_normalized",
                {
                    "run_id": run_id,
                    "row_index": idx,
                    "papel": row.get("papel", ""),
                    "status_coleta": row.get("status_coleta", ""),
                },
            )

        details_snapshot = {
            "source": "fundamentus_detalhes_fii",
            "run_id": run_id,
            "url": "https://www.fundamentus.com.br/detalhes.php?papel=<TICKER>",
            "collected_at_utc": collected_at,
            "total": len(normalized_detail_rows),
            "items": normalized_detail_rows,
        }
        save_snapshot(details_snapshot, DEFAULT_DETAILS_SNAPSHOT_PATH)
        logger.info("Snapshot de detalhes salvo em %s", DEFAULT_DETAILS_SNAPSHOT_PATH)
        audit_event(
            "details_snapshot_saved",
            {
                "run_id": run_id,
                "path": str(DEFAULT_DETAILS_SNAPSHOT_PATH),
                "total": len(normalized_detail_rows),
                "collected_at_utc": collected_at,
            },
        )

    logger.info("Pipeline finalizada com sucesso.")
    audit_event("pipeline_finished", {"run_id": run_id, "status": "success"})

    print(f"Run ID: {run_id}")
    print(f"Total de linhas extraidas: {len(raw_rows)}")
    if should_collect_general:
        print(f"Snapshot geral salvo em: {DEFAULT_GENERAL_SNAPSHOT_PATH}")
    if should_collect_details:
        print(f"Snapshot detalhado salvo em: {DEFAULT_DETAILS_SNAPSHOT_PATH}")

    if should_collect_general and normalized_general_rows:
        print("Primeiro registro geral normalizado:")
        print(json.dumps(normalized_general_rows[0], ensure_ascii=False, indent=2))
    if should_collect_details and normalized_detail_rows:
        print("Primeiro registro detalhado normalizado:")
        print(json.dumps(normalized_detail_rows[0], ensure_ascii=False, indent=2))

    return {
        "run_id": run_id,
        "total_raw_rows": len(raw_rows),
        "general_total": len(normalized_general_rows),
        "details_total": len(normalized_detail_rows),
        "general_snapshot_path": str(DEFAULT_GENERAL_SNAPSHOT_PATH) if should_collect_general else None,
        "details_snapshot_path": str(DEFAULT_DETAILS_SNAPSHOT_PATH) if should_collect_details else None,
    }


if __name__ == "__main__":
    asyncio.run(main())
