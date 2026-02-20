"""USD/JPY 為替レートを Frankfurter API から取得する。

Frankfurter (https://www.frankfurter.app) は ECB データを使用する
APIキー不要の無料パブリック API。
失敗時は既存の pricing.json の値をフォールバックとして使用。
"""

from __future__ import annotations
import logging
from datetime import date as dt_date

import httpx

logger = logging.getLogger(__name__)

# Frankfurter API: ECB の公式レートを使用、APIキー不要
_FRANKFURTER_URL = "https://api.frankfurter.app/latest?from=USD&to=JPY"


def fetch_jpy_rate(fallback: float = 155.0) -> tuple[float, str]:
    """(rate, date) を返す。失敗時は (fallback, 'fallback') を返す。"""
    try:
        resp = httpx.get(_FRANKFURTER_URL, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        # {"amount": 1.0, "base": "USD", "date": "2026-02-21", "rates": {"JPY": 155.22}}
        rate: float = data["rates"]["JPY"]
        date_str: str = data.get("date", str(dt_date.today()))
        logger.info("USD/JPY rate fetched: %.2f (date: %s)", rate, date_str)
        return rate, date_str
    except Exception as exc:
        logger.warning("Frankfurter API fetch failed: %s — using fallback %.2f", exc, fallback)
    return fallback, "fallback"
