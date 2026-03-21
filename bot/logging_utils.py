import json
import logging
from pathlib import Path
from typing import Any


def setup_logging(log_dir: Path, level: int = logging.INFO) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)

    app_log_file = log_dir / "ingestor.log"
    audit_log_file = log_dir / "extraction_audit.ndjson"

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Evita handlers duplicados quando o script é executado múltiplas vezes.
    if not root_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        root_logger.addHandler(console_handler)

        file_handler = logging.FileHandler(app_log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        root_logger.addHandler(file_handler)

    audit_logger = logging.getLogger("bot.audit")
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False

    if not audit_logger.handlers:
        audit_handler = logging.FileHandler(audit_log_file, encoding="utf-8")
        audit_handler.setLevel(logging.INFO)
        audit_handler.setFormatter(logging.Formatter("%(message)s"))
        audit_logger.addHandler(audit_handler)


def audit_event(event: str, payload: dict[str, Any]) -> None:
    audit_logger = logging.getLogger("bot.audit")
    body = {"event": event, **payload}
    audit_logger.info(json.dumps(body, ensure_ascii=False))
