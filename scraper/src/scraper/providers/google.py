"""Google AI Studio / Vertex AI 料金スクレイパー。

対象:
  - Google AI Studio: https://ai.google.dev/pricing
  - Vertex AI:        https://cloud.google.com/vertex-ai/generative-ai/pricing
"""

from __future__ import annotations
import logging

from scraper.browser import get_page_text, extract_price, sanity_check
from scraper.models import ApiModel

logger = logging.getLogger(__name__)

_URL_GOOGLE_AI = "https://ai.google.dev/pricing"
_URL_VERTEX = "https://cloud.google.com/vertex-ai/generative-ai/pricing"

_FALLBACKS: dict[str, tuple[float, float, str, str, str, str, str]] = {
    # name: (price_in, price_out, provider, tag, cls, sub_ja, sub_en)
    "Gemini 3.1 Pro Preview": (2.00,  12.00, "Google AI", "Preview",  "tag-flag", "最新世代 / 1M ctx",    "Latest generation / 1M ctx"),
    "Gemini 2.5 Pro":         (1.25,  10.00, "Google AI", "Flagship", "tag-flag", "コーディング最強 / 1M ctx", "Top coding model / 1M ctx"),
    "Gemini 2.5 Flash":       (0.30,   2.50, "Google AI", "Fast",     "tag-bal",  "バランス高速 / 1M ctx",   "Balanced & fast / 1M ctx"),
    "Gemini 2.5 Flash-Lite":  (0.10,   0.40, "Google AI", "Budget",   "tag-mini", "超低コスト / 1M ctx",    "Ultra low cost / 1M ctx"),
    "Gemini 2.5 Pro (Vertex)":        (1.25,  10.00, "Vertex AI", "GCP Enterprise", "tag-vtx",
                                       "Google AIと同額 / GCP SLA / ≤200K", "Same as Google AI / GCP SLA / ≤200K"),
    "Gemini 2.5 Pro >200K (Vertex)":  (2.50,  15.00, "Vertex AI", "Long Context",   "tag-vtx",
                                       "200K超コンテキスト / VPC Controls", ">200K context / VPC Controls"),
    "Gemini 2.5 Flash (Vertex)":      (0.30,   2.50, "Vertex AI", "GCP Fast",       "tag-vtx",
                                       "同Google AI料金 / GCP課金 / 1M", "Same as Google AI / GCP billing / 1M"),
    "Gemini 2.5 Flash-Lite (Vertex)": (0.10,   0.40, "Vertex AI", "GCP Budget",     "tag-vtx",
                                       "最安 / GCP無料枠あり / 1M", "Lowest cost / GCP free tier / 1M"),
}


def scrape(existing: list[ApiModel] | None = None) -> list[ApiModel]:
    """Google AI / Vertex AI の価格をスクレイピング。"""
    logger.info("Google AI: スクレイピング開始")

    fallback_map: dict[str, tuple[float, float]] = {}
    if existing:
        for m in existing:
            if m.provider in ("Google AI", "Vertex AI"):
                fallback_map[m.name] = (m.price_in, m.price_out)
    for k, v in _FALLBACKS.items():
        fallback_map.setdefault(k, (v[0], v[1]))

    # Google AI Studio ページを取得
    google_html = ""
    try:
        google_html = get_page_text(_URL_GOOGLE_AI, timeout_ms=40_000)
    except Exception as exc:
        logger.warning("Google AI: ページ取得失敗 %s", exc)

    models = []
    for name, fb_data in _FALLBACKS.items():
        fb_in, fb_out = fb_data[0], fb_data[1]
        provider, tag, cls, sub_ja, sub_en = fb_data[2], fb_data[3], fb_data[4], fb_data[5], fb_data[6]

        # Gemini Pro は Google AI Studio ページから取得試みる
        html_to_use = google_html if provider == "Google AI" else ""
        status = "fallback"

        if html_to_use:
            model_key = name.lower().replace(" ", "[-\\s]?").replace(".", r"\.")
            in_price = extract_price(html_to_use, [
                rf"{model_key}[^$]*?\$([\d.]+)\s*/\s*1M",
                rf"\$([\d.]+)[^$]*?{model_key}",
            ])
            out_price = extract_price(html_to_use, [
                rf"{model_key}[^$]*?output[^$]*?\$([\d.]+)",
            ])
            pi, si = sanity_check(in_price, f"GoogleAI/{name}/in", fb_in)
            po, so = sanity_check(out_price, f"GoogleAI/{name}/out", fb_out)
            fb_in, fb_out = pi, po
            status = si if si == so else "fallback"
        else:
            logger.info("%s: フォールバック値を使用", name)

        models.append(ApiModel(
            provider=provider,
            name=name,
            tag=tag,
            cls=cls,
            price_in=fb_in,
            price_out=fb_out,
            sub_ja=sub_ja,
            sub_en=sub_en,
            scrape_status=status,  # type: ignore[arg-type]
        ))

    return models
