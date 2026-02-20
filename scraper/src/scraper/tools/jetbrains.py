"""JetBrains AI / Junie 料金スクレイパー。

対象: https://www.jetbrains.com/store/#personal
"""

from __future__ import annotations
import logging

from scraper.browser import get_page_text, extract_price, sanity_check
from scraper.models import SubTool

logger = logging.getLogger(__name__)

_URL = "https://www.jetbrains.com/ai/#plans"

_FALLBACKS: list[tuple[str, str, float, float | None, str, str, str, str]] = [
    ("JetBrains AI", "Free (基本AI機能)",          0,     0,    "Free",       "tag-mini",
     "補完・基本チャット / 10 AI actions/day", "Completions & basic chat / 10 AI actions/day"),
    ("JetBrains AI", "AI Pro (Individual)",       10,    100,  "Individual", "tag-jb",
     "無制限AI補完+チャット / 全IDE / ローカルモデル可", "Unlimited AI completion+chat / All IDEs / local models"),
    ("JetBrains AI", "AI Pro (All Products Pack)", 28.90, None, "All IDEs",   "tag-jb",
     "全JetBrains IDE + AI Pro込み",       "All JetBrains IDEs + AI Pro included"),
    ("JetBrains AI", "AI Business (Team)",         20,    None, "Team",       "tag-jb",
     "管理ダッシュ / SSO / 請求統合 /user", "Admin dashboard / SSO / centralized billing /user"),
    ("JetBrains AI", "AI Enterprise",              30,    None, "Enterprise", "tag-jb",
     "セルフホスト / BYOK / カスタムモデル /user", "Self-hosted / BYOK / custom models /user"),
    ("Junie (JetBrains)", "AI Pro incl. (Individual)", 10, 100,  "Agent",       "tag-jb",
     "AI Pro に含む / IntelliJ対応 / 自律タスク", "Included in AI Pro / IntelliJ / autonomous tasks"),
    ("Junie (JetBrains)", "AI Business incl. (Team)",  20, None, "Team Agent",  "tag-jb",
     "チーム向けJunie / 管理ダッシュ /user", "Junie for teams / admin dashboard /user"),
]


def scrape(existing: list[SubTool] | None = None) -> list[SubTool]:
    logger.info("JetBrains: スクレイピング開始 %s", _URL)

    try:
        html = get_page_text(_URL, timeout_ms=40_000)
    except Exception as exc:
        logger.warning("JetBrains: ページ取得失敗 %s → fallback", exc)
        return _build_fallback()

    tools: list[SubTool] = []
    for group, name, fb_m, fb_a, tag, cls, note_ja, note_en in _FALLBACKS:
        price = None
        if "AI Pro (Individual)" in name:
            price = extract_price(html, [r"ai\s+pro[^$\n]*?\$([\d.]+)\s*/\s*month"])
        elif "All Products Pack" in name:
            price = extract_price(html, [r"all\s+products[^$\n]*?\$([\d.]+)\s*/\s*month"])
        elif "AI Business" in name and "Junie" not in group:
            price = extract_price(html, [r"ai\s+business[^$\n]*?\$([\d.]+)\s*/\s*(?:user|month)"])
        elif "AI Enterprise" in name:
            price = extract_price(html, [r"ai\s+enterprise[^$\n]*?\$([\d.]+)\s*/\s*(?:user|month)"])

        cur_m = fb_m
        status = "fallback"
        if price is not None:
            new_m, s = sanity_check(price, f"JetBrains/{name}/monthly", fb_m)
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
