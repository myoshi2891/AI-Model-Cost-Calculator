"""Google One AI Plans 料金スクレイパー。

対象: https://one.google.com/about/google-ai-plans/
"""

from __future__ import annotations
import logging

from scraper.browser import get_page_text, extract_price, sanity_check
from scraper.models import SubTool

logger = logging.getLogger(__name__)

_URL = "https://one.google.com/about/google-ai-plans/"

_FALLBACKS: list[tuple[str, str, float, float | None, str, str, str, str]] = [
    ("Google One AI", "AI Plus",  9.99,   None, "Plus",  "tag-bal",
     "200GB / Gemini 3.1 Pro / Veo 3.1 Fast / Jules (coding)",
     "200 GB / Gemini 3.1 Pro / Veo 3.1 Fast / Jules (coding)"),
    ("Google One AI", "AI Pro",   19.99,  None, "Pro",   "tag-flag",
     "2TB / Deep Research / Jules 拡張 / Google Home Premium",
     "2 TB / Deep Research / Jules extended / Google Home Premium"),
    ("Google One AI", "AI Ultra", 249.99, None, "Ultra", "tag-flag",
     "30TB / Deep Think / Mariner / YouTube Premium / 最上位",
     "30 TB / Deep Think / Project Mariner / YouTube Premium / Top tier"),
]


def scrape(existing: list[SubTool] | None = None) -> list[SubTool]:
    logger.info("Google One AI: スクレイピング開始 %s", _URL)

    try:
        html = get_page_text(_URL, timeout_ms=40_000)
    except Exception as exc:
        logger.warning("Google One AI: ページ取得失敗 %s → fallback", exc)
        return _build_fallback()

    tools: list[SubTool] = []
    for group, name, fb_m, fb_a, tag, cls, note_ja, note_en in _FALLBACKS:
        price = None
        plan_key = name.lower().split()[-1]  # "plus", "pro", "ultra"
        price = extract_price(html, [
            rf"ai\s+{plan_key}[^$\n]*?\$([\d.]+)\s*/\s*m(?:o|onth)",
            rf"\$([\d.]+)[^$\n]*?ai\s+{plan_key}",
        ])

        cur_m = fb_m
        status = "fallback"
        if price is not None:
            new_m, s = sanity_check(price, f"GoogleOneAI/{name}/monthly", fb_m)
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
