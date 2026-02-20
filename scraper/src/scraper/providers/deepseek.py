"""DeepSeek 料金スクレイパー。

対象: https://platform.deepseek.com/api-docs/pricing
"""

from __future__ import annotations
import logging

from scraper.browser import get_page_text, extract_price, sanity_check
from scraper.models import ApiModel

logger = logging.getLogger(__name__)

_URL = "https://platform.deepseek.com/api-docs/pricing"

_FALLBACKS: dict[str, tuple[float, float]] = {
    "DeepSeek-V3.2": (0.27, 1.10),
    "DeepSeek-R1":   (0.55, 2.19),
}
_TAG  = {"DeepSeek-V3.2": "General",   "DeepSeek-R1": "Reasoning"}
_CLS  = {"DeepSeek-V3.2": "tag-oss",   "DeepSeek-R1": "tag-oss"}
_SUB_JA = {
    "DeepSeek-V3.2": "671B MoE / OSS MIT",
    "DeepSeek-R1":   "CoT推論 / OSS MIT",
}
_SUB_EN = {
    "DeepSeek-V3.2": "671B MoE / OSS MIT",
    "DeepSeek-R1":   "Chain-of-thought reasoning / OSS MIT",
}


def scrape(existing: list[ApiModel] | None = None) -> list[ApiModel]:
    logger.info("DeepSeek: スクレイピング開始 %s", _URL)

    fallback_map: dict[str, tuple[float, float]] = {}
    if existing:
        for m in existing:
            if m.provider == "DeepSeek":
                fallback_map[m.name] = (m.price_in, m.price_out)
    for k, v in _FALLBACKS.items():
        fallback_map.setdefault(k, v)

    try:
        html = get_page_text(_URL, timeout_ms=40_000)
    except Exception as exc:
        logger.error("DeepSeek: ページ取得失敗 %s", exc)
        return _build_fallback(fallback_map)

    models = []
    for name, (fb_in, fb_out) in _FALLBACKS.items():
        key = name.lower().replace("-", "[-]?").replace(".", r"\.")
        in_price = extract_price(html, [
            rf"{key}[^$]*?\$([\d.]+)",
            rf"\$([\d.]+)[^$]*?{key}",
        ])
        out_price = extract_price(html, [
            rf"{key}[^$]*?output[^$]*?\$([\d.]+)",
            rf"output[^$]*?\$([\d.]+)[^$]*?{key}",
        ])
        pi, si = sanity_check(in_price, f"DeepSeek/{name}/in", fb_in)
        po, so = sanity_check(out_price, f"DeepSeek/{name}/out", fb_out)
        models.append(ApiModel(
            provider="DeepSeek",
            name=name,
            tag=_TAG[name],
            cls=_CLS[name],
            price_in=pi,
            price_out=po,
            sub_ja=_SUB_JA[name],
            sub_en=_SUB_EN[name],
            scrape_status=si if si == so else "fallback",  # type: ignore[arg-type]
        ))
    return models


def _build_fallback(fallback_map: dict[str, tuple[float, float]]) -> list[ApiModel]:
    return [
        ApiModel(
            provider="DeepSeek",
            name=n,
            tag=_TAG[n], cls=_CLS[n],
            price_in=fallback_map[n][0], price_out=fallback_map[n][1],
            sub_ja=_SUB_JA[n], sub_en=_SUB_EN[n],
            scrape_status="fallback",
        )
        for n in _FALLBACKS
    ]
