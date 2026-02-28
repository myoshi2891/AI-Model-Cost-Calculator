# requirements.md — 詳細要件定義

> **目的**: spec.md を機能要件（FR）と非機能要件（NFR）に分解し、受入基準を付与する。
> **最終更新**: 2026-02-28
> **優先度**: P0（必須）/ P1（重要）/ P2（改善）

---

## 機能要件（FR: Functional Requirements）

### FR-001: 価格データ自動取得 [P0]

**概要**: Python スクレイパーが各社公式料金ページから API モデル価格を自動取得する。

**受入基準**:

- [ ] 6 プロバイダー（Anthropic, OpenAI, Google AI, AWS, DeepSeek, xAI）の価格を取得できる
- [ ] 各モデルの input/output 価格（USD/1M tokens）を正しく抽出する
- [ ] 3 層フォールバック（スクレイプ成功 → 既存値 → ハードコード値）が動作する
- [ ] `scrape_status` フィールドで各値の出自を追跡する
- [ ] sanity check（0.001〜2000 USD）で異常値を排除する

**関連ファイル**: `scraper/src/scraper/providers/*.py`, `scraper/src/scraper/browser.py`

---

### FR-002: コーディングツール料金取得 [P0]

**概要**: コーディングツールのサブスクリプション料金を取得する。

**受入基準**:

- [ ] 8 ツール（Cursor, GitHub Copilot, Windsurf, Claude Code, JetBrains, Codex, Google One, Antigravity）の料金を取得できる
- [ ] 月額・年払い月換算の両方を取得する
- [ ] 無料プランは monthly=0, annual=null で表現する

**関連ファイル**: `scraper/src/scraper/tools/*.py`

---

### FR-003: 為替レート取得 [P0]

**概要**: Frankfurter API から最新の USD/JPY レートを取得する。

**受入基準**:

- [ ] API から当日または直近営業日のレートを取得する
- [ ] API 失敗時は既存値またはデフォルト値（155.0）にフォールバックする
- [ ] `jpy_rate_date` でレート取得日を記録する

**関連ファイル**: `scraper/src/scraper/exchange.py`

---

### FR-004: pricing.json 生成 [P0]

**概要**: スクレイプ結果を構造化 JSON として出力する。

**受入基準**:

- [ ] `PricingData` スキーマ（Pydantic v2）に準拠した JSON を生成する
- [ ] `--output` 指定先と `web/src/data/pricing.json` の二重書き込みを行う
- [ ] `generated_at`（YYYY-MM-DD）を含める
- [ ] `api_models` と `sub_tools` の両配列を含める

**関連ファイル**: `scraper/src/scraper/main.py`, `scraper/src/scraper/models.py`

---

### FR-005: 時間別コスト計算 [P0]

**概要**: トークン使用量とモデル単価から時間別コストを算出する。

**受入基準**:

- [ ] API コスト: `(input/1M × price_in + output/1M × price_out) × hours`
- [ ] サブスク按分: 時間按分（≤720h）/ 月数換算 / 年払い優先（≥8760h）
- [ ] 7 期間（1h, 8h, 24h, 7d, 30d, 4mo, 12mo）で計算する
- [ ] USD と JPY の両方で表示する
- [ ] 0 コストを正しくハンドリングする（無料プラン）

**関連ファイル**: `web/src/lib/cost.ts`

---

### FR-006: シナリオ選択 UI [P0]

**概要**: ユーザーがトークン使用量のプリセットを選択またはカスタム入力できる。

**受入基準**:

- [ ] Light / Standard / Heavy / Custom の 4 シナリオを提供する
- [ ] Custom 選択時に input/output トークン数を自由入力できる
- [ ] シナリオ変更で全テーブルが即座に再計算される

**関連ファイル**: `web/src/components/ScenarioSelector.tsx`

---

### FR-007: API モデル比較テーブル [P0]

**概要**: 全 API モデルを時間別コストで比較するテーブルを表示する。

**受入基準**:

- [ ] プロバイダー名、モデル名、タグ、単価を表示する
- [ ] 7 期間分のコストを USD + JPY のデュアル表示で表示する
- [ ] コスト帯に応じたカラーインデックスを適用する
- [ ] `scrape_status` による出自の視覚的区別（将来対応可）

**関連ファイル**: `web/src/components/ApiTable.tsx`, `web/src/components/DualCell.tsx`

---

### FR-008: サブスクリプション比較テーブル [P0]

**概要**: コーディングツールのサブスクリプション料金を比較する。

**受入基準**:

- [ ] ツール名、プラン名、月額/年額を表示する
- [ ] 時間按分コストを 7 期間分表示する
- [ ] 備考テキスト（note_ja / note_en）を表示する

**関連ファイル**: `web/src/components/SubTable.tsx`

---

### FR-009: JA/EN バイリンガル対応 [P0]

**概要**: 日本語と英語の切り替え機能を提供する。

**受入基準**:

- [ ] 全 UI テキストが JA/EN で用意されている
- [ ] 言語切替ボタンで即座に切り替わる
- [ ] スクレイパーの `sub_ja`/`sub_en`, `note_ja`/`note_en` が正しく表示される

**関連ファイル**: `web/src/i18n.ts`, `web/src/components/LanguageToggle.tsx`

---

### FR-010: 単一 HTML ビルド [P0]

**概要**: 全アセットをインライン化した単一 HTML ファイルを出力する。

**受入基準**:

- [ ] `vite-plugin-singlefile` で CSS/JS が全てインライン化される
- [ ] 外部リソース参照が一切ない
- [ ] オフライン環境で完全動作する
- [ ] `assetsInlineLimit: 100_000_000` が設定されている

**関連ファイル**: `web/vite.config.ts`

---

### FR-011: 共通ヘッダー・ナビゲーション [P1]

**概要**: 静的 HTML ページに共通ヘッダーを注入する。

**受入基準**:

- [ ] ブランドロゴ、ナビリンク、GitHub リンクを含むヘッダーを表示する
- [ ] Claude / Gemini / Codex / Copilot のドロップダウンメニューを提供する
- [ ] モバイルではハンバーガーメニューに切り替わる
- [ ] `nav-links.json` からリンク構造を外部設定できる
- [ ] `data-links` 属性によるフォールバック設定が動作する
- [ ] Escape キーでメニューが閉じる
- [ ] XSS 安全（DOM メソッドのみ使用、innerHTML 不使用）

**関連ファイル**: `common-header.js`, `common-header.css`

---

### FR-012: 免責事項バナー [P1]

**概要**: 全ページに免責事項を表示する。

**受入基準**:

- [ ] ヘッダー直下に固定表示される
- [ ] デスクトップ: 2 行に分割表示（改行位置: 「ご確認ください。」の後）
- [ ] タブレット（≤768px）: フォントサイズ縮小（0.7rem）
- [ ] スマホ（≤480px）: さらに縮小（0.65rem）、自然折り返し
- [ ] ResizeObserver で高さを動的に CSS 変数に反映する
- [ ] `body.has-common-header` の margin-top に高さが加算される

**関連ファイル**: `common-header.js`, `common-header.css`

---

### FR-013: ドキュメントサイト [P1]

**概要**: AI ツール別の SDD ベストプラクティスガイドをホスティングする。

**受入基準**:

- [ ] 4 ツール × 2 ページ（skill / agent）= 8 ページが公開されている
- [ ] 各ページが共通ヘッダーを使用している
- [ ] 参照リンク先が有効である

**関連ファイル**: `claude/*.html`, `gemini/*.html`, `codex/*.html`, `copilot/*.html`

---

### FR-014: 計算式解説セクション [P2]

**概要**: コスト計算の数式を解説するセクションを表示する。

**受入基準**:

- [ ] API コストとサブスク按分の計算式を JA/EN で表示する

**関連ファイル**: `web/src/components/MathSection.tsx`

---

### FR-015: 参照リンク集 [P2]

**概要**: 各社公式料金ページへのリンクを表示する。

**受入基準**:

- [ ] 各プロバイダーの公式料金ページ URL が最新である
- [ ] リンクが新しいタブで開く

**関連ファイル**: `web/src/components/RefLinks.tsx`, `links.md`

---

## 非機能要件（NFR: Non-Functional Requirements）

### NFR-001: パフォーマンス [P1]

- 単一 HTML ファイルサイズ < 2MB
- 初回ロード時間 < 2s（3G 回線想定）
- テーブル再計算は 16ms 以内（60fps 維持）

---

### NFR-002: セキュリティ [P0]

- DOM 操作は `document.createElement` + `textContent` のみ（innerHTML 禁止）
- 外部スクリプト読み込みなし（CSP 準拠）
- `nav-links.json` の href は `isSafeHref()` でプロトコル検証
- `javascript:` / `data:` / プロトコル相対 URL (`//`) を拒否

---

### NFR-003: アクセシビリティ [P1]

- ナビゲーションに `aria-label`, `aria-controls`, `aria-expanded` を付与
- アクティブページに `aria-current="page"` を付与
- キーボード操作（Tab / Escape）でメニュー操作可能

---

### NFR-004: レスポンシブデザイン [P1]

- デスクトップ（>768px）: 横並びナビゲーション
- タブレット / スマホ（≤768px）: ハンバーガーメニュー
- 免責事項バナーのフォントサイズが段階的に縮小

---

### NFR-005: 型安全性 [P0]

- TypeScript: `strict: true`, `noUnusedLocals`, `noUnusedParameters`
- `erasableSyntaxOnly: true`（enum / namespace 禁止）
- Python: Pydantic v2 でスキーマ定義、型ヒント必須
- `models.py` と `pricing.ts` の型同期を維持

---

### NFR-006: データ鮮度 [P1]

- 価格データは `update.sh` 実行で更新（目標: 週次）
- 為替レートは Frankfurter API の最新値を使用
- `generated_at` で生成日時を記録

---

### NFR-007: テスタビリティ [P1]

- フロントエンド: vitest + @testing-library/react
- バックエンド: pytest
- 外部通信はモック必須（E2E スクレイプテスト禁止）
- AAA パターン（Arrange-Act-Assert）に準拠
- 詳細は `docs/TESTING.md` を参照

---

### NFR-008: デプロイ [P1]

- Netlify で自動デプロイ（`bun run build` のみ、スクレイパー不実行）
- リポジトリの既存 `pricing.json` をそのまま使用
- `update.sh` でローカルから手動更新 → push → 自動デプロイ

---

## 将来要件（Backlog）

> research.md の調査結果に基づく。優先度は未定。

| ID | 概要 | 出典 |
| ---- | ------ | ------ |
| FR-B01 | 段階的課金 UI（>200K トークンでの単価変動） | research.md §2 |
| FR-B02 | プロンプトキャッシュ率スライダー | research.md §2, §4 |
| FR-B03 | ストレージ維持費計算（Gemini コンテキストキャッシング） | research.md §3 |
| FR-B04 | グラウンディング費用加算（Google Search / Maps） | research.md §3 |
| FR-B05 | Mistral AI プロバイダー追加 | research.md §5 |
| FR-B06 | Perplexity プロバイダー追加（検索深度別基本手数料） | research.md §6 |
| FR-B07 | Batch API 割引計算（OpenAI / Anthropic 50% OFF） | research.md §7 |
| FR-B08 | 非トークン課金対応（RL ファインチューニング時間課金） | research.md §1 |
