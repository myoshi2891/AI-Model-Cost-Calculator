"""AWS Bedrock 料金スクレイパー。

AWS Pricing JSON API を使用（スクレイピングより信頼性が高い）。
API エンドポイント:
  https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrock/current/index.json

失敗時は公式料金ページをフォールバックとして使用。
"""

from __future__ import annotations
import logging

import httpx

from scraper.browser import sanity_check
from scraper.models import ApiModel

logger = logging.getLogger(__name__)

_PRICING_API = (
    "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrock/current/index.json"
)

_FALLBACKS: dict[str, tuple[float, float]] = {
    "Amazon Nova Pro":   (0.80,  3.20),
    "Amazon Nova Micro": (0.035, 0.14),
}

_TAG = {
    "Amazon Nova Pro":   "Nova",
    "Amazon Nova Micro": "Cheapest",
}
_CLS = {
    "Amazon Nova Pro":   "tag-bal",
    "Amazon Nova Micro": "tag-mini",
}
_SUB_JA = {
    "Amazon Nova Pro":   "マルチモーダル / 300K ctx",
    "Amazon Nova Micro": "Bedrock最安モデル",
}
_SUB_EN = {
    "Amazon Nova Pro":   "Multimodal / 300K ctx",
    "Amazon Nova Micro": "Lowest-cost Bedrock model",
}

# AWS Pricing API の model キーワードマッピング
_AWS_KEYWORDS: dict[str, list[str]] = {
    "Amazon Nova Pro":   ["Nova Pro", "amazon.nova-pro"],
    "Amazon Nova Micro": ["Nova Micro", "amazon.nova-micro"],
}


def scrape(existing: list[ApiModel] | None = None) -> list[ApiModel]:
    """
    Fetches AWS Bedrock on-demand prices from the AWS Pricing API and returns normalized ApiModel entries.
    
    If provided, `existing` models from the AWS provider are used to seed fallback prices; built-in fallbacks fill any remaining missing models. Prices are converted to USD per 1,000,000 tokens (with recognition of per-1K unit descriptions) and selection prefers standard token usage tiers for the us-east-1 region. If the Pricing API call or parsing fails, all models fall back to the prepared fallback prices.
    
    Parameters:
        existing (list[ApiModel] | None): Optional list of previously scraped ApiModel objects whose AWS entries are used as higher-priority fallback prices.
    
    Returns:
        list[ApiModel]: List of ApiModel objects for each known model, each populated with provider="AWS", name, display metadata, computed price_in and price_out (USD per 1M tokens), and a scrape_status indicating whether the price was scraped or came from a fallback.
    """
    logger.info("AWS: Pricing API から取得開始")

    fallback_map: dict[str, tuple[float, float]] = {}
    if existing:
        for m in existing:
            if m.provider == "AWS":
                fallback_map[m.name] = (m.price_in, m.price_out)
    for k, v in _FALLBACKS.items():
        fallback_map.setdefault(k, v)

    results: dict[str, tuple[float, float, str]] = {}

    try:
        resp = httpx.get(_PRICING_API, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        products = data.get("products", {})
        terms = data.get("terms", {}).get("OnDemand", {})

        # モデルごとに SKU を探して価格を取得
        for model_name, keywords in _AWS_KEYWORDS.items():
            in_price: float | None = None
            out_price: float | None = None
            fb_in, fb_out = fallback_map[model_name]

            for sku, product in products.items():
                attrs = product.get("attributes", {})
                desc = attrs.get("modelId", "") + " " + attrs.get("model", "")
                if not any(kw.lower() in desc.lower() for kw in keywords):
                    continue
                usage_type = attrs.get("usagetype", "")
                # 入力トークン: InputToken / output: OutputToken
                sku_terms = terms.get(sku, {})
                for _, term in sku_terms.items():
                    for _, pd in term.get("priceDimensions", {}).items():
                        usd_per_unit = float(pd.get("pricePerUnit", {}).get("USD", "0") or "0")
                        if usd_per_unit == 0:
                            continue
                        usage_type_lower = usage_type.lower()
                        desc_lower = pd.get("description", "").lower()

                        # Skip non-standard tiers (batch, flex, etc.)
                        # Standard format: [Region]-Nova[Size]-[input|output]-tokens
                        if not (usage_type_lower.endswith("-input-tokens") or usage_type_lower.endswith("-output-tokens")):
                            continue

                        # Skip specific keywords in usage type
                        if any(kw in usage_type_lower for kw in ["batch", "flex", "priority", "custom-model", "latency-optimized", "cache", "storage", "throughput", "training"]):
                            continue

                        # USD per unit -> USD per 1M tokens
                        # AWS Bedrock is typically per 1,000 tokens
                        multiplier = 1000 if "1k" in desc_lower else 1_000_000
                        price_1m = usd_per_unit * multiplier

                        # Prefer us-east-1 (USE1) for price consistency
                        # Also prefer rows that don't have extra qualifiers in usage type
                        is_use1 = "use1" in usage_type_lower
                        
                        if "input" in usage_type_lower or "input" in desc_lower:
                            if in_price is None or (is_use1 and usage_type_lower.count("-") <= 3):
                                in_price = price_1m
                        elif "output" in usage_type_lower or "output" in desc_lower:
                            if out_price is None or (is_use1 and usage_type_lower.count("-") <= 3):
                                out_price = price_1m

            pi, si = sanity_check(in_price, f"AWS/{model_name}/in", fb_in)
            po, so = sanity_check(out_price, f"AWS/{model_name}/out", fb_out)
            results[model_name] = (pi, po, si if si == so else "fallback")

    except Exception as exc:
        logger.warning("AWS: Pricing API 失敗 %s → fallback", exc)
        for n, (fb_in, fb_out) in fallback_map.items():
            results[n] = (fb_in, fb_out, "fallback")

    return [
        ApiModel(
            provider="AWS",
            name=n,
            tag=_TAG.get(n, ""),
            cls=_CLS.get(n, "tag-bal"),
            price_in=results[n][0],
            price_out=results[n][1],
            sub_ja=_SUB_JA.get(n, ""),
            sub_en=_SUB_EN.get(n, ""),
            scrape_status=results[n][2],  # type: ignore[arg-type]
        )
        for n in _FALLBACKS
        if n in results
    ]