from __future__ import annotations

import logging
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_GENERAL_SNAPSHOT_PATH = PROJECT_ROOT / "data" / "fii_general_snapshot.json"
DEFAULT_DETAILS_SNAPSHOT_PATH = PROJECT_ROOT / "data" / "fii_details_snapshot.json"
DEFAULT_LOG_DIR = PROJECT_ROOT / "data" / "logs"

DEFAULT_TIMEOUT_MS = 30_000
DEFAULT_MAX_DETAIL_TABS = 4

logger = logging.getLogger(__name__)


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError:
        logger.warning("Valor invalido em %s=%r. Usando default=%s.", name, value, default)
        return default
    return parsed if parsed > 0 else default


def resolve_detail_concurrency(concurrency: int | None) -> int:
    if concurrency is not None and concurrency > 0:
        return concurrency
    return env_int("BOT_MAX_DETAIL_TABS", DEFAULT_MAX_DETAIL_TABS)
