"""OpenAI 公式料金ページスクレイパー。

対象: https://openai.com/api/pricing/
"""

from __future__ import annotations
import logging

from scraper.browser import get_page_text, extract_price, sanity_check
from scraper.models import ApiModel

logger = logging.getLogger(__name__)

_URL = "https://openai.com/api/pricing/"

_FALLBACKS: dict[str, tuple[float, float]] = {
    "o3-pro":       (20.00,  80.00),
    "o1":           (15.00,  60.00),
    "o3":           (2.00,    8.00),
    "o4-mini":      (1.10,    4.40),
    "GPT-5":        (1.25,   10.00),
    "GPT-4o-latest":(5.00,   15.00),
    "GPT-4o":       (2.50,   10.00),
    "GPT-4.1":      (2.00,    8.00),
    "GPT-5 Mini":   (0.25,    2.00),
    "GPT-4.1 Mini": (0.40,    1.60),
    "GPT-4o Mini":  (0.15,    0.60),
    "GPT-5 Nano":   (0.05,    0.40),
}

_TAG = {
    "o3-pro":        "Reasoning",
    "o1":            "Legacy",
    "o3":            "Reasoning ↓80%OFF",
    "o4-mini":       "Reasoning",
    "GPT-5":         "Flagship",
    "GPT-4o-latest": "Latest",
    "GPT-4o":        "Stable",
    "GPT-4.1":       "New",
    "GPT-5 Mini":    "Balanced",
    "GPT-4.1 Mini":  "Mini",
    "GPT-4o Mini":   "Budget",
    "GPT-5 Nano":    "Budget",
}
_CLS = {
    "o3-pro":        "tag-rsn",
    "o1":            "tag-leg",
    "o3":            "tag-rsn",
    "o4-mini":       "tag-rsn",
    "GPT-5":         "tag-flag",
    "GPT-4o-latest": "tag-bal",
    "GPT-4o":        "tag-bal",
    "GPT-4.1":       "tag-bal",
    "GPT-5 Mini":    "tag-bal",
    "GPT-4.1 Mini":  "tag-mini",
    "GPT-4o Mini":   "tag-mini",
    "GPT-5 Nano":    "tag-mini",
}
_SUB_JA = {
    "o3-pro":        "最高品質推論 / Jun 2025",
    "o1":            "旧推論フラッグシップ",
    "o3":            "Jun 2025: $10→$2 値下げ",
    "o4-mini":       "軽量推論 / 200K ctx",
    "GPT-5":         "SWE-bench最高クラス / 400K",
    "GPT-4o-latest": "ChatGPT最新版追跡モデル",
    "GPT-4o":        "マルチモーダル安定版 / 128K",
    "GPT-4.1":       "1Mコンテキスト / Apr 2025",
    "GPT-5 Mini":    "汎用バランスモデル / 400K",
    "GPT-4.1 Mini":  "1Mコンテキスト軽量版",
    "GPT-4o Mini":   "コスト重視マルチモーダル",
    "GPT-5 Nano":    "最安クラス / 大量分類向け",
}
_SUB_EN = {
    "o3-pro":        "Highest quality reasoning / Jun 2025",
    "o1":            "Legacy reasoning flagship",
    "o3":            "Jun 2025: $10→$2 price cut",
    "o4-mini":       "Lightweight reasoning / 200K ctx",
    "GPT-5":         "Top SWE-bench / 400K ctx",
    "GPT-4o-latest": "Tracks latest ChatGPT version",
    "GPT-4o":        "Multimodal stable / 128K ctx",
    "GPT-4.1":       "1M context / Apr 2025",
    "GPT-5 Mini":    "General purpose balanced / 400K",
    "GPT-4.1 Mini":  "1M context lightweight",
    "GPT-4o Mini":   "Cost-efficient multimodal",
    "GPT-5 Nano":    "Ultra-budget / high-volume classification",
}


def scrape(existing: list[ApiModel] | None = None) -> list[ApiModel]:
    """OpenAI の価格をスクレイピングして ApiModel リストを返す。"""
    logger.info("OpenAI: スクレイピング開始 %s", _URL)

    fallback_map: dict[str, tuple[float, float]] = {}
    if existing:
        for m in existing:
            if m.provider == "OpenAI":
                fallback_map[m.name] = (m.price_in, m.price_out)
    for k, v in _FALLBACKS.items():
        fallback_map.setdefault(k, v)

    try:
        html = get_page_text(_URL, timeout_ms=40_000)
    except Exception as exc:
        logger.error("OpenAI: ページ取得失敗 %s", exc)
        return _build_fallback(fallback_map)

    models = []
    for name, (fb_in, fb_out) in _FALLBACKS.items():
        # モデル名をキーに周辺の価格テキストを探す
        key = name.lower().replace(" ", "[-\\s]?").replace(".", r"\.")
        in_price = extract_price(html, [
            rf"{key}[^$]*?\$([\d.]+)\s*/\s*1M.*?input",
            rf"{key}[^$]*?\$([\d.]+)\s*per\s*(?:1M|million).*?input",
            rf"input[^$]*?\$([\d.]+)[^$]*?{key}",
        ])
        out_price = extract_price(html, [
            rf"{key}[^$]*?output[^$]*?\$([\d.]+)",
            rf"output[^$]*?\$([\d.]+)[^$]*?{key}",
        ])
        pi, si = sanity_check(in_price, f"OpenAI/{name}/in", fb_in)
        po, so = sanity_check(out_price, f"OpenAI/{name}/out", fb_out)
        status = si if si == so else "fallback"
        models.append(ApiModel(
            provider="OpenAI",
            name=name,
            tag=_TAG.get(name, ""),
            cls=_CLS.get(name, "tag-bal"),
            price_in=pi,
            price_out=po,
            sub_ja=_SUB_JA.get(name, ""),
            sub_en=_SUB_EN.get(name, ""),
            scrape_status=status,  # type: ignore[arg-type]
        ))

    return models


def _build_fallback(fallback_map: dict[str, tuple[float, float]]) -> list[ApiModel]:
    return [
        ApiModel(
            provider="OpenAI",
            name=n,
            tag=_TAG.get(n, ""),
            cls=_CLS.get(n, "tag-bal"),
            price_in=fallback_map[n][0],
            price_out=fallback_map[n][1],
            sub_ja=_SUB_JA.get(n, ""),
            sub_en=_SUB_EN.get(n, ""),
            scrape_status="fallback",
        )
        for n in _FALLBACKS
    ]
