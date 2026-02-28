# AGENTS.md

AI コーディングエージェント向けのプロジェクト仕様書。

## プロジェクト概要

AI モデルの時間別コスト計算機。Python スクレイパーが各社料金ページから価格を自動取得し `pricing.json` を生成、React フロントエンドがそれを読み込んで**単一ポータブル HTML** にビルドする。

## アーキテクチャ

```text
update.sh                ← オーケストレーター (スクレイプ → ビルド → コピー)
├── scraper/             Python 3.12+ (uv, Pydantic v2, Playwright, httpx)
│   └── src/scraper/
│       ├── main.py              CLI エントリポイント
│       ├── models.py            PricingData / ApiModel / SubTool スキーマ
│       ├── exchange.py          USD/JPY レート取得 (Frankfurter API)
│       ├── browser.py           Playwright 共通ユーティリティ
│       ├── providers/           API プロバイダー別スクレイパー
│       │   ├── anthropic.py
│       │   ├── openai.py
│       │   ├── google.py
│       │   ├── aws.py
│       │   ├── deepseek.py
│       │   └── xai.py
│       └── tools/               コーディングツール別スクレイパー
│           ├── cursor.py
│           ├── github_copilot.py
│           ├── windsurf.py
│           ├── claude_code.py
│           ├── jetbrains.py
│           ├── openai_codex.py
│           ├── google_one.py
│           └── antigravity.py
├── web/                 React 19 + TypeScript + Vite 7 (bun)
│   └── src/
│       ├── App.tsx              メインコンポーネント (タブ切替・シナリオ選択)
│       ├── main.tsx             React エントリポイント
│       ├── types/pricing.ts     JSON スキーマ型定義 (models.py と同期必須)
│       ├── lib/cost.ts          コスト計算ロジック (calcApiCost / calcSubCost)
│       ├── i18n.ts              JA/EN 翻訳定義
│       ├── data/pricing.json    ビルド時に埋め込まれる価格データ
│       └── components/
│           ├── ApiTable.tsx      API モデル比較テーブル
│           ├── SubTable.tsx      サブスクリプションツール比較テーブル
│           ├── Hero.tsx          ヒーローセクション
│           ├── ScenarioSelector.tsx  利用シナリオ選択 UI
│           ├── DualCell.tsx      USD/JPY 二段表示セル
│           ├── MathSection.tsx   計算式表示セクション
│           ├── LanguageToggle.tsx  言語切替
│           └── RefLinks.tsx      参照リンク
├── netlify.toml         Netlify デプロイ設定 (ビルドのみ、スクレイパーなし)
├── common-header.js     共通ヘッダー DOM 構築・注入スクリプト (ドロップダウンナビゲーション)
├── common-header.css    共通ヘッダー用スタイリング
├── claude/              Claude ドキュメント (skill.html / agent.html)
├── gemini/              Gemini ドキュメント (skill.html / agent.html)
├── codex/               Codex ドキュメント (skill.html / agent.html)
├── copilot/             Copilot ドキュメント (skill.html / agent.html)
```

## データフロー

1. `scraper/` が各社ページをスクレイプ → `pricing.json` を生成
2. スクレイパーは既存 `pricing.json` をフォールバック値として使用
   - 3 層フォールバック: **スクレイプ成功 → 既存値 → ハードコード値**
   - `scrape_status` フィールド (`success` | `fallback` | `manual`) で出自を追跡
3. `web/` がビルド時に `src/data/pricing.json` を静的インポート
4. `vite-plugin-singlefile` で全アセットをインライン化 → 単一 `index.html` 出力
5. `update.sh` が `web/dist/index.html` と `pricing.json` をルートにコピー

> **注意**: スクレイパーは `--output` 先に加え `web/src/data/pricing.json` にも自動コピーする（二重書き込み）。

## セットアップ

```bash
# スクレイパー
cd scraper && uv sync && uv run playwright install chromium

# フロントエンド
cd web && bun install
```

## コマンド

### 全体更新

```bash
bash update.sh              # フルパイプライン (スクレイプ → ビルド → コピー)
bash update.sh --no-scrape  # 為替レートのみ更新、既存価格データ保持
```

### スクレイパー単体

```bash
cd scraper
uv run python -m scraper.main --output ../pricing.json
uv run python -m scraper.main --no-scrape   # 為替レートのみ
uv run scraper                               # pyproject.toml scripts 経由
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

フロントエンド（vitest）およびバックエンド（pytest）ともに基本的なスモークテストが実装されています。
CI（`.github/workflows/test.yaml`）で自動化されています。

## ランタイム要件

- Python 3.12+
- uv (Python パッケージマネージャー)
- Playwright ブラウザ (`uv run playwright install chromium`)
- Bun (フロントエンドビルド)
- Node.js 22+ (CI 環境)

## 重要な設計判断

### 単一 HTML 出力

`vite-plugin-singlefile` + `assetsInlineLimit: 100_000_000` で CSS/JS を全てインライン化。外部アセットなしで配布可能。

### 型の同期

`scraper/src/scraper/models.py` (Pydantic) と `web/src/types/pricing.ts` (TypeScript) は同じスキーマを表現する。**片方を変更したら必ずもう片方も更新すること。**

### JA/EN バイリンガル

`i18n.ts` で全テキストを管理。各スクレイパーも `sub_ja` / `sub_en` や `note_ja` / `note_en` のペアで日英テキストを持つ。

### Netlify デプロイ

`netlify.toml` でビルドのみ実行（スクレイパーは走らない）。リポジトリ内の既存 `pricing.json` をそのまま使用。

## コーディング規約

### TypeScript

- `strict: true` + `noUnusedLocals` + `noUnusedParameters`
- `erasableSyntaxOnly: true` — **`enum` と `namespace` は使用禁止**
- ESLint: recommended + react-hooks + react-refresh

### Python

- Pydantic v2 でスキーマ定義
- 型ヒント必須 (Python 3.12+ の `|` 記法を使用)
- `from __future__ import annotations` を各ファイル先頭に配置

### 共通

- `any` 禁止 → `unknown` + 型ガード (TypeScript)
- 早期リターンでネスト削減
- エラーを握りつぶさない
- 秘密情報をハードコードしない

## 新しいプロバイダー/ツールの追加パターン

1. `scraper/src/scraper/providers/<name>.py` (API) または `tools/<name>.py` (ツール) を作成
2. `_FALLBACKS` 辞書にハードコードフォールバック値を定義
3. `scrape(existing)` 関数を実装 → `list[ApiModel]` または `list[SubTool]` を返す
4. `providers/__init__.py` または `tools/__init__.py` にインポート追加
5. `main.py` の `_scrape_all()` にエントリ追加

## サブエージェント設計パターン

> Claude Code のサブエージェント機能（[公式ドキュメント](https://code.claude.com/docs/en/sub-agents)）に基づく推奨パターン。

### ルーティング判断フロー

```text
タスク 3 件以上？
→ NO → メインエージェントが直接処理
→ YES → 依存関係あり？
   → YES → 順次実行（チェーン）
   → NO → 共有状態あり？
      → YES → 順次実行
      → NO → 境界が明確？
         → YES → 並列実行
         → NO → スコープを明確化してから分割
```

### 推奨サブエージェント構成

| 名前 | モデル | ツール | 用途 |
|------|--------|--------|------|
| Explore | haiku | Read, Glob, Grep | コードベース探索（高速・低コスト） |
| Plan | inherit | Read, Glob, Grep | 実装計画策定（読み取り専用） |
| Code Reviewer | sonnet | Read, Glob, Grep, Bash | コードレビュー（バランス） |
| Debugger | inherit | Read, Edit, Bash, Grep, Glob | バグ修正・根本原因分析 |

### ベストプラクティス

- **description に具体的なトリガー条件を記述**: 「いつ使う」を明確に
- **ツールは最小限に制限**: 読み取り専用エージェントには Edit/Write を付与しない
- **コスト最適化**: 探索系は haiku、分析系は sonnet、複雑な推論は opus
- **メモリスコープ**: `user`（全プロジェクト共通）/ `project`（プロジェクト固有）/ `local`（個人用）

## マルチエージェント連携

> Gemini ADK のマルチエージェントパターン（[公式ドキュメント](https://google.github.io/adk-docs/agents/multi-agents/)）に基づく。

### エージェント間通信パターン

| パターン | 方式 | 用途 |
|----------|------|------|
| Sequential Pipeline | 共有状態（output_key） | 仕様→実装→レビューの段階的処理 |
| Parallel Fan-Out | 独立 output_key | 独立した調査・分析の並列実行 |
| Coordinator/Dispatcher | LLM ルーティング | 中央エージェントが専門エージェントに動的委譲 |
| Review/Critique Loop | LoopAgent | 生成→検証→改善の反復 |

### クロスツール互換（AGENTS.md の位置づけ）

本ファイル（AGENTS.md）は複数 AI ツール間の共通エントリポイントとして機能する:

| ツール | 一次ファイル | 二次ファイル |
|--------|-------------|-------------|
| Claude Code | CLAUDE.md | AGENTS.md（読み取り） |
| Gemini CLI | GEMINI.md | AGENTS.md |
| Android Studio (Gemini) | AGENTS.md | — |
| Cursor | .cursorrules | AGENTS.md |

ツール固有の設定は各一次ファイルに記述し、AGENTS.md には横断的な情報のみを含める。

### A2A プロトコル（参考）

Google A2A（Agent-to-Agent）プロトコルは、異なるフレームワークのエージェント間通信を標準化する:

- **Agent Card** (`agent.json`): エージェントの能力を公開する JSON マニフェスト
- **RemoteA2aAgent**: リモートエージェントを ADK サブエージェントとして統合
- **to_a2a()**: 既存 ADK エージェントを A2A エンドポイントとして公開

詳細: [A2A ドキュメント](https://google.github.io/adk-docs/a2a/)

## SDD 仕様書体系

Spec-Driven Development に基づく文書管理（詳細は `docs/` 配下を参照）:

| ファイル | 役割 | AI エージェントの用途 |
|----------|------|---------------------|
| `docs/spec.md` | 何を・なぜ | プロジェクト全体像の理解 |
| `docs/requirements.md` | FR/NFR 要件定義 | 受入基準の確認 |
| `docs/design.md` | 設計判断と根拠 | 実装方針の理解 |
| `docs/tasks.md` | 実装ロードマップ | `/clear` 後のコンテキスト回復 |
| `docs/ARCHITECTURE.md` | 構造の事実 | ファイル配置・データフロー |
| `docs/TESTING.md` | テスト戦略 | テスト追加時のガイドライン |

## Git 規約

- コミットメッセージ形式: `<type>(<scope>): <subject>`
- type: `feat` | `fix` | `docs` | `refactor` | `test` | `chore`
- コミット前に型・リントエラーがないことを確認
- `.env` をコミット対象にしない
