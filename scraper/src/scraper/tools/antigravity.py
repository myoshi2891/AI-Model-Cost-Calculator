"""Antigravity (Google) 料金スクレイパー。

対象: https://antigravity.google/pricing
JS レンダリングが必要なページ。価格が取得できない場合は既存値を維持。
"""

from __future__ import annotations
import logging

from scraper.browser import get_page_text, extract_price, sanity_check
from scraper.models import SubTool

logger = logging.getLogger(__name__)

_URL = "https://antigravity.google/pricing"

# 既知のフォールバック（ページが読めない場合に使用）
_FALLBACKS: list[tuple[str, str, float, float | None, str, str, str, str]] = [
    ("Antigravity", "Free",  0,  None, "Free (Google)", "tag-mini",
     "⚠要確認 / antigravity.google / 基本機能", "⚠ Verify / antigravity.google / Basic features"),
    ("Antigravity", "Pro",   20, None, "Indiv. ⚠",     "tag-ag",
     "⚠要確認 / antigravity.google/pricing", "⚠ Verify at antigravity.google/pricing"),
    ("Antigravity", "Team",  40, None, "Team ⚠",       "tag-ag",
     "⚠要確認 / SSO + 管理 / /user", "⚠ Verify / SSO + admin / /user"),
]


def scrape(existing: list[SubTool] | None = None) -> list[SubTool]:
    logger.info("Antigravity: スクレイピング開始 %s", _URL)

    fb_map: dict[str, tuple[float, float | None]] = {
        row[1]: (row[2], row[3]) for row in _FALLBACKS
    }
    if existing:
        for t in existing:
            if t.group == "Antigravity":
                fb_map[t.name] = (t.monthly, t.annual)

    try:
        html = get_page_text(_URL, timeout_ms=40_000)
    except Exception as exc:
        logger.warning("Antigravity: ページ取得失敗 %s → fallback", exc)
        return _build_fallback(fb_map)

    tools: list[SubTool] = []
    for group, name, _, fb_a, tag, cls, note_ja, note_en in _FALLBACKS:
        fb_m = fb_map.get(name, (0, None))[0]
        price = None
        if name != "Free":
            plan_key = name.lower()
            price = extract_price(html, [
                rf"{plan_key}[^$\n]*?\$([\d.]+)\s*/\s*(?:month|mo|user)",
                rf"\$([\d.]+)[^$\n]*?{plan_key}",
            ])

        cur_m = fb_m
        status = "fallback"
        if price is not None:
            new_m, s = sanity_check(price, f"Antigravity/{name}/monthly", fb_m)
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


def _build_fallback(fb_map: dict[str, tuple[float, float | None]]) -> list[SubTool]:
    return [
        SubTool(
            group=g, name=n,
            monthly=fb_map.get(n, (m, a))[0],
            annual=fb_map.get(n, (m, a))[1],
            tag=t, cls=c,
            note_ja=nj, note_en=ne,
            scrape_status="fallback",
        )
        for g, n, m, a, t, c, nj, ne in _FALLBACKS
    ]
