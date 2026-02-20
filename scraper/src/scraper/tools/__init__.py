"""コーディングツール / サブスクリプションのスクレイパー群。

月額固定料金が多いため、変更検知ロジックでページから価格を取得し、
変化があれば logging.warning で通知する。
"""

from scraper.tools.github_copilot import scrape as scrape_github_copilot
from scraper.tools.cursor import scrape as scrape_cursor
from scraper.tools.windsurf import scrape as scrape_windsurf
from scraper.tools.claude_code import scrape as scrape_claude_code
from scraper.tools.jetbrains import scrape as scrape_jetbrains
from scraper.tools.openai_codex import scrape as scrape_openai_codex
from scraper.tools.google_one import scrape as scrape_google_one
from scraper.tools.antigravity import scrape as scrape_antigravity

__all__ = [
    "scrape_github_copilot",
    "scrape_cursor",
    "scrape_windsurf",
    "scrape_claude_code",
    "scrape_jetbrains",
    "scrape_openai_codex",
    "scrape_google_one",
    "scrape_antigravity",
]
