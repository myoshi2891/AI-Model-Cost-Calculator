# AI Model Pricing / AI Model Cost Calculator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AIモデルの最新価格を自動取得し、時間あたりのコストを計算・比較できるポータブルなWebツールです。

## 概要

このプロジェクトは、各AIプロバイダー（Anthropic, OpenAI, Google, AWS, DeepSeek, xAI等）の料金ページから最新の価格情報をスクレイピングし、直感的なUIでコストを試算できる単一のHTMLファイルを提供します。

### 特徴

- **自動更新**: Pythonスクレイパーが定期的に（または手動で）最新価格を取得
- **ポータブル**: 全てのアセット（CSS/JS/Data）をインライン化した単一の `index.html` として出力。サーバー不要でどこでも閲覧可能
- **バイリンガル**: 日本語と英語に完全対応
- **詳細な試算**: 入力/出力トークン、月間リクエスト数などに基づいた詳細な月額・年額シミュレーション

## クイックスタート

### 成果物の閲覧

ルートディレクトリにある `index.html` をブラウザで開くだけで、最新の価格データに基づいた計算機を利用できます。

### データの更新

最新の価格をスクレイピングしてレポートを再生成するには、以下のコマンドを実行します。

```bash
bash update.sh
```

## アーキテクチャ

プロジェクトは主に以下の2つのコンポーネントで構成されています。

1. **scraper/** (Python):
    - `uv` を使用した現代的なPython環境。
    - `Playwright` を用いて各プロバイダーのページから価格を抽出。
    - 取得したデータを `pricing.json` として出力。
2. **web/** (React + TypeScript):
    - `Bun` を使用した高速なビルド環境。
    - `Vite` + `vite-plugin-singlefile` により、ポータブルな単一HTMLを生成。

## 開発者向けガイド

### セットアップ

#### スクレイパー (Python)

```bash
cd scraper
uv sync
playwright install chromium
```

#### フロントエンド (Web)

```bash
cd web
bun install
```

### 主要なコマンド

- **全工程の実行**: `bash update.sh`
- **フロントエンド開発サーバー**: `cd web && bun run dev`
- **スクレイパー単体実行**: `cd scraper && uv run python -m scraper.main`

## ライブラリ・技術スタック

- **Scraper**: Python 3.12+, uv, Pydantic v2, Playwright, httpx
- **Web**: React 19, TypeScript, Vite 7, Bun, Tailwind CSS

## ライセンス

[MIT License](LICENSE) (またはプロジェクトのライセンス条項に従ってください)
