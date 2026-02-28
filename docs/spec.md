# spec.md — AI Model Cost Calculator 仕様書

> **目的**: プロジェクトの「何を」「なぜ」を定義する。全ての要件・設計・タスク文書の起点。
> **最終更新**: 2026-02-28

---

## 1. プロダクト概要

**AI Model Cost Calculator** は、主要 AI プロバイダーの API 料金とコーディングツールのサブスクリプション料金を**時間別コスト**で横断比較する Web アプリケーションである。

### 1.1 解決する課題

- AI モデルの料金体系はプロバイダーごとに異なり（トークン単価、月額、年額）、**同一基準での比較が困難**
- 公式料金ページは頻繁に更新されるが、**手動での追跡は非現実的**
- 日本のユーザーには **USD/JPY 換算**が不可欠だが、既存ツールは USD のみ対応が多い

### 1.2 ソリューション

1. **Python スクレイパー**が各社公式料金ページから自動で価格を取得
2. **React フロントエンド**がトークン使用量シナリオに基づき時間別コストを算出
3. **単一ポータブル HTML** として出力し、オフラインでも動作可能
4. **JA/EN バイリンガル**対応で国内外ユーザーをカバー

### 1.3 ターゲットユーザー

| ペルソナ | ニーズ |
| ---------- | -------- |
| AI エンジニア | API コスト見積もり、プロバイダー選定 |
| プロジェクトマネージャー | 月次/年次予算策定 |
| 個人開発者 | 低コストモデルの発見、ツール比較 |
| 技術評価担当 | 最新モデルの価格動向把握 |

---

## 2. スコープ

### 2.1 対応プロバイダー（API モデル）

| プロバイダー | モデル例 | スクレイパー |
| ------------- | ---------- | ------------- |
| Anthropic | Claude Opus 4.6, Sonnet 4.6, Haiku 4.5 | `providers/anthropic.py` |
| OpenAI | GPT-5.2, GPT-5, o3-pro, o4-mini | `providers/openai.py` |
| Google AI / Vertex AI | Gemini 3.1 Pro, 2.5 Pro/Flash | `providers/google.py` |
| AWS Bedrock | Amazon Nova Pro/Lite/Micro | `providers/aws.py` |
| DeepSeek | DeepSeek-V3.2, R1 | `providers/deepseek.py` |
| xAI | Grok 4, Grok 4.1 Fast | `providers/xai.py` |

### 2.2 対応ツール（サブスクリプション）

| ツール | プラン例 | スクレイパー |
| -------- | ---------- | ------------- |
| Cursor | Hobby, Pro, Business, Ultra | `tools/cursor.py` |
| GitHub Copilot | Free, Pro, Business, Enterprise | `tools/github_copilot.py` |
| Windsurf | Free, Pro, Team, Ultimate | `tools/windsurf.py` |
| Claude Code | Free, Pro, Max (5/20) | `tools/claude_code.py` |
| JetBrains AI | Free, All Products Pack | `tools/jetbrains.py` |
| OpenAI Codex | Plus, Pro, Team, Enterprise | `tools/openai_codex.py` |
| Google One AI | Free, Premium | `tools/google_one.py` |
| Antigravity | Free, Pro, Team, Enterprise | `tools/antigravity.py` |

### 2.3 対象外（現時点）

- 段階的課金 UI（>200K トークンでの単価変動）
- プロンプトキャッシュ率スライダー
- ストレージ維持費用計算（Gemini コンテキストキャッシング）
- グラウンディング費用（Google Search / Maps）
- 非トークン課金（RL ファインチューニング時間課金、動画生成秒数課金）
- Mistral AI / Perplexity / Cohere プロバイダー追加
- Batch API 割引計算

---

## 3. コア機能

### 3.1 価格データ自動取得

- Playwright ヘッドレスブラウザで JS レンダリング済みページを取得
- 正規表現で価格を抽出し、sanity check（0.001〜2000 USD）を適用
- **3 層フォールバック**: スクレイプ成功 → 既存 JSON → ハードコード値
- `scrape_status` フィールドで出自を追跡

### 3.2 為替レート取得

- Frankfurter API から最新 USD/JPY レートを取得
- フォールバック: 既存値 or 155.0

### 3.3 時間別コスト計算

- **API コスト**: `(input_tokens/1M × price_in + output_tokens/1M × price_out) × hours`
- **サブスク按分**: 時間按分（≤30d）/ 月数換算（30d〜12mo）/ 年払い優先（≥12mo）
- 7 期間: 1h / 8h / 24h / 7d / 30d / 4mo / 12mo

### 3.4 トークン使用量シナリオ

| シナリオ | Input | Output | 想定用途 |
| ---------- | ------- | -------- | ---------- |
| Light | 10K | 1K | 簡単な Q&A |
| Standard | 50K | 5K | コーディング支援 |
| Heavy | 200K | 20K | 大規模コード生成 |
| Custom | 任意 | 任意 | ユーザー定義 |

### 3.5 単一 HTML 出力

- `vite-plugin-singlefile` で全アセットをインライン化
- 外部依存なし、オフラインで動作
- Netlify でホスティング

### 3.6 共通ヘッダー・ナビゲーション

- `common-header.js` / `common-header.css` で全ページに共通ヘッダーを注入
- ドロップダウンナビゲーション（Claude / Gemini / Codex / Copilot）
- 免責事項バナー（2行レイアウト、レスポンシブ対応）
- `nav-links.json` による外部設定可能なリンク構造

### 3.7 ドキュメントサイト

各 AI ツールの SDD（Spec-Driven Development）ベストプラクティスガイドをホスティング:

| パス | 内容 |
| ------ | ------ |
| `/claude/skill.html` | Claude Code スキル・SDD ガイド |
| `/claude/agent.html` | Claude Code サブエージェント・Agent Teams ガイド |
| `/gemini/skill.html` | Gemini / Antigravity スキル・ルール・ワークフロー ガイド |
| `/gemini/agent.html` | Gemini サブエージェント・A2A プロトコル ガイド |
| `/codex/skill.html` | OpenAI Codex スキルガイド |
| `/codex/agent.html` | OpenAI Codex エージェントガイド |
| `/copilot/skill.html` | GitHub Copilot スキルガイド |
| `/copilot/agent.html` | GitHub Copilot エージェントガイド |

---

## 4. 技術スタック

| レイヤー | 技術 | バージョン |
| ---------- | ------ | ----------- |
| スクレイパー | Python + uv | 3.12+ |
| スキーマ | Pydantic v2 | 2.x |
| ブラウザ自動化 | Playwright | 最新 |
| HTTP クライアント | httpx | 最新 |
| フロントエンド | React + TypeScript | 19 / 5.5+ |
| ビルド | Vite + bun | 7 / 最新 |
| テスト (FE) | vitest + testing-library | 最新 |
| テスト (BE) | pytest | 9.0+ |
| デプロイ | Netlify | — |

---

## 5. 非機能要件サマリー

| 項目 | 要件 |
| ------ | ------ |
| パフォーマンス | ビルド済み HTML のロード < 2s（3G 回線） |
| 可用性 | 静的サイトのため Netlify CDN SLA に依存 |
| セキュリティ | XSS 対策（DOM メソッドのみ使用、innerHTML 禁止）、外部入力バリデーション |
| i18n | JA/EN 完全対応 |
| アクセシビリティ | ARIA ラベル、キーボードナビゲーション、Escape キー対応 |
| オフライン | 単一 HTML で完全動作 |
| データ鮮度 | 最大 1 週間以内の価格データ（手動 update.sh 実行） |

---

## 6. 参考情報

### 6.1 SDD 方法論

本プロジェクトは以下の SDD ベストプラクティスに基づいて運用される:

- **spec.md** → requirements.md → design.md → tasks.md の4文書体系
- CLAUDE.md / AGENTS.md による AI エージェント向けコンテキスト提供
- `/clear` 後のコンテキスト回復は tasks.md + design.md で実現

### 6.2 関連ドキュメント

| ファイル | 役割 |
| ---------- | ------ |
| `CLAUDE.md` | Claude Code 向けプロジェクト指示書 |
| `AGENTS.md` | AI エージェント向けガイドライン |
| `docs/ARCHITECTURE.md` | アーキテクチャリファレンス |
| `docs/TESTING.md` | テスト戦略・ガイドライン |
| `docs/requirements.md` | 詳細要件定義（FR/NFR） |
| `docs/design.md` | 技術設計ドキュメント |
| `docs/tasks.md` | 実装ロードマップ |
| `links.md` | 公式料金ページ参考リンク集 |
| `research.md` | 改善調査レポート |
