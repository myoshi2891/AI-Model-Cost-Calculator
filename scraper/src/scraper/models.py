"""pricing.json のスキーマ定義 (Pydantic v2)"""

from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field


ScrapeStatus = Literal["success", "fallback", "manual"]


class ApiModel(BaseModel):
    provider: str
    name: str
    tag: str
    cls: str
    price_in: float = Field(ge=0)   # USD per 1M input tokens
    price_out: float = Field(ge=0)  # USD per 1M output tokens
    sub_ja: str
    sub_en: str
    scrape_status: ScrapeStatus = "manual"


class SubTool(BaseModel):
    group: str
    name: str
    monthly: float = Field(ge=0)
    annual: float | None = None     # None = 年払いなし、値 = 月換算年払い
    tag: str
    cls: str
    note_ja: str
    note_en: str
    scrape_status: ScrapeStatus = "manual"


class PricingData(BaseModel):
    generated_at: str               # ISO 8601 datetime string
    jpy_rate: float                 # 1 USD = jpy_rate JPY
    jpy_rate_date: str              # YYYY-MM-DD
    api_models: list[ApiModel]
    sub_tools: list[SubTool]
