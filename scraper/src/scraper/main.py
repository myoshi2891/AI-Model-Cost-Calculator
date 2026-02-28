"""スクレイパー CLI エントリポイント。

Usage:
    uv run python -m scraper.main [--output PATH] [--no-scrape]

--output: 出力先 JSON パス (デフォルト: ../../pricing.json)
--no-scrape: スクレイピングをスキップし、既存値 or フォールバック値のみで出力
"""

from __future__ import annotations
import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import TypeVar, Callable

from scraper.exchange import fetch_jpy_rate
from scraper.models import ApiModel, PricingData, SubTool
from scraper.providers import (
    scrape_anthropic,
    scrape_openai,
    scrape_google,
    scrape_aws,
    scrape_deepseek,
    scrape_xai,
)
from scraper.tools import (
    scrape_github_copilot,
    scrape_cursor,
    scrape_windsurf,
    scrape_claude_code,
    scrape_jetbrains,
    scrape_openai_codex,
    scrape_google_one,
    scrape_antigravity,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

_DEFAULT_OUTPUT = Path(__file__).parent.parent.parent.parent.parent / "pricing.json"

T = TypeVar("T")


def _load_existing(output_path: Path) -> PricingData | None:
    """既存の pricing.json を読み込んでフォールバック値として使う。"""
    if not output_path.exists():
        return None
    try:
        with output_path.open(encoding="utf-8") as f:
            return PricingData.model_validate(json.load(f))
    except Exception as exc:
        logger.warning("既存 pricing.json の読み込み失敗: %s", exc)
        return None


def _run_scraper(fn: Callable[[], list[T]], label: str, dest: list[T]) -> None:
    """スクレイパー 1 件を安全に実行し dest に追加する。"""
    try:
        result = fn()
        dest.extend(result)
        success = sum(1 for m in result if getattr(m, "scrape_status", "") == "success")
        logger.info("%s: %d件取得 (%d件 success)", label, len(result), success)
    except Exception as exc:
        logger.error("%s: スクレイパークラッシュ %s", label, exc)


def _scrape_all(
    existing_api: list[ApiModel] | None,
    existing_tools: list[SubTool] | None,
) -> tuple[list[ApiModel], list[SubTool]]:
    """全プロバイダーをスクレイピングして (api_models, sub_tools) を返す。"""
    logger.info("=== API プロバイダーのスクレイピング開始 ===")
    api_models: list[ApiModel] = []
    for fn, label in [
        (lambda: scrape_anthropic(existing_api), "Anthropic"),
        (lambda: scrape_openai(existing_api),    "OpenAI"),
        (lambda: scrape_google(existing_api),    "Google AI / Vertex AI"),
        (lambda: scrape_aws(existing_api),       "AWS Bedrock"),
        (lambda: scrape_deepseek(existing_api),  "DeepSeek"),
        (lambda: scrape_xai(existing_api),       "xAI"),
    ]:
        _run_scraper(fn, label, api_models)

    logger.info("=== コーディングツールのスクレイピング開始 ===")
    sub_tools: list[SubTool] = []
    for fn, label in [
        (lambda: scrape_github_copilot(existing_tools), "GitHub Copilot"),
        (lambda: scrape_cursor(existing_tools),         "Cursor"),
        (lambda: scrape_windsurf(existing_tools),       "Windsurf"),
        (lambda: scrape_claude_code(existing_tools),    "Claude Code"),
        (lambda: scrape_jetbrains(existing_tools),      "JetBrains AI / Junie"),
        (lambda: scrape_openai_codex(existing_tools),   "OpenAI Codex"),
        (lambda: scrape_google_one(existing_tools),     "Google One AI"),
        (lambda: scrape_antigravity(existing_tools),    "Antigravity"),
    ]:
        _run_scraper(fn, label, sub_tools)

    return api_models, sub_tools


def _write_output(data: PricingData, output_path: Path) -> None:
    """pricing.json を書き込み、web フロントエンド用ディレクトリにもコピーする。"""
    # 浮動小数点アーティファクトを除去（例: 0.034999... → 0.035）
    for m in data.api_models:
        m.price_in = round(m.price_in, 6)
        m.price_out = round(m.price_out, 6)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = data.model_dump()

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logger.info("✓ pricing.json を書き込みました: %s", output_path)
    logger.info("  API モデル: %d件 / コーディングツール: %d件",
                len(data.api_models), len(data.sub_tools))
    logger.info("  USD/JPY: %.2f (as of %s)", data.jpy_rate, data.jpy_rate_date)

    web_data_path = (
        Path(__file__).parent.parent.parent.parent.parent
        / "web" / "src" / "data" / "pricing.json"
    )
    if web_data_path.parent.exists():
        with web_data_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        logger.info("  web/src/data/pricing.json にもコピー完了")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LLM-Studies Scraper")
    parser.add_argument("--output", type=Path, default=_DEFAULT_OUTPUT, help="出力先 JSON パス")
    parser.add_argument(
        "--no-scrape", action="store_true",
        help="スクレイピングをスキップ（既存値 or フォールバック値のみ）"
    )
    args = parser.parse_args(argv)

    output_path: Path = args.output.resolve()
    logger.info("出力先: %s", output_path)

    existing = _load_existing(output_path)
    jpy_rate, jpy_date = fetch_jpy_rate(fallback=existing.jpy_rate if existing else 155.0)

    if args.no_scrape and existing:
        logger.info("--no-scrape: 既存値を保持し為替レートのみ更新")
        api_models, sub_tools = existing.api_models, existing.sub_tools
    elif args.no_scrape:
        logger.warning("--no-scrape 指定だが既存ファイルなし → 通常スクレイピングを実行")
        api_models, sub_tools = _scrape_all(None, None)
    else:
        api_models, sub_tools = _scrape_all(
            existing.api_models if existing else None,
            existing.sub_tools if existing else None,
        )

    data = PricingData(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        jpy_rate=jpy_rate,
        jpy_rate_date=jpy_date,
        api_models=api_models,
        sub_tools=sub_tools,
    )
    _write_output(data, output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
