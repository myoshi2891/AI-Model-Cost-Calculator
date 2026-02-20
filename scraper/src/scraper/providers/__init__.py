"""API プロバイダーのスクレイパー群。

各モジュールは scrape() 関数を公開し、
list[ApiModel] を返す。失敗時は fallback リストを返す。
"""

from scraper.providers.anthropic import scrape as scrape_anthropic
from scraper.providers.openai import scrape as scrape_openai
from scraper.providers.google import scrape as scrape_google
from scraper.providers.aws import scrape as scrape_aws
from scraper.providers.deepseek import scrape as scrape_deepseek
from scraper.providers.xai import scrape as scrape_xai

__all__ = [
    "scrape_anthropic",
    "scrape_openai",
    "scrape_google",
    "scrape_aws",
    "scrape_deepseek",
    "scrape_xai",
]
