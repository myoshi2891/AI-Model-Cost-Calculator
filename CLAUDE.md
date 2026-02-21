# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

AIモデルの時間別コスト計算機。Python スクレイパーが各社料金ページから価格を自動取得し `pricing.json` を生成、React フロントエンドがそれを読み込んで**単一ポータブル HTML** にビルドする。

## アーキテクチャ

```text
update.sh  ← オーケストレーター (スクレイプ → ビルド → コピー)
├── scraper/          Python (uv, Pydantic v2, Playwright, httpx)
│   └── src/scraper/
│       ├── main.py           CLI エントリポイント (python -m scraper.main)
│       ├── models.py         PricingData / ApiModel / SubTool スキーマ
│       ├── exchange.py       USD/JPY レート取得 (Frankfurter API)
│       ├── browser.py        Playwright 共通ユーティリティ (get_page_text / extract_price / sanity_check)
│       ├── providers/        API プロバイダー別スクレイパー (anthropic, openai, google, aws, deepseek, xai)
│       └── tools/            コーディングツール別スクレイパー (cursor, github_copilot, windsurf, claude_code 等)
├── web/              React 19 + TypeScript + Vite 7 (bun)
│   └── src/
│       ├── App.tsx           メインコンポーネント (タブ切替・シナリオ選択)
│       ├── types/pricing.ts  JSON スキーマ型定義 (Python models.py と同期が必要)
│       ├── lib/cost.ts       コスト計算ロジック (calcApiCost / calcSubCost)
│       ├── i18n.ts           JA/EN 翻訳定義
│       ├── data/pricing.json ビルド時に埋め込まれる価格データ
│       └── components/       UI コンポーネント群
├── common-header.js  共通ヘッダーDOM構築・注入スクリプト (全HTMLで動的読み込み)
├── common-header.css 共通ヘッダー用スタイリング
└── *_spec.html       各ツール向け静的仕様書ファイル群 (claude, codex, gemini, copilot)
```

## データフロー

1. `scraper/` が各社ページをスクレイプ → `pricing.json` を生成
2. スクレイパーは既存 `pricing.json` をフォールバック値として使用（3層: スクレイプ成功 → 既存値 → ハードコード値）
3. `web/` がビルド時に `src/data/pricing.json` を静的インポート
4. `vite-plugin-singlefile` で全アセットをインライン化 → 単一 `index.html` 出力
5. `update.sh` が `web/dist/index.html` をルートにコピー

## コマンド

### 全体更新（スクレイプ → ビルド → コピー）

```bash
bash update.sh              # フルパイプライン
bash update.sh --no-scrape  # 為替レートのみ更新、既存価格データ保持
```

### スクレイパー単体

```bash
cd scraper
uv run python -m scraper.main --output ../pricing.json
uv run python -m scraper.main --no-scrape  # 為替レートのみ
```

### フロントエンド

```bash
cd web
bun install        # 依存インストール
bun run dev        # Vite 開発サーバー
bun run build      # プロダクションビルド (tsc -b && vite build)
bun run lint       # ESLint
bun run preview    # ビルド結果プレビュー
```

## 重要な設計判断

- **単一 HTML 出力**: `vite-plugin-singlefile` で CSS/JS を全てインライン化。外部アセットなしで配布可能
- **3層フォールバック**: スクレイパーは「スクレイプ成功 → 既存 JSON の値 → ハードコードフォールバック」の順で価格を決定。`scrape_status` フィールド (`success` | `fallback` | `manual`) で出自を追跡
- **型の同期**: `scraper/src/scraper/models.py` (Pydantic) と `web/src/types/pricing.ts` (TypeScript) は同じスキーマを表現。片方を変更したら必ずもう片方も更新すること
- **JA/EN バイリンガル**: `i18n.ts` で全テキストを管理。各スクレイパーも `sub_ja` / `sub_en` や `note_ja` / `note_en` のペアで日英テキストを持つ

## 新しいプロバイダー/ツールの追加パターン

1. `scraper/src/scraper/providers/<name>.py` (API) または `tools/<name>.py` (ツール) を作成
2. `_FALLBACKS` 辞書にハードコードフォールバック値を定義
3. `scrape()` 関数を実装（`existing` 引数でフォールバック対応）
4. `providers/__init__.py` または `tools/__init__.py` にインポート追加
5. `main.py` の `_scrape_all()` にエントリ追加

## ランタイム要件

- Python 3.12+, uv (パッケージマネージャー)
- Playwright ブラウザ (`playwright install chromium`)
- Bun (フロントエンドビルド)
