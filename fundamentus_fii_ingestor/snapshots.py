from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def save_snapshot(payload: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_general_snapshot(
    *,
    run_id: str,
    collected_at_utc: str,
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "source": "fundamentus_fii_resultado",
        "run_id": run_id,
        "url": "https://www.fundamentus.com.br/fii_resultado.php",
        "collected_at_utc": collected_at_utc,
        "total": len(items),
        "items": items,
    }


def build_details_snapshot(
    *,
    run_id: str,
    collected_at_utc: str,
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "source": "fundamentus_detalhes_fii",
        "run_id": run_id,
        "url": "https://www.fundamentus.com.br/detalhes.php?papel=<TICKER>",
        "collected_at_utc": collected_at_utc,
        "total": len(items),
        "items": items,
    }
