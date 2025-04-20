# リポジトリ概要とガイド

このドキュメントは、「writing_with_ai」リポジトリの全体像と学習パスを提供します。医療者向けに、AIを活用した英語論文執筆をサポートするためのリソースを体系的に整理しています。

## リポジトリの目的

このリポジトリは、英語論文を書くことが苦手な医療者が、AIツール（GitHub CopilotやClaude）とテンプレートを活用して、効率的に臨床医学論文を執筆できるようにすることを目的としています。

## 学習パス

以下の順序でドキュメントを読み進めることで、効率的に論文執筆の準備から完成までを進めることができます：

1. [Markdown基礎](01_markdown.md) - Markdownの基本的な書き方と論文執筆への応用
2. [AIを活用した執筆ワークフロー](02_ai_workflow.md) - 「結果から投稿への道のり」アプローチとAIツールの活用方法
3. [Gitとガバナンス](03_git_gov.md) - ブランチ/PR運用とコラボレーションの方法

## フォルダ構成

```
writing_with_ai/
├── docs/                # 読むだけで理解できる学習ガイド
│   ├── 00_overview.md   # サイトマップ & 学習ルート（このファイル）
│   ├── 01_markdown.md   # Markdown 超入門
│   ├── 02_ai_workflow.md # AIを活用した執筆ワークフロー
│   ├── 03_git_gov.md    # ブランチ/PR 運用 & CODEOWNERS
│   └── _assets/         # 画像・動画
├── templates/           # そのままコピーして使う雛形
│   ├── imrad_full.md    # IMRaD形式の論文テンプレート
│   ├── results_first.md # 結果から投稿への道のりテンプレート
│   └── letter_to_editor.md # 編集者への手紙テンプレート
├── scripts/             # 補助スクリプト
│   └── build.sh         # ビルドスクリプト
├── .vscode/             # VS Code設定
│   ├── tasks.json       # ビルド・リント・スペルチェックタスク
│   └── copilot-chat.json # Copilotチャットスニペット
├── .github/             # GitHub関連設定
│   ├── workflows/       # CI/CDワークフロー
│   └── PULL_REQUEST_TEMPLATE.md # PRテンプレート
├── resources/           # 各種リソース
│   ├── csl/             # 引用スタイル
│   └── prompts/         # AIプロンプトライブラリ
└── README.md            # はじめに + 最短10分で動かす手順
```

## 始め方

1. このリポジトリをクローンまたはフォークする
2. `templates/` ディレクトリから適切なテンプレートを選択してコピーする
3. VS Codeで開き、`Ctrl+Shift+B`でビルドタスクを実行する
4. 生成されたdocxファイルを確認する

詳細な手順は[README.md](../README.md)を参照してください。

## 次のステップ

- [Markdown基礎](01_markdown.md)に進み、論文執筆に必要なMarkdownの基本を学びましょう。
