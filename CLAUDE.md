# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

AIモデルの時間別コスト計算機。Python スクレイパーが各社料金ページから価格を自動取得し `pricing.json` を生成、React フロントエンドがそれを読み込んで**単一ポータブル HTML** にビルドする。

## アーキテクチャ

```text
update.sh  ← オーケストレーター (スクレイプ → ビルド → コピー)
├── scraper/          Python 3.12+ (uv, Pydantic v2, Playwright, httpx)
│   └── src/scraper/
│       ├── main.py           CLI エントリポイント
│       ├── models.py         PricingData / ApiModel / SubTool スキーマ
│       ├── exchange.py       USD/JPY レート取得 (Frankfurter API)
│       ├── browser.py        Playwright 共通ユーティリティ
│       ├── providers/        API プロバイダー別スクレイパー (anthropic, openai, google, aws, deepseek, xai)
│       └── tools/            コーディングツール別スクレイパー (cursor, github_copilot, windsurf, claude_code, jetbrains, openai_codex, google_one, antigravity)
├── web/              React 19 + TypeScript + Vite 7 (bun)
│   └── src/
│       ├── App.tsx           メインコンポーネント (タブ切替・シナリオ選択)
│       ├── types/pricing.ts  JSON スキーマ型定義 (Python models.py と同期が必要)
│       ├── lib/cost.ts       コスト計算ロジック (calcApiCost / calcSubCost)
│       ├── i18n.ts           JA/EN 翻訳定義
│       ├── data/pricing.json ビルド時に埋め込まれる価格データ
│       └── components/       UI コンポーネント群
├── netlify.toml      Netlify デプロイ設定（スクレイパーなし、既存 pricing.json でビルドのみ）
├── common-header.js  共通ヘッダーDOM構築・注入スクリプト (ドロップダウンナビゲーション)
├── common-header.css 共通ヘッダー用スタイリング
├── claude/           Claude ドキュメント (skill.html / agent.html)
├── gemini/           Gemini ドキュメント (skill.html / agent.html)
├── codex/            Codex ドキュメント (skill.html / agent.html)
├── copilot/          Copilot ドキュメント (skill.html / agent.html)
```

## データフロー

1. `scraper/` が各社ページをスクレイプ → `pricing.json` を生成
2. スクレイパーは既存 `pricing.json` をフォールバック値として使用（3層: スクレイプ成功 → 既存値 → ハードコード値）
3. `web/` がビルド時に `src/data/pricing.json` を静的インポート
4. `vite-plugin-singlefile` で全アセットをインライン化 → 単一 `index.html` 出力
5. `update.sh` が `web/dist/index.html` と `pricing.json` をルートにコピー

**注意**: スクレイパーは `--output` 先に加えて `web/src/data/pricing.json` にも自動コピーする（二重書き込み）。`update.sh` は明示的に `--output web/src/data/pricing.json` を指定するため、実質同じファイルへの書き込みとなる。

## コマンド

### セットアップ

```bash
# スクレイパー
cd scraper && uv sync && uv run playwright install chromium

# フロントエンド
cd web && bun install
```

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
uv run scraper                              # pyproject.toml の scripts 経由でも起動可能
```

### フロントエンド

```bash
cd web
bun run dev        # Vite 開発サーバー (http://localhost:5173)
bun run build      # プロダクションビルド (tsc -b && vite build)
bun run lint       # ESLint
bun run preview    # ビルド結果プレビュー
```

### テスト

```bash
cd web && bun test           # フロントエンド (vitest)
cd scraper && uv run pytest  # バックエンド (pytest)
```

## 重要な設計判断

- **単一 HTML 出力**: `vite-plugin-singlefile` + `assetsInlineLimit: 100_000_000` で CSS/JS を全てインライン化。外部アセットなしで配布可能
- **3層フォールバック**: スクレイパーは「スクレイプ成功 → 既存 JSON の値 → ハードコードフォールバック」の順で価格を決定。`scrape_status` フィールド (`success` | `fallback` | `manual`) で出自を追跡
- **型の同期**: `scraper/src/scraper/models.py` (Pydantic) と `web/src/types/pricing.ts` (TypeScript) は同じスキーマを表現。**片方を変更したら必ずもう片方も更新すること**
- **JA/EN バイリンガル**: `i18n.ts` で全テキストを管理。各スクレイパーも `sub_ja` / `sub_en` や `note_ja` / `note_en` のペアで日英テキストを持つ
- **Netlify デプロイ**: `netlify.toml` でビルドのみ実行（スクレイパーは走らない）。リポジトリ内の既存 `pricing.json` をそのまま使用

## TypeScript 制約

- `strict: true` + `noUnusedLocals` + `noUnusedParameters`
- `erasableSyntaxOnly: true` — **enum と namespace は使用禁止**（TypeScript 5.5+ の制約）
- ESLint: `eslint.config.js` で `ts/tsx` に recommended + react-hooks + react-refresh を適用

## 新しいプロバイダー/ツールの追加パターン

1. `scraper/src/scraper/providers/<name>.py` (API) または `tools/<name>.py` (ツール) を作成
2. `_FALLBACKS` 辞書にハードコードフォールバック値を定義
3. `scrape(existing)` 関数を実装 → `list[ApiModel]` または `list[SubTool]` を返す
4. `providers/__init__.py` または `tools/__init__.py` にインポート追加
5. `main.py` の `_scrape_all()` にエントリ追加

## ランタイム要件

- Python 3.12+, uv (パッケージマネージャー)
- Playwright ブラウザ (`uv run playwright install chromium`)
- Bun (フロントエンドビルド)

## AI 変更ルール

このリポジトリは AI アシスト対象。全 AI エージェント (Jules, Claude, Copilot 等) は以下を厳守すること。

### 禁止事項

- ファイル全体の書き直し（明示的な指示がない限り）
- 依存関係のアップグレード
- CI ワークフロー構造の変更（明示的な指示がない限り。ただしユーザー指示による追加・修正は許容される。例: `.github/workflows/auto-fix.yml`）
- ビルドツール設定の変更 (vite, bun, pytest, tsconfig)
- ディレクトリのリネーム・ファイルの `web/` ↔ `scraper/` 間移動
- リポジトリ全体の自動フォーマット
- 新しいフレームワークの導入
- 環境変数・Netlify 設定の変更
- スタイル目的のリライト

### 許可される変更

- テスト追加（既存テストファイルがある場合、またはユーザー指示）
- import 修正
- CI 修正
- 小規模な型修正

### テストポリシー

許可: import スモークテスト、純粋関数テスト、決定論的コンポーネントレンダリングテスト

禁止: スナップショットテスト、ブラウザ自動化テスト、ネットワークテスト、重い結合テスト

### インポート安全性

モジュールの動的クロスディレクトリインポート禁止。`scraper/` → `scraper/` のみ、`web/` → `web/` のみ。

### CI 定義

```text
Frontend: bun run test
Backend:  pytest
Build:    cd web && bun run build
```

### コミット前チェック

以下を全て確認してからコミットすること：

1. `cd web && bun run build` が成功
2. `cd web && bun test` が成功
3. `cd scraper && uv run pytest` が成功
4. import が有効
5. 設定ファイルが意図せず変更されていない

いずれか失敗 → **停止してユーザーに確認**。

### CI 失敗時の対応

1. 失敗しているエラーのみ修正
2. リファクタリング禁止
3. 依存関係変更禁止
4. テスト書き直しは壊れている場合のみ

### パッチ戦略

small diff > medium diff > large diff — 常に最小の差分を選択。
