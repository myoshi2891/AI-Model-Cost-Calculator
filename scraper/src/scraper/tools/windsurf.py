"""Windsurf 料金スクレイパー。

対象: https://windsurf.com/pricing
"""

from __future__ import annotations
import logging

from scraper.browser import get_page_text, extract_price, sanity_check
from scraper.models import SubTool

logger = logging.getLogger(__name__)

_URL = "https://windsurf.com/pricing"

_FALLBACKS: list[tuple[str, str, float, float | None, str, str, str, str]] = [
    ("Windsurf", "Free",  0,  None, "Free",       "tag-mini",
     "25 credits/月 | 全モデル対応",   "25 credits/mo | All models"),
    ("Windsurf", "Pro",   15, None, "Individual", "tag-bal",
     "500 credits/月 | SWE-1.5 含む", "500 credits/mo | Includes SWE-1.5"),
    ("Windsurf", "Teams", 30, None, "Team",       "tag-bal",
     "500 credits/user + 管理機能",    "500 credits/user + admin features"),
]


def scrape(existing: list[SubTool] | None = None) -> list[SubTool]:
    logger.info("Windsurf: スクレイピング開始 %s", _URL)

    try:
        html = get_page_text(_URL, timeout_ms=40_000)
    except Exception as exc:
        logger.warning("Windsurf: ページ取得失敗 %s → fallback", exc)
        return _build_fallback()

    tools: list[SubTool] = []
    for group, name, fb_m, fb_a, tag, cls, note_ja, note_en in _FALLBACKS:
        price = None
        if name == "Pro":
            price = extract_price(html, [r"pro[^$\n]*?\$([\d]+)\s*/\s*month"])
        elif name == "Teams":
            price = extract_price(html, [r"team[^$\n]*?\$([\d]+)\s*/\s*(?:user|month)"])

        cur_m = fb_m
        status = "fallback"
        if price is not None:
            new_m, s = sanity_check(price, f"Windsurf/{name}/monthly", fb_m)
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
