import os
import unittest
from unittest.mock import patch

from fundamentus_fii_ingestor.config import DEFAULT_MAX_DETAIL_TABS, env_int, resolve_detail_concurrency


class ConfigTests(unittest.TestCase):
    def test_env_int_uses_default_when_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(env_int("BOT_MAX_DETAIL_TABS", 4), 4)

    def test_env_int_handles_invalid_and_non_positive(self) -> None:
        with patch.dict(os.environ, {"BOT_MAX_DETAIL_TABS": "abc"}, clear=True):
            self.assertEqual(env_int("BOT_MAX_DETAIL_TABS", 4), 4)
        with patch.dict(os.environ, {"BOT_MAX_DETAIL_TABS": "0"}, clear=True):
            self.assertEqual(env_int("BOT_MAX_DETAIL_TABS", 4), 4)

    def test_resolve_detail_concurrency_prefers_explicit_value(self) -> None:
        with patch.dict(os.environ, {"BOT_MAX_DETAIL_TABS": "9"}, clear=True):
            self.assertEqual(resolve_detail_concurrency(3), 3)
            self.assertEqual(resolve_detail_concurrency(None), 9)
            self.assertEqual(resolve_detail_concurrency(0), 9)

    def test_default_max_detail_tabs_is_conservative(self) -> None:
        self.assertEqual(DEFAULT_MAX_DETAIL_TABS, 4)


if __name__ == "__main__":
    unittest.main()
