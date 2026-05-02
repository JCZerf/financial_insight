from __future__ import annotations

import asyncio
from threading import Lock
from time import perf_counter
from typing import Any

from fundamentus_fii_ingestor.pipeline import run_ingestion

_ingestion_lock = Lock()


class IngestionAlreadyRunningError(RuntimeError):
    pass


def run_manual_ingestion(*, detailed: bool, limit: int | None = None) -> dict[str, Any]:
    if not _ingestion_lock.acquire(blocking=False):
        raise IngestionAlreadyRunningError("An ingestion is already running.")

    started = perf_counter()
    try:
        result = asyncio.run(
            run_ingestion(
                detailed=detailed,
                details_only=False,
                headless=True,
                limit=limit,
            )
        )
    finally:
        _ingestion_lock.release()

    return {
        "mode": "detailed" if detailed else "basic",
        "duration_seconds": round(perf_counter() - started, 2),
        **result,
    }
