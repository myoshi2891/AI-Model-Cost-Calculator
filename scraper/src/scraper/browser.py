"""Playwright ブラウザの共通ユーティリティ。

price_from_page() はページを JS レンダリングしてテキストを返す。
3 層フォールバック:
  1. JSON-LD / script[type="application/json"] から抽出
  2. CSS セレクター群で抽出
  3. 正規表現でテキスト全体を検索
"""

from __future__ import annotations
import logging
import re

from playwright.sync_api import sync_playwright, Page

logger = logging.getLogger(__name__)

# 価格として有効な範囲（USD / 1M トークン）
_PRICE_MIN = 0.001
_PRICE_MAX = 2000.0


def get_page_text(url: str, wait_selector: str | None = None, timeout_ms: int = 30_000) -> str:
    """URL をヘッドレスブラウザで開き、ページテキスト全体を返す。"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page: Page = browser.new_page()
            page.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=timeout_ms)
            else:
                page.wait_for_timeout(3000)  # JS レンダリング待ち
            return page.content()
        finally:
            browser.close()


def extract_price(text: str, patterns: list[str]) -> float | None:
    """複数の正規表現パターンで最初にマッチした価格を返す。"""
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE | re.DOTALL)
        if m:
            try:
                price = float(m.group(1).replace(",", ""))
                if _PRICE_MIN <= price <= _PRICE_MAX:
                    return price
            except (ValueError, IndexError):
                pass
    return None


def sanity_check(value: float | None, name: str, fallback: float) -> tuple[float, str]:
    """値が有効範囲内かチェックし、(value, status) を返す。"""
    if value is None:
        logger.warning("%s: 抽出失敗 → fallback %.4f を使用", name, fallback)
        return fallback, "fallback"
    if not (_PRICE_MIN <= value <= _PRICE_MAX):
        logger.warning("%s: 範囲外の値 %.4f → fallback %.4f を使用", name, value, fallback)
        return fallback, "fallback"
    logger.info("%s: %.4f (success)", name, value)
    return value, "success"
