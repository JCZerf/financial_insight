from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from uuid import uuid4

try:
    from fundamentus_fii_ingestor.browser_factory import BrowserFactory
    from fundamentus_fii_ingestor.config import (
        DEFAULT_DETAILS_SNAPSHOT_PATH,
        DEFAULT_GENERAL_SNAPSHOT_PATH,
        DEFAULT_LOG_DIR,
        DEFAULT_TIMEOUT_MS,
        resolve_detail_concurrency,
    )
    from fundamentus_fii_ingestor.db_persistence import upsert_detail_rows, upsert_general_rows
    from fundamentus_fii_ingestor.fundamentus_details_extractor import extract_one_detail
    from fundamentus_fii_ingestor.fundamentus_extractor import extract_fii_table_raw
    from fundamentus_fii_ingestor.logging_utils import audit_event, setup_logging
    from fundamentus_fii_ingestor.normalizers import normalize_fii_detail, normalize_fii_row
    from fundamentus_fii_ingestor.snapshots import build_details_snapshot, build_general_snapshot, save_snapshot
except ModuleNotFoundError:
    from browser_factory import BrowserFactory
    from config import (
        DEFAULT_DETAILS_SNAPSHOT_PATH,
        DEFAULT_GENERAL_SNAPSHOT_PATH,
        DEFAULT_LOG_DIR,
        DEFAULT_TIMEOUT_MS,
        resolve_detail_concurrency,
    )
    from db_persistence import upsert_detail_rows, upsert_general_rows
    from fundamentus_details_extractor import extract_one_detail
    from fundamentus_extractor import extract_fii_table_raw
    from logging_utils import audit_event, setup_logging
    from normalizers import normalize_fii_detail, normalize_fii_row
    from snapshots import build_details_snapshot, build_general_snapshot, save_snapshot

logger = logging.getLogger(__name__)


async def run_ingestion(
    *,
    detailed: bool = True,
    details_only: bool = False,
    headless: bool = True,
    concurrency: int | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    setup_logging(log_dir=DEFAULT_LOG_DIR, level=logging.INFO)
    detail_concurrency = resolve_detail_concurrency(concurrency)
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
            "concurrency": detail_concurrency,
            "limit": limit,
        },
    )

    should_collect_general = not details_only
    should_collect_details = detailed or details_only
    detail_tasks: list[asyncio.Task[dict[str, Any]]] = []
    semaphore = asyncio.Semaphore(detail_concurrency)
    raw_detail_rows: list[dict[str, Any]] = []
    extraction_partial_seconds = 0.0
    extraction_complete_seconds = 0.0
    details_extraction_seconds = 0.0

    async with BrowserFactory(headless=headless, timeout_ms=DEFAULT_TIMEOUT_MS) as browser_factory:
        context = await browser_factory.start()
        general_page = await browser_factory.new_page()

        async def on_row_extracted(row: dict[str, str], idx: int) -> None:
            if not should_collect_details:
                return

            async def run_detail_task() -> dict[str, Any]:
                async with semaphore:
                    return await extract_one_detail(
                        context=context,
                        item=row,
                        idx=idx,
                        timeout_ms=DEFAULT_TIMEOUT_MS,
                    )

            detail_tasks.append(asyncio.create_task(run_detail_task()))

        extraction_total_started = perf_counter()
        partial_extraction_started = perf_counter()
        raw_rows = await extract_fii_table_raw(
            timeout_ms=DEFAULT_TIMEOUT_MS,
            page=general_page,
            limit=limit,
            on_row_extracted=on_row_extracted if should_collect_details else None,
        )
        extraction_partial_seconds = perf_counter() - partial_extraction_started
        await general_page.close()

        if should_collect_details:
            logger.info(
                "Aguardando finalizacao das tarefas de detalhe. Total agendado: %s | max_abas=%s",
                len(detail_tasks),
                detail_concurrency,
            )
            details_extraction_started = perf_counter()
            raw_detail_rows = await asyncio.gather(*detail_tasks) if detail_tasks else []
            details_extraction_seconds = perf_counter() - details_extraction_started

        extraction_complete_seconds = perf_counter() - extraction_total_started

    logger.info("Extracao bruta concluida. Total de linhas: %s", len(raw_rows))
    logger.info(
        "Tempo de extracao parcial (dados gerais): %.2fs",
        extraction_partial_seconds,
    )
    logger.info("TEMPO TOTAL DE EXTRACAO (geral + detalhes): %.2fs", extraction_complete_seconds)
    if should_collect_details:
        logger.info("Tempo adicional de extracao de detalhes: %.2fs", details_extraction_seconds)
    if limit is not None and limit > 0:
        audit_event("limit_applied", {"run_id": run_id, "limit": limit, "rows_used": len(raw_rows)})
    audit_event(
        "raw_rows_collected",
        {
            "run_id": run_id,
            "total_rows": len(raw_rows),
            "extraction_partial_seconds": extraction_partial_seconds,
            "extraction_complete_seconds": extraction_complete_seconds,
            "details_extraction_seconds": details_extraction_seconds,
        },
    )

    collected_at = datetime.now(timezone.utc).isoformat()
    normalized_general_rows: list[dict[str, Any]] = []
    normalized_detail_rows: list[dict[str, Any]] = []

    if should_collect_general:
        normalized_general_rows = [normalize_fii_row(row) for row in raw_rows]
        logger.info("Normalizacao de dados gerais concluida. Total de linhas: %s", len(normalized_general_rows))

        for idx, row in enumerate(normalized_general_rows):
            audit_event(
                "general_row_normalized",
                {
                    "run_id": run_id,
                    "row_index": idx,
                    "ticker": row.get("ticker", ""),
                    "row": row,
                },
            )

        general_snapshot = build_general_snapshot(
            run_id=run_id,
            collected_at_utc=collected_at,
            items=normalized_general_rows,
        )
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

        general_db_started = perf_counter()
        db_general_result = upsert_general_rows(
            run_id=run_id,
            source=general_snapshot["source"],
            url=general_snapshot["url"],
            collected_at_utc=collected_at,
            rows=normalized_general_rows,
        )
        general_db_seconds = perf_counter() - general_db_started
        logger.info(
            "Persistencia geral no banco concluida em %.2fs (post=%s, update=%s, total=%s)",
            general_db_seconds,
            db_general_result.get("posted", 0),
            db_general_result.get("updated", 0),
            db_general_result.get("upserted", 0),
        )
        audit_event(
            "general_db_upsert_finished",
            {"run_id": run_id, "duration_seconds": general_db_seconds, **db_general_result},
        )

    if should_collect_details:
        normalized_detail_rows = [normalize_fii_detail(item) for item in raw_detail_rows]
        logger.info("Normalizacao de dados detalhados concluida. Total de linhas: %s", len(normalized_detail_rows))

        for idx, row in enumerate(normalized_detail_rows):
            audit_event(
                "detail_row_normalized",
                {
                    "run_id": run_id,
                    "row_index": idx,
                    "ticker": row.get("ticker", ""),
                    "collection_status": row.get("collection_status", ""),
                },
            )

        details_snapshot = build_details_snapshot(
            run_id=run_id,
            collected_at_utc=collected_at,
            items=normalized_detail_rows,
        )
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

        details_db_started = perf_counter()
        db_detail_result = upsert_detail_rows(
            run_id=run_id,
            source=details_snapshot["source"],
            url=details_snapshot["url"],
            collected_at_utc=collected_at,
            rows=normalized_detail_rows,
        )
        details_db_seconds = perf_counter() - details_db_started
        logger.info(
            "Persistencia de detalhes no banco concluida em %.2fs (post=%s, update=%s, total=%s, skipped=%s)",
            details_db_seconds,
            db_detail_result.get("posted", 0),
            db_detail_result.get("updated", 0),
            db_detail_result.get("upserted", 0),
            db_detail_result.get("skipped", 0),
        )
        audit_event(
            "details_db_upsert_finished",
            {"run_id": run_id, "duration_seconds": details_db_seconds, **db_detail_result},
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
        "extraction_partial_seconds": extraction_partial_seconds,
        "extraction_complete_seconds": extraction_complete_seconds,
        "details_extraction_seconds": details_extraction_seconds,
    }
