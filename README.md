# writing_with_ai

> 医療者向け「AI × Markdown × GitHub」で英語論文を書くスターターキット

このリポジトリは、英語論文を書くことが苦手な医療者が、AIツール（GitHub CopilotやClaude）とテンプレートを活用して、効率的に臨床医学論文を執筆できるようにすることを目的としています。

## 🚀 クイックスタート (10分)

1. **VS Codeを起動**
   - デスクトップまたはスタートメニューからVS Codeを起動
   - 「File」→「Open Folder」を選択
   - 論文を保存したいフォルダを選択または新規作成

2. **テンプレートを取得**
   - 「File」→「New File」を選択し、新しいファイルを作成
   - [templates/results_first_template.md](https://github.com/SRWS-PSG/writing_with_ai/blob/main/templates/results_first_template.md)の内容をコピー
   - 新しいファイルに貼り付けて「Save」（例: `my_paper.md`として保存）

3. **論文を編集**
   - テンプレートの指示に従って内容を編集
   - GitHub Copilotが有効な場合は、AIの提案を活用

4. **ビルド実行**
   - `Ctrl+Shift+B`でビルドタスクを実行
   - 同じフォルダに生成されたdocxファイルを確認

## 🗺️ リポジトリマップ

```
writing_with_ai/
├── docs/                # 読むだけで理解できる学習ガイド
│   ├── 00_overview.md   # サイトマップ & 学習ルート
│   ├── 01_markdown.md   # Markdown 超入門
│   ├── 02_ai_workflow.md # AIを活用した執筆ワークフロー
│   ├── 03_git_gov.md    # ブランチ/PR 運用 & CODEOWNERS
│   └── _assets/         # 画像・動画
├── templates/           # そのままコピーして使う雛形
│   ├── imrad_full.md    # IMRaD形式の論文テンプレート
│   ├── results_first_template.md # 結果から投稿への道のりテンプレート
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

## 📚 ステップバイステップガイド

詳細な使い方は以下のドキュメントを参照してください：

1. [環境セットアップガイド](docs/00_environment_setup.md)
2. [リポジトリ概要とガイド](docs/01_overview.md)
3. [Markdown基礎](docs/02_markdown.md)
4. [AIを活用した執筆ワークフロー](docs/03_ai_workflow.md)
5. [Gitとガバナンス](docs/04_git_gov.md)

## 🤖 AIワークフロー チートシート

「結果から投稿への道のり」アプローチに基づいた執筆ワークフロー：

```mermaid
graph LR
  A[結果の整理] -->|ボトムラインメッセージ| B(結果セクション)
  B --> C(方法セクション)
  C --> D(考察セクション)
  D --> E(背景セクション)
  E --> F(要旨)
  F --> G[最終原稿]
  
  style A fill:#f9f9f9,stroke:#333,stroke-width:1px
  style B fill:#e1f5fe,stroke:#0288d1,stroke-width:1px
  style C fill:#e8f5e9,stroke:#388e3c,stroke-width:1px
  style D fill:#fff3e0,stroke:#f57c00,stroke-width:1px
  style E fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px
  style F fill:#e8eaf6,stroke:#3f51b5,stroke-width:1px
  style G fill:#fce4ec,stroke:#e91e63,stroke-width:1px
```

各ステップでのAIツール活用ポイント：
- **結果の整理**: [section_outline.prompt](resources/prompts/section_outline.prompt)を使用
- **結果セクション**: [stats2sentence.prompt](resources/prompts/stats2sentence.prompt)を使用
- **文章洗練**: [refinement.prompt](resources/prompts/refinement.prompt)を使用

詳細は[AIを活用した執筆ワークフロー](docs/02_ai_workflow.md)を参照してください。

## 🛠️ ビルド & チェック機能

VS Codeでは以下のタスクが利用可能です：

- **ビルド**: `Ctrl+Shift+B` - Markdownファイルをdocxに変換
- **リント**: 
  1. `Ctrl+Shift+P`でコマンドパレットを開く
  2. `Tasks: Run Task`と入力
  3. `lint-md`を選択 - Markdownの文法チェック
- **スペルチェック**: 
  1. `Ctrl+Shift+P`でコマンドパレットを開く
  2. `Tasks: Run Task`と入力
  3. `spell-check`を選択 - スペルチェック

複数のファイルを一括処理する場合は、VS Codeのエクスプローラービューで各ファイルを開いて処理するか、サポートが必要な場合は[Gitとガバナンス](docs/03_git_gov.md)を参照してください。

## 🙋‍♂️ FAQ

### Pandocのインストール方法は？

**Windows**:
1. [Pandocダウンロードページ](https://pandoc.org/installing.html)にアクセス
2. Windowsインストーラー(.msi)をダウンロード
3. ダウンロードしたファイルをダブルクリックして指示に従いインストール

**macOS**:
1. [Pandocダウンロードページ](https://pandoc.org/installing.html)にアクセス
2. macOSパッケージ(.pkg)をダウンロード
3. ダウンロードしたファイルをダブルクリックして指示に従いインストール

**または**:
- Homebrewがインストールされている場合は、「Homebrew」アプリから検索してインストール

### 引用文献が正しく処理されません

以下を確認してください：

1. YAMLフロントマターに`bibliography`と`csl`が正しく設定されているか
2. Pandocコマンドに`--citeproc`オプションが指定されているか

VS Codeでは、`Ctrl+Shift+B`を押すことで自動的に`--citeproc`オプション付きでビルドが実行されます。

### VS Codeの推奨拡張機能は？

- Markdown All in One
- markdownlint
- Pandoc Citer
- GitHub Copilot
- GitHub Copilot Chat

詳細は[VS Codeのインストール方法](docs/vs_code_installation.md)を参照してください。

## 貢献について

このリポジトリへの貢献を歓迎します。改善案やバグ報告は、Issueを作成するか、Pull Requestを送信してください。
