# Tools README

このディレクトリには、事例データの変換や閲覧に使う補助スクリプトが含まれています。

## GitHub Pages ビューア

本リポジトリでは、`cases/` 配下の JSON をブラウザ上でドキュメントとして閲覧できる静的サイトを `docs/` に用意しています。

- 公開URL: https://rist-kobe.github.io/user-support-cases/
- 機能: カテゴリ別一覧・キーワード全文検索・タグ絞り込み（支援タグ / 技術タグ）・詳細表示（`?case=` クエリパラメータまたはモーダル）

詳細な概要と公開手順は、ルートの [README.md](../README.md) の `GitHub Pages ビューア` セクションを参照してください。

## 事例確認ツール (Streamlit)

JSON 変換結果や技術タグを確認するための簡易検索ツールを提供しています。

### インストール

```bash
pip install streamlit pandas
```

### 起動

```bash
cd tools
streamlit run viewer.py
```

### 主な機能

- キーワード検索
- 技術タグ検索
- 種別による絞り込み
- 高速化倍率による絞り込み
- ノード数による絞り込み
