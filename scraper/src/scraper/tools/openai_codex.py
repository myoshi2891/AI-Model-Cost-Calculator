"""OpenAI Codex (ChatGPT) 料金スクレイパー。

対象: https://openai.com/chatgpt/pricing/
"""

from __future__ import annotations
import logging

from scraper.browser import get_page_text, extract_price, sanity_check
from scraper.models import SubTool

logger = logging.getLogger(__name__)

_URL = "https://openai.com/chatgpt/pricing/"

_FALLBACKS: list[tuple[str, str, float, float | None, str, str, str, str]] = [
    ("OpenAI Codex", "ChatGPT Plus (Codex)",  20,  None, "Plus", "tag-bal",
     "30-150 tasks/5h | codex-1",    "30-150 tasks/5h | codex-1"),
    ("OpenAI Codex", "ChatGPT Pro (Codex)",  200,  None, "Pro",  "tag-flag",
     "300-1500 tasks/5h | 全機能",   "300-1500 tasks/5h | All features"),
]


def scrape(existing: list[SubTool] | None = None) -> list[SubTool]:
    logger.info("OpenAI Codex: スクレイピング開始 %s", _URL)

    try:
        html = get_page_text(_URL, timeout_ms=40_000)
    except Exception as exc:
        logger.warning("OpenAI Codex: ページ取得失敗 %s → fallback", exc)
        return _build_fallback()

    tools: list[SubTool] = []
    for group, name, fb_m, fb_a, tag, cls, note_ja, note_en in _FALLBACKS:
        price = None
        if "Plus" in name:
            price = extract_price(html, [r"plus[^$\n]*?\$([\d]+)\s*/\s*month"])
        elif "Pro" in name:
            price = extract_price(html, [r"(?:chatgpt\s+)?pro[^$\n]*?\$([\d]+)\s*/\s*month"])

        cur_m = fb_m
        status = "fallback"
        if price is not None:
            new_m, s = sanity_check(price, f"OpenAICodex/{name}/monthly", fb_m)
            cur_m = new_m
            status = s

        tools.append(SubTool(
            group=group, name=name,
            monthly=cur_m, annual=fb_a,
            tag=tag, cls=cls,
            note_ja=note_ja, note_en=note_en,
            scrape_status=status,  # type: ignore[arg-type]
        ))
    return tools


def _build_fallback() -> list[SubTool]:
    return [
        SubTool(group=g, name=n, monthly=m, annual=a, tag=t, cls=c,
                note_ja=nj, note_en=ne, scrape_status="fallback")
        for g, n, m, a, t, c, nj, ne in _FALLBACKS
    ]
