# リポジトリ概要とガイド

このドキュメントは、「writing_with_ai」リポジトリの全体像と学習パスを提供します。医療者向けに、AIを活用した英語論文執筆をサポートするためのリソースを体系的に整理しています。

## リポジトリの目的

このリポジトリは、英語論文を書くことが苦手な医療者が、AIツール（GitHub CopilotやClaude）とテンプレートを活用して、効率的に臨床医学論文を執筆できるようにすることを目的としています。

## 学習パス

以下の順序でドキュメントを読み進めることで、効率的に論文執筆の準備から完成までを進めることができます：

1. [Markdown基礎](02_markdown.md) - Markdownの基本的な書き方と論文執筆への応用
2. [AIを活用した執筆ワークフロー](03_ai_workflow.md) - 「結果から投稿への道のり」アプローチとAIツールの活用方法
3. [Gitとガバナンス](04_git_gov.md) - ブランチ/PR運用とコラボレーションの方法

## フォルダ構成

```
writing_with_ai/
├── demo/                # ハンズオン用の最小プロジェクト (draft.md, refs.bib, styles/ など)
├── projects/            # 実際の原稿を置く場所 (Git 管理外)
├── skills/              # AI アシスタント用の Skill 群
├── templates/           # そのままコピーして使う雛形と CSL
├── tutorials/           # 入門ドキュメント (このファイルを含む)
├── resources/           # プロンプト集、STROBE、AI ツール資料
├── README.md            # はじめに + コピペ用プロンプト集
├── CLAUDE.md            # AI アシスタント向けの運用メモ
├── env_check.md         # 環境チェック (AI に読ませて使う)
└── rclone_advanced.md   # rclone の応用メモ
```

## 始め方

1. このリポジトリをクローンまたはフォークする
> このリポジトリは公開の設定になっているので、フォークした場合（自分のレポジトリにコピー）は公開の設定になります。機微な情報を扱いたい場合は、[こちらの方法](https://github.com/SRWS-PSG/writing_with_ai/edit/devin/1744771887-add-writing-guides/docs/01_overview.md)でプライベートレポジトリを作成してください。
3. `templates/` ディレクトリから適切なテンプレートを選択してコピーする
4. VS Codeで開き、`Ctrl+Shift+B`でビルドタスクを実行する
5. 生成されたdocxファイルを確認する

詳細な手順は[README.md](../README.md)を参照してください。

## 次のステップ

- [Markdown基礎](02_markdown.md)に進み、論文執筆に必要なMarkdownの基本を学びましょう。
