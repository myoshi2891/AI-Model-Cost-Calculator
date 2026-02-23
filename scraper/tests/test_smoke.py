import unittest
from unittest.mock import MagicMock, patch
import logging

from scraper.main import main
from scraper.exchange import fetch_jpy_rate
from scraper.providers import (
    scrape_anthropic, scrape_openai, scrape_google, scrape_aws, scrape_deepseek, scrape_xai
)
from scraper.tools import (
    scrape_github_copilot, scrape_cursor, scrape_windsurf, scrape_claude_code,
    scrape_jetbrains, scrape_openai_codex, scrape_google_one, scrape_antigravity
)

class TestSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """
        Disable all logging for the test class by suppressing log records at CRITICAL level and below.
        """
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Restore global logging to NOTSET, re-enabling all logging after tests complete.
        """
        logging.disable(logging.NOTSET)

    def test_fetch_jpy_rate(self):
        """Minimal smoke test for exchange rate fetcher (mocked)."""
        with patch("scraper.exchange.httpx.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {"rates": {"JPY": 150.0}, "date": "2024-01-01"}
            mock_resp.raise_for_status.return_value = None
            mock_get.return_value = mock_resp

            rate, date = fetch_jpy_rate()
            self.assertEqual(rate, 150.0)
            self.assertEqual(date, "2024-01-01")

    def test_main(self):
        """
        Smoke test for the CLI entry point that verifies main([]) triggers a full scrape and writes output when external calls are mocked.
        
        Asserts that main([]) returns 0 and that _scrape_all and _write_output are each called exactly once while fetch_jpy_rate and _load_existing are patched.
        """
        with patch("scraper.main.fetch_jpy_rate") as mock_rate, \
             patch("scraper.main._scrape_all") as mock_scrape, \
             patch("scraper.main._write_output") as mock_write, \
             patch("scraper.main._load_existing") as mock_load:

            mock_rate.return_value = (150.0, "2024-01-01")
            mock_scrape.return_value = ([], [])
            mock_load.return_value = None

            # Test with no arguments (full scrape path)
            ret = main([])
            self.assertEqual(ret, 0)
            mock_scrape.assert_called_once()
            mock_write.assert_called_once()

    def test_providers(self):
        """Smoke test for all provider scrapers (mocked)."""
        # Providers using get_page_text
        providers_browser = [
            (scrape_anthropic, "scraper.providers.anthropic.get_page_text"),
            (scrape_openai, "scraper.providers.openai.get_page_text"),
            (scrape_google, "scraper.providers.google.get_page_text"),
            (scrape_deepseek, "scraper.providers.deepseek.get_page_text"),
            (scrape_xai, "scraper.providers.xai.get_page_text"),
        ]
        for func, target in providers_browser:
            with self.subTest(provider=func.__name__):
                with patch(target) as mock_get:
                    mock_get.return_value = "<html>Mock</html>"
                    res = func()
                    self.assertIsInstance(res, list)

        # AWS uses httpx
        with self.subTest(provider="scraper.providers.aws"):
            with patch("scraper.providers.aws.httpx.get") as mock_get:
                mock_resp = MagicMock()
                mock_resp.json.return_value = {}
                mock_resp.raise_for_status.return_value = None
                mock_get.return_value = mock_resp
                res = scrape_aws()
                self.assertIsInstance(res, list)

    def test_tools(self):
        """Smoke test for all tool scrapers (mocked)."""
        tools = [
            (scrape_github_copilot, "scraper.tools.github_copilot.get_page_text"),
            (scrape_cursor, "scraper.tools.cursor.get_page_text"),
            (scrape_windsurf, "scraper.tools.windsurf.get_page_text"),
            (scrape_claude_code, "scraper.tools.claude_code.get_page_text"),
            (scrape_jetbrains, "scraper.tools.jetbrains.get_page_text"),
            (scrape_openai_codex, "scraper.tools.openai_codex.get_page_text"),
            (scrape_google_one, "scraper.tools.google_one.get_page_text"),
            (scrape_antigravity, "scraper.tools.antigravity.get_page_text"),
        ]
        for func, target in tools:
            with self.subTest(tool=func.__name__):
                with patch(target) as mock_get:
                    mock_get.return_value = "<html>Mock</html>"
                    res = func()
                    self.assertIsInstance(res, list)

if __name__ == "__main__":
    unittest.main()
