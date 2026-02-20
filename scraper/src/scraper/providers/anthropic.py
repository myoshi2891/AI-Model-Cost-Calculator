"""Anthropic 公式料金ページスクレイパー。

対象: https://www.anthropic.com/pricing
"""

from __future__ import annotations
import logging

from scraper.browser import get_page_text, extract_price, sanity_check
from scraper.models import ApiModel

logger = logging.getLogger(__name__)

_URL = "https://www.anthropic.com/pricing"

# フォールバック価格（ハードコード最終手段）
_FALLBACKS: dict[str, tuple[float, float]] = {
    "Claude Opus 4.6":          (5.00,  25.00),
    "Claude Sonnet 4.6":        (3.00,  15.00),
    "Claude Haiku 4.5":         (1.00,   5.00),
    "Claude Opus 4.1 (Legacy)": (15.00, 75.00),
    "Claude Haiku 3":           (0.25,   1.25),
}


def scrape(existing: list[ApiModel] | None = None) -> list[ApiModel]:
    """Anthropic の価格をスクレイピングして ApiModel リストを返す。"""
    logger.info("Anthropic: スクレイピング開始 %s", _URL)

    # 既存値をフォールバックとして使う（既存 JSON があれば）
    fallback_map: dict[str, tuple[float, float]] = {}
    if existing:
        for m in existing:
            if m.provider == "Anthropic":
                fallback_map[m.name] = (m.price_in, m.price_out)
    for k, v in _FALLBACKS.items():
        fallback_map.setdefault(k, v)

    try:
        html = get_page_text(_URL, timeout_ms=40_000)
    except Exception as exc:
        logger.error("Anthropic: ページ取得失敗 %s", exc)
        return _build_models(fallback_map, "fallback")

    results: dict[str, tuple[float, float, str]] = {}

    # Claude Opus 4.6: $5 / $25
    in_price = extract_price(html, [
        r"opus[^\n]*?4\.6[^\n]*?\$\s*([\d.]+)",
        r"claude-opus-4[^\n]*?\$\s*([\d.]+)",
    ])
    out_price = extract_price(html, [
        r"opus[^\n]*?4\.6[^\n]*?\$[\d.]+[^\n]*?\$\s*([\d.]+)",
    ])
    fb_in, fb_out = fallback_map["Claude Opus 4.6"]
    pi, si = sanity_check(in_price, "Anthropic/Opus4.6/in", fb_in)
    po, so = sanity_check(out_price, "Anthropic/Opus4.6/out", fb_out)
    results["Claude Opus 4.6"] = (pi, po, si if si == so else "fallback")

    # Claude Sonnet 4.6: $3 / $15
    in_price = extract_price(html, [
        r"sonnet[^\n]*?4\.6[^\n]*?\$\s*([\d.]+)",
        r"claude-sonnet-4[^\n]*?\$\s*([\d.]+)",
    ])
    out_price = extract_price(html, [
        r"sonnet[^\n]*?4\.6[^\n]*?\$[\d.]+[^\n]*?\$\s*([\d.]+)",
    ])
    fb_in, fb_out = fallback_map["Claude Sonnet 4.6"]
    pi, si = sanity_check(in_price, "Anthropic/Sonnet4.6/in", fb_in)
    po, so = sanity_check(out_price, "Anthropic/Sonnet4.6/out", fb_out)
    results["Claude Sonnet 4.6"] = (pi, po, si if si == so else "fallback")

    # Claude Haiku 4.5: $1 / $5
    in_price = extract_price(html, [
        r"haiku[^\n]*?4\.5[^\n]*?\$\s*([\d.]+)",
        r"claude-haiku-4[^\n]*?\$\s*([\d.]+)",
    ])
    out_price = extract_price(html, [
        r"haiku[^\n]*?4\.5[^\n]*?\$[\d.]+[^\n]*?\$\s*([\d.]+)",
    ])
    fb_in, fb_out = fallback_map["Claude Haiku 4.5"]
    pi, si = sanity_check(in_price, "Anthropic/Haiku4.5/in", fb_in)
    po, so = sanity_check(out_price, "Anthropic/Haiku4.5/out", fb_out)
    results["Claude Haiku 4.5"] = (pi, po, si if si == so else "fallback")

    # Legacy / Budget はフォールバック維持
    for name in ("Claude Opus 4.1 (Legacy)", "Claude Haiku 3"):
        fb_in, fb_out = fallback_map[name]
        results[name] = (fb_in, fb_out, "fallback")

    return _build_models_from_results(results, fallback_map)


def _build_models(
    fallback_map: dict[str, tuple[float, float]], status: str
) -> list[ApiModel]:
    return [
        ApiModel(
            provider="Anthropic",
            name=n,
            tag="最新 Feb-26" if "4.6" in n or "4.5" in n else ("Legacy" if "Legacy" in n else "Budget"),
            cls="tag-flag" if "4.6" in n else ("tag-mini" if n == "Claude Haiku 3" else ("tag-leg" if "Legacy" in n else "tag-mini")),
            price_in=v[0],
            price_out=v[1],
            sub_ja=_SUB_JA.get(n, ""),
            sub_en=_SUB_EN.get(n, ""),
            scrape_status=status,  # type: ignore[arg-type]
        )
        for n, v in _FALLBACKS.items()
    ]


def _build_models_from_results(
    results: dict[str, tuple[float, float, str]],
    fallback_map: dict[str, tuple[float, float]],
) -> list[ApiModel]:
    order = list(_FALLBACKS.keys())
    return [
        ApiModel(
            provider="Anthropic",
            name=n,
            tag=_TAG.get(n, ""),
            cls=_CLS.get(n, "tag-bal"),
            price_in=results[n][0],
            price_out=results[n][1],
            sub_ja=_SUB_JA.get(n, ""),
            sub_en=_SUB_EN.get(n, ""),
            scrape_status=results[n][2],  # type: ignore[arg-type]
        )
        for n in order
        if n in results
    ]


_TAG = {
    "Claude Opus 4.6":          "最新",
    "Claude Sonnet 4.6":        "最新",
    "Claude Haiku 4.5":         "Fast",
    "Claude Opus 4.1 (Legacy)": "Legacy",
    "Claude Haiku 3":           "Budget",
}
_CLS = {
    "Claude Opus 4.6":          "tag-flag",
    "Claude Sonnet 4.6":        "tag-flag",
    "Claude Haiku 4.5":         "tag-mini",
    "Claude Opus 4.1 (Legacy)": "tag-leg",
    "Claude Haiku 3":           "tag-mini",
}
_SUB_JA = {
    "Claude Opus 4.6":          "エージェントチーム / 200K",
    "Claude Sonnet 4.6":        "バランス最適 / 200K",
    "Claude Haiku 4.5":         "高速・高ボリューム向け",
    "Claude Opus 4.1 (Legacy)": "旧フラッグシップ / 非推奨",
    "Claude Haiku 3":           "Claude最安値モデル",
}
_SUB_EN = {
    "Claude Opus 4.6":          "Agent teams / 200K ctx",
    "Claude Sonnet 4.6":        "Optimal balance / 200K ctx",
    "Claude Haiku 4.5":         "Fast / high-volume use cases",
    "Claude Opus 4.1 (Legacy)": "Legacy flagship / deprecated",
    "Claude Haiku 3":           "Claude lowest-cost model",
}
