# Testing

> テスト戦略・実行方法・テスト追加ガイドライン。

## 現状のテスト体制

| 領域 | フレームワーク | 状態 | コマンド |
| ------ | --------------- | ------ | ---------- |
| フロントエンド (web/) | vitest + @testing-library/react | 基本スモークテストあり | `cd web && bun test` |
| スクレイパー (scraper/) | pytest | 基本スモークテストあり | `cd scraper && uv run pytest` |

## テスト実行

### フロントエンド

```bash
cd web
bun test           # vitest 実行 (watch モード)
bun test --run     # 単発実行 (CI 用)
```

**設定ファイル:**

- テストランナー: `vitest` (package.json の `"test": "vitest"`)
- DOM 環境: `jsdom` (vitest.config 経由 or vite.config.ts のtest設定)
- セットアップ: `src/setupTests.ts` (`@testing-library/jest-dom` のマッチャー拡張)
- tsconfig: テストファイルは `tsconfig.app.json` の `exclude` に指定 (`**/*.test.ts`, `**/*.test.tsx`)

**既存テスト:**

```text
web/src/App.test.tsx
  - App コンポーネントの基本レンダリングテスト
  - "AI Cost Simulator" テキストの存在確認
  - "USD + JPY" テキストの存在確認
web/tests/smoke/smoke.test.tsx
  - ヘッダー注入スクリプトなど、ビルド成果物の基本的な動作確認
```

### スクレイパー

```bash
cd scraper
uv run pytest              # 全テスト実行
uv run pytest -v           # 詳細出力
uv run pytest -k "test_"   # パターンマッチ
```

**設定:**

- `pyproject.toml` の `[dependency-groups]` dev に `pytest>=9.0.2`
- 単純なインポート検証 (`test_imports.py`) および基本的なスモークテスト (`tests/smoke/`) が設定されています。

## CI での実行

GitHub Actions (`.github/workflows/test.yaml`) で自動実行:

```text
push / pull_request
  ├── web/** 変更時   → bun test || true  (失敗を許容)
  └── scraper/** 変更時 → uv run pytest    (strict)
```

**注意:** web-test は `|| true` で失敗を許容している。将来テストが安定したら外すべき。

## テスト追加ガイドライン

### フロントエンド (`web/`)

#### ファイル命名規則

```text
src/<name>.test.tsx    # コンポーネントテスト
src/lib/<name>.test.ts # ユーティリティテスト
```

#### 推奨テストパターン

**1. コスト計算ロジック (`lib/cost.ts`)** — 最優先

```typescript
// src/lib/cost.test.ts
import { calcApiCost, calcSubCost, colorIndex, fmtUSD, fmtJPY } from './cost'

describe('calcApiCost', () => {
  it('1時間のコストを正しく計算する', () => {
    // Arrange
    const priceIn = 3.0   // $3/1M input tokens
    const priceOut = 15.0  // $15/1M output tokens
    const input = 50_000
    const output = 5_000

    // Act
    const cost = calcApiCost(priceIn, priceOut, input, output, 1)

    // Assert: (50000/1M * 3 + 5000/1M * 15) * 1 = 0.225
    expect(cost).toBeCloseTo(0.225)
  })

  it('0時間は0を返す', () => {
    expect(calcApiCost(3.0, 15.0, 50000, 5000, 0)).toBe(0)
  })
})

describe('calcSubCost', () => {
  it('30日以下は時間按分', () => {
    expect(calcSubCost(20, 16, 720)).toBe(20)      // 30日 = 月額そのまま
    expect(calcSubCost(20, 16, 360)).toBeCloseTo(10) // 15日 = 半額
  })

  it('12ヶ月は年払い優先', () => {
    expect(calcSubCost(20, 16, 8760)).toBe(16) // annual が使われる
  })

  it('annual=null の場合は月額換算', () => {
    expect(calcSubCost(20, null, 8760)).toBeCloseTo(20 * 12.166, 0)
  })

  it('無料プランは常に0', () => {
    expect(calcSubCost(0, null, 8760)).toBe(0)
  })
})

describe('fmtUSD', () => {
  it('通常のフォーマット', () => {
    expect(fmtUSD(1234.56)).toBe('$1,234.56')
  })

  it('極小値は <$0.01', () => {
    expect(fmtUSD(0.001)).toBe('<$0.01')
  })

  it('0は $0.00', () => {
    expect(fmtUSD(0)).toBe('$0.00')
  })
})
```

## **2. コンポーネントテスト**

```typescript
// src/components/ScenarioSelector.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { ScenarioSelector } from './ScenarioSelector'

describe('ScenarioSelector', () => {
  it('シナリオ変更でコールバックが呼ばれる', () => {
    const onChange = vi.fn()
    render(
      <ScenarioSelector
        lang="ja"
        scenario="standard"
        currentInput={50000}
        currentOutput={5000}
        onScenarioChange={onChange}
      />
    )
    // シナリオボタンをクリックしてコールバック検証
  })
})
```

### vitest の注意点

- `vi.fn()` でモック関数を作成（jest.fn() ではない）
- `vi.mock()` でモジュールモック
- `@testing-library/jest-dom` のマッチャー (`toBeInTheDocument` 等) は `setupTests.ts` で自動読み込み

### スクレイパー (`scraper/`)

#### ファイル配置

```text
scraper/
├── tests/
│   ├── __init__.py
│   ├── test_models.py      # Pydantic モデルのバリデーション
│   ├── test_exchange.py     # 為替レート取得 (モック)
│   ├── test_browser.py      # 価格抽出ロジック
│   └── test_main.py         # CLI エントリポイント
```

#### 推奨テストパターン2

**1. モデルバリデーション** — 最優先

```python
# tests/test_models.py
import pytest
from pydantic import ValidationError
from scraper.models import ApiModel, SubTool, PricingData

class TestApiModel:
    def test_valid_model(self):
        """正常な ApiModel を生成できる"""
        m = ApiModel(
            provider="TestProvider",
            name="Test Model",
            tag="Test",
            cls="tag-bal",
            price_in=3.0,
            price_out=15.0,
            sub_ja="テスト",
            sub_en="Test",
            scrape_status="success",
        )
        assert m.price_in == 3.0

    def test_negative_price_rejected(self):
        """負の価格は ValidationError"""
        with pytest.raises(ValidationError):
            ApiModel(
                provider="X", name="X", tag="X", cls="X",
                price_in=-1.0, price_out=0.0,
                sub_ja="", sub_en="",
            )
```

## **2. 価格抽出ロジック (外部通信なし)**

```python
# tests/test_browser.py
from scraper.browser import extract_price, sanity_check

class TestExtractPrice:
    def test_dollar_pattern(self):
        """$X.XX パターンから価格を抽出"""
        html = '<span>Input: $3.00 per 1M tokens</span>'
        result = extract_price(html, [r"\$\s*([\d.]+)\s*per"])
        assert result == 3.0

    def test_no_match_returns_none(self):
        """マッチしない場合は None"""
        result = extract_price("no price here", [r"\$\s*([\d.]+)"])
        assert result is None

    def test_out_of_range_rejected(self):
        """範囲外の値は None"""
        html = "$999999.00"
        result = extract_price(html, [r"\$([\d.]+)"])
        assert result is None

class TestSanityCheck:
    def test_valid_value(self):
        value, status = sanity_check(3.0, "test", 5.0)
        assert value == 3.0
        assert status == "success"

    def test_none_falls_back(self):
        value, status = sanity_check(None, "test", 5.0)
        assert value == 5.0
        assert status == "fallback"
```

## **3. 為替レート取得 (httpx モック)**

```python
# tests/test_exchange.py
from unittest.mock import patch, MagicMock
from scraper.exchange import fetch_jpy_rate

class TestFetchJpyRate:
    def test_success(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "rates": {"JPY": 155.22},
            "date": "2026-02-21",
        }
        mock_resp.raise_for_status = MagicMock()

        with patch("scraper.exchange.httpx.get", return_value=mock_resp):
            rate, date = fetch_jpy_rate()
            assert rate == 155.22
            assert date == "2026-02-21"

    def test_failure_returns_fallback(self):
        with patch("scraper.exchange.httpx.get", side_effect=Exception("timeout")):
            rate, date = fetch_jpy_rate(fallback=150.0)
            assert rate == 150.0
            assert date == "fallback"
```

### スクレイパーテストの原則

- **外部通信はモック必須**: Playwright や httpx の実際のネットワーク呼び出しはテストしない
- **ロジック部分をテスト**: `extract_price`, `sanity_check`, モデルバリデーション
- **E2E スクレイプテストは書かない**: 外部サイトの HTML 構造変更で壊れるため

## AAA パターン

全テストは **Arrange-Act-Assert** パターンに従う:

```text
Arrange: テストデータ・モック・前提条件を準備
Act:     テスト対象の関数/コンポーネントを実行
Assert:  期待結果を検証
```

## テストで避けるべきこと

- スナップショットテスト（HTML 構造変更で容易に壊れる）
- 外部 API への実際のリクエスト
- `pricing.json` のハードコードされた値への依存（価格は頻繁に変わる）
- 実装の内部詳細への依存（プライベート関数のテスト等）
- タイマーやタイムアウトに依存するテスト
