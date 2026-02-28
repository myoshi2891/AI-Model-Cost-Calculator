"""xAI (Grok) 料金スクレイパー。

対象: https://x.ai/api
"""

from __future__ import annotations
import logging

from scraper.browser import get_page_text, extract_price, sanity_check
from scraper.models import ApiModel

logger = logging.getLogger(__name__)

_URL = "https://x.ai/api"

_FALLBACKS: dict[str, tuple[float, float]] = {
    "Grok 4":      (3.00, 15.00),
    "Grok 4.1 Fast": (0.20,  0.50),
}
_TAG = {"Grok 4": "Flagship", "Grok 4.1 Fast": "Fast"}
_CLS = {"Grok 4": "tag-flag", "Grok 4.1 Fast": "tag-mini"}
_SUB_JA = {
    "Grok 4":      "Jul 2025 / 256K ctx",
    "Grok 4.1 Fast": "2Mコンテキスト / 業界最安クラス",
}
_SUB_EN = {
    "Grok 4":      "Jul 2025 / 256K ctx",
    "Grok 4.1 Fast": "2M context / among cheapest in class",
}


def scrape(existing: list[ApiModel] | None = None) -> list[ApiModel]:
    logger.info("xAI: スクレイピング開始 %s", _URL)

    fallback_map: dict[str, tuple[float, float]] = {}
    if existing:
        for m in existing:
            if m.provider == "xAI":
                fallback_map[m.name] = (m.price_in, m.price_out)
    for k, v in _FALLBACKS.items():
        fallback_map.setdefault(k, v)

    try:
        html = get_page_text(_URL, timeout_ms=40_000)
    except Exception as exc:
        logger.error("xAI: ページ取得失敗 %s", exc)
        return _build_fallback(fallback_map)

    models = []
    for name, (fb_in, fb_out) in _FALLBACKS.items():
        key = name.lower().replace(" ", "[-\\s]?").replace(".", r"\.")
        in_price = extract_price(html, [
            rf"{key}[^$]*?\$([\d.]+)",
        ])
        out_price = extract_price(html, [
            rf"{key}[^$]*?output[^$]*?\$([\d.]+)",
        ])
        pi, si = sanity_check(in_price, f"xAI/{name}/in", fb_in)
        po, so = sanity_check(out_price, f"xAI/{name}/out", fb_out)
        models.append(ApiModel(
            provider="xAI",
            name=name,
            tag=_TAG[name], cls=_CLS[name],
            price_in=pi, price_out=po,
            sub_ja=_SUB_JA[name], sub_en=_SUB_EN[name],
            scrape_status=si if si == so else "fallback",  # type: ignore[arg-type]
        ))
    return models


def _build_fallback(fallback_map: dict[str, tuple[float, float]]) -> list[ApiModel]:
    return [
        ApiModel(
            provider="xAI",
            name=n, tag=_TAG[n], cls=_CLS[n],
            price_in=fallback_map[n][0], price_out=fallback_map[n][1],
            sub_ja=_SUB_JA[n], sub_en=_SUB_EN[n],
            scrape_status="fallback",
        )
        for n in _FALLBACKS
    ]
