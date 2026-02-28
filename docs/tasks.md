# tasks.md — 実装ロードマップ

> **目的**: design.md の設計を独立してテスト可能なタスクに分解する。`/clear` 後のコンテキスト回復にも使用。
> **最終更新**: 2026-02-28

---

## 完了済みタスク

### Phase 0: データ修正（2026-02-28 完了）

- [x] **T-001**: Google AI 破損価格修正（Flash $35.0 → $0.30 等）
  - 関連: FR-001, `providers/google.py`, `pricing.json`
- [x] **T-002**: AWS Bedrock multiplier バグ修正（"1,000" / "per 1000" 対応）
  - 関連: FR-001, `providers/aws.py`
- [x] **T-003**: DeepSeek V3.2 統合価格更新（$0.28/$0.42）
  - 関連: FR-001, `providers/deepseek.py`
- [x] **T-004**: GPT-5.2 / GPT-5.2 pro モデル追加
  - 関連: FR-001, `providers/openai.py`
- [x] **T-005**: Grok 4 Fast → Grok 4.1 Fast リネーム
  - 関連: FR-001, `providers/xai.py`
- [x] **T-006**: USD/JPY レート更新（155.98, 2026-02-27）
  - 関連: FR-003, `exchange.py`
- [x] **T-007**: root pricing.json の git 追跡解除
  - 関連: NFR-008
- [x] **T-008**: GPT-4.1 / Gemini 3.1 Pro を一次ソースに基づきリバート
  - 関連: FR-001

### Phase 0.5: 共通ヘッダー改善（2026-02-28 完了）

- [x] **T-009**: 免責事項バナー追加
  - 関連: FR-012, `common-header.js`, `common-header.css`
- [x] **T-010**: ResizeObserver で免責事項バナー高さ追従
  - 関連: FR-012
- [x] **T-011**: 免責事項 2 行レイアウト + レスポンシブ対応
  - 関連: FR-012

### Phase 0.6: 仕様書整備（2026-02-28 完了）

- [x] **T-012**: SDD 仕様書体系の作成（spec.md / requirements.md / design.md / tasks.md）
  - 関連: spec.md §6.1
- [x] **T-013**: ARCHITECTURE.md の共通ヘッダー情報追加
  - 関連: FR-011, FR-012
- [x] **T-014**: AGENTS.md のサブエージェント・マルチエージェントパターン追加
  - 関連: design.md §7

---

## 未着手タスク

### Phase 1: 価格データ拡充 [P1]

- [ ] **T-101**: Mistral AI プロバイダー追加
  - 関連: FR-B05, research.md §5
  - 依存: なし
  - 受入基準: `providers/mistral.py` 作成、3 層フォールバック動作、pricing.json に反映
  - モデル: Mistral Large 3, Medium 3, Small 4

- [ ] **T-102**: Perplexity プロバイダー追加
  - 関連: FR-B06, research.md §6
  - 依存: なし
  - 受入基準: `providers/perplexity.py` 作成、検索深度別基本手数料の計算ロジック
  - 注意: トークン単価 + リクエスト手数料の複合課金

- [ ] **T-103**: Gemini 2.0 Flash / Robotics-ER 追加
  - 関連: FR-001, research.md §3
  - 依存: なし

- [ ] **T-104**: Gemini 3.1 Pro Preview → Flagship 昇格時の更新
  - 関連: FR-001
  - 依存: Google 公式ページの更新を待つ
  - 注意: 現在は "Preview" が公式名称

---

### Phase 2: 計算機能強化 [P1]

- [ ] **T-201**: 段階的課金 UI（>200K トークンでの単価変動）
  - 関連: FR-B01, research.md §2
  - 依存: T-204（UI コンポーネント設計）
  - 受入基準: Anthropic Claude 4.6 の 200K 超入力/出力単価倍増を計算に反映
  - 影響ファイル: `lib/cost.ts`, `types/pricing.ts`, `models.py`, `ApiTable.tsx`

- [ ] **T-202**: プロンプトキャッシュ率スライダー
  - 関連: FR-B02, research.md §2, §4
  - 依存: T-201
  - 受入基準: キャッシュヒット率（0-100%）入力で Write/Read 単価を加重平均

- [ ] **T-203**: Batch API 割引計算
  - 関連: FR-B07, research.md §7
  - 依存: なし
  - 受入基準: Batch API チェックボックスで 50% 割引適用

- [ ] **T-204**: pricing.ts / models.py に段階的課金フィールド追加
  - 関連: NFR-005
  - 依存: なし（Phase 2 の前提タスク）
  - 受入基準: `price_in_high`, `price_out_high`, `threshold_tokens` フィールド追加
  - 注意: 型同期必須（Pydantic ↔ TypeScript）

---

### Phase 3: ストレージ・付加料金 [P2]

- [ ] **T-301**: Gemini コンテキストキャッシング維持費計算
  - 関連: FR-B03, research.md §3
  - 依存: T-204
  - 受入基準: 時間 × トークン数 × 維持単価で算出

- [ ] **T-302**: Google Search/Maps グラウンディング費用
  - 関連: FR-B04, research.md §3
  - 依存: なし
  - 受入基準: 1,000 リクエストあたりの固定料金を加算

- [ ] **T-303**: 非トークン課金対応（RL ファインチューニング時間課金）
  - 関連: FR-B08, research.md §1
  - 依存: 大規模 UI 変更が必要
  - 注意: 計算モデルが根本的に異なるため、別タブまたは別セクションが必要

---

### Phase 4: テスト強化 [P1]

- [ ] **T-401**: コスト計算ロジックのユニットテスト追加
  - 関連: NFR-007, TESTING.md §推奨テストパターン
  - 依存: なし
  - 受入基準: `calcApiCost`, `calcSubCost`, `fmtUSD`, `fmtJPY` の正常系・異常系テスト
  - ファイル: `web/src/lib/cost.test.ts`

- [ ] **T-402**: Pydantic モデルバリデーションテスト追加
  - 関連: NFR-007
  - 依存: なし
  - 受入基準: `ApiModel`, `SubTool`, `PricingData` の正常値・異常値テスト
  - ファイル: `scraper/tests/test_models.py`

- [ ] **T-403**: 価格抽出ロジックテスト追加
  - 関連: NFR-007
  - 依存: なし
  - 受入基準: `extract_price`, `sanity_check` のパターンマッチテスト
  - ファイル: `scraper/tests/test_browser.py`

- [ ] **T-404**: 為替レート取得テスト追加（httpx モック）
  - 関連: NFR-007
  - 依存: なし
  - 受入基準: 成功時とフォールバック時の両方をテスト
  - ファイル: `scraper/tests/test_exchange.py`

---

### Phase 5: CI/CD 改善 [P2]

- [ ] **T-501**: GitHub Actions でスクレイプ自動化
  - 関連: NFR-006, NFR-008
  - 依存: T-401〜T-404（テスト整備後）
  - 受入基準: 週次スケジュールで `update.sh` を実行し、auto-commit + push
  - 注意: Playwright ブラウザインストール、secrets 管理が必要

- [ ] **T-502**: web-test の `|| true` 除去
  - 関連: NFR-007
  - 依存: T-401（テスト安定化後）
  - 受入基準: `bun test` が strict mode で CI をブロックする

---

## 依存関係グラフ

```text
T-204 (型拡張)
  ├── T-201 (段階的課金 UI)
  │   └── T-202 (キャッシュ率スライダー)
  └── T-301 (キャッシング維持費)

T-401〜T-404 (テスト強化)
  ├── T-501 (CI 自動化)
  └── T-502 (strict テスト)
```
