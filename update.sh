#!/bin/bash
# AI Model Pricing 日次更新スクリプト
# 使い方: bash update.sh [--no-scrape]
#   --no-scrape: スクレイピングをスキップし、既存データの為替レートのみ更新
set -euo pipefail
cd "$(dirname "$0")"

SCRIPT_DIR="$(pwd)"
SCRAPER_DIR="${SCRIPT_DIR}/scraper"
WEB_DIR="${SCRIPT_DIR}/web"
DATA_JSON="${WEB_DIR}/src/data/pricing.json"
OUTPUT_HTML="${SCRIPT_DIR}/index.html"
OUTPUT_JSON="${SCRIPT_DIR}/pricing.json"

# uv / bun のパスを補完（CI・cron 環境向け）
export PATH="${HOME}/.local/bin:${HOME}/.bun/bin:${PATH}"

# ── 引数処理 ──────────────────────────────────────────────
NO_SCRAPE=""
for arg in "$@"; do
  [[ "${arg}" == "--no-scrape" ]] && NO_SCRAPE="--no-scrape"
done

echo "=== AI Model Pricing Updater ==="
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ── 1/3 スクレイピング ────────────────────────────────────
echo ">>> [1/3] 価格スクレイピング${NO_SCRAPE:+ (スキップ)}"
uv run --project "${SCRAPER_DIR}" python -m scraper.main \
  --output "${DATA_JSON}" \
  ${NO_SCRAPE}
echo "✓ pricing.json 更新完了: ${DATA_JSON}"
echo ""

# ── 2/3 フロントエンドビルド ──────────────────────────────
echo ">>> [2/3] フロントエンドビルド"
(cd "${WEB_DIR}" && bun run build)
echo "✓ ビルド完了: ${WEB_DIR}/dist/index.html"
echo ""

# ── 3/3 成果物コピー ──────────────────────────────────────
echo ">>> [3/3] 成果物コピー"
cp "${WEB_DIR}/dist/index.html" "${OUTPUT_HTML}"
cp "${DATA_JSON}" "${OUTPUT_JSON}"
echo "✓ ${OUTPUT_HTML}"
echo "✓ ${OUTPUT_JSON}"
echo ""

echo "=== 完了 ==="
echo "  index.html : $(wc -c < "${OUTPUT_HTML}") bytes"
echo "  JPY rate   : $(python3 -c "import json; d=json.load(open('${OUTPUT_JSON}')); print(f\"{d['jpy_rate']:.2f} ({d['jpy_rate_date']})\")" 2>/dev/null || echo '(確認できません)')"
