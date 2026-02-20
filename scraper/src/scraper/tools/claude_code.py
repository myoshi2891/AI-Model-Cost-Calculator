"""Claude Code 料金スクレイパー。

対象: https://docs.anthropic.com/en/docs/claude-code/pricing
"""

from __future__ import annotations
import logging

from scraper.browser import get_page_text, extract_price, sanity_check
from scraper.models import SubTool

logger = logging.getLogger(__name__)

_URL = "https://docs.anthropic.com/en/docs/claude-code/pricing"

_FALLBACKS: list[tuple[str, str, float, float | None, str, str, str, str]] = [
    ("Claude Code", "Pro",           20,  17,   "Individual", "tag-bal",
     "~45 msg/5h | Claude CLI含む",      "~45 msg/5h | Includes Claude CLI"),
    ("Claude Code", "Max 5x",        100, None, "Power",      "tag-flag",
     "~225 msg/5h | Pro×5",              "~225 msg/5h | Pro×5"),
    ("Claude Code", "Max 20x",       200, None, "Max",        "tag-flag",
     "~900 msg/5h | Pro×20",             "~900 msg/5h | Pro×20"),
    ("Claude Code", "Team Standard", 30,  25,   "Team",       "tag-bal",
     "SSO + 集中課金 | /user (5席~)",    "SSO + centralized billing | /user (5+ seats)"),
]


def scrape(existing: list[SubTool] | None = None) -> list[SubTool]:
    logger.info("Claude Code: スクレイピング開始 %s", _URL)

    try:
        html = get_page_text(_URL, timeout_ms=40_000)
    except Exception as exc:
        logger.warning("Claude Code: ページ取得失敗 %s → fallback", exc)
        return _build_fallback()

    tools: list[SubTool] = []
    for group, name, fb_m, fb_a, tag, cls, note_ja, note_en in _FALLBACKS:
        price = None
        if name == "Pro":
            price = extract_price(html, [r"pro[^$\n]*?\$([\d]+)\s*/\s*month"])
        elif name == "Max 5x":
            price = extract_price(html, [r"max[^$\n]*?5x[^$\n]*?\$([\d]+)"])
        elif name == "Max 20x":
            price = extract_price(html, [r"max[^$\n]*?20x[^$\n]*?\$([\d]+)"])
        elif name == "Team Standard":
            price = extract_price(html, [r"team[^$\n]*?\$([\d]+)\s*/\s*(?:user|member)"])

        cur_m = fb_m
        status = "fallback"
        if price is not None:
            new_m, s = sanity_check(price, f"ClaudeCode/{name}/monthly", fb_m)
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
