import unittest
from unittest.mock import Mock, patch

from fundamentus_fii_ingestor import pipeline


class _FakePage:
    async def close(self) -> None:
        return None


class _FakeBrowserFactory:
    def __init__(self, *args, **kwargs):
        self._context = object()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def start(self):
        return self._context

    async def new_page(self):
        return _FakePage()


class PipelineTests(unittest.IsolatedAsyncioTestCase):
    async def test_run_ingestion_collects_details_and_persists(self) -> None:
        rows = [
            {"Papel": "AAZQ11", "detail_url": "https://www.fundamentus.com.br/detalhes.php?papel=AAZQ11"},
            {"Papel": "ABCP11", "detail_url": "https://www.fundamentus.com.br/detalhes.php?papel=ABCP11"},
        ]

        async def fake_extract_fii_table_raw(*, page, timeout_ms, limit, on_row_extracted):
            for idx, row in enumerate(rows):
                if on_row_extracted is not None:
                    await on_row_extracted(row, idx)
            return rows

        async def fake_extract_one_detail(*, context, item, idx, timeout_ms):
            return {
                "ticker": item.get("Papel", ""),
                "detail_url": item.get("detail_url", ""),
                "collection_status": "success",
                "raw_labels": {},
            }

        with (
            patch.object(pipeline, "BrowserFactory", _FakeBrowserFactory),
            patch.object(pipeline, "extract_fii_table_raw", side_effect=fake_extract_fii_table_raw),
            patch.object(pipeline, "extract_one_detail", side_effect=fake_extract_one_detail),
            patch.object(pipeline, "setup_logging", Mock()),
            patch.object(pipeline, "audit_event", Mock()),
            patch.object(pipeline, "save_snapshot", Mock()),
            patch.object(pipeline, "upsert_general_rows", Mock(return_value={"upserted": 2})),
            patch.object(pipeline, "upsert_detail_rows", Mock(return_value={"upserted": 2, "skipped": 0})),
            patch("builtins.print", Mock()),
        ):
            result = await pipeline.run_ingestion(detailed=True, headless=True, limit=2, concurrency=2)

        self.assertEqual(result["total_raw_rows"], 2)
        self.assertEqual(result["details_total"], 2)


if __name__ == "__main__":
    unittest.main()
