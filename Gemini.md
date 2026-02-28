# Gemini.md

AI モデルの時間別コスト計算機における Gemini (Code Assist / ADK / CLI) 向けプロジェクト仕様・コンテキストファイルです。

## プロジェクト概要・目的

AI モデルの時間別コスト計算機プロジェクト。Pythonスクレイパーが各社料金ページから価格を自動取得して `pricing.json` を生成し、Reactフロントエンドがそれを読み込んで「単一ポータブルHTML」として出力します。

## 技術スタック・主要ライブラリ

- **バックエンド**: Python 3.12+, uv, Pydantic v2, Playwright, httpx (ディレクトリ: `scraper/`)
- **フロントエンド**: React 19, TypeScript, Vite 7 (`vite-plugin-singlefile`), Bun (ディレクトリ: `web/`)

## ビルド・テスト・デプロイコマンド

- **全体フル更新** (スクレイプ→ビルド→コピー): `bash update.sh`
- **為替レートのみ更新** (スクレイプスキップ): `bash update.sh --no-scrape`
- **スクレイパー単体起動**: `cd scraper && uv run python -m scraper.main --output ../pricing.json`
- **フロントエンド開発サーバー**: `cd web && bun run dev`
- **フロントエンドテスト**: `cd web && bun test`
- **バックエンドテスト**: `cd scraper && uv run pytest`

## コーディング規約 (コンパクト版)

- **TypeScript**: `strict: true`, `erasableSyntaxOnly: true` (enum と namespace は使用禁止)。`any` 禁止(`unknown` + 型ガード推奨)。
- **Python**: Pydantic v2 ベースのスキーマ定義。型ヒント必須 (Python 3.12+ の `|` 記法)。ファイル先頭に `from __future__ import annotations` を付与。
- **データ型同期**: `scraper/src/scraper/models.py` と `web/src/types/pricing.ts` のスキーマは必ず同期させること。

## 禁止操作の明示 (Anti-Patterns)

- ファイル全体の不要な書き直し・過剰なリファクタリング（明示的な指示がない限り禁止）
- 依存関係の勝手なアップグレード
- ビルドツール設定 (`vite`, `bun`, `pytest`, `tsconfig`) や CI ワークフローの無断変更
- `.env` や機密情報のハードコード
- ネットワークテストや重い統合テストの無断追加

## サブエージェント委譲ルール (Agent Routing)

複雑なタスクは以下のようにサブエージェントに適切に委譲または分割して処理すること：

- **Explore**: コードベースの全体探索、影響範囲の特定（Gemini Flash等の高速モデルを推奨）
- **Plan**: 実装計画の策定、仕様の読み込み（読み取り専用）
- **Code Reviewer**: 実装コードのレビュー
- **Debugger**: バグ修正、エラー原因の特定とテストの実行

## 重要ドキュメントへのパス参照

詳細な仕様や設計情報が必要な場合は、以下のファイルを `@` 参照で読み込んでください。

- カスタムルール・複数エージェント共通設定: `@AGENTS.md`
- プロジェクト全体像・仕様: `@docs/spec.md`
- アーキテクチャ図・構成: `@docs/ARCHITECTURE.md`
- 実装ロードマップ: `@docs/tasks.md`
- テスト戦略: `@docs/TESTING.md`
