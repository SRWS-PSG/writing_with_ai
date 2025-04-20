# writing_with_ai

> 医療者向け「AI × Markdown × GitHub」で英語論文を書くスターターキット

このリポジトリは、英語論文を書くことが苦手な医療者が、AIツール（GitHub CopilotやClaude）とテンプレートを活用して、効率的に臨床医学論文を執筆できるようにすることを目的としています。

## :beginner: Quick Start – まず 10 分で書き始める

> **対象:**  
> *英語論文執筆に不慣れな臨床医* が **Git 未経験でも** 最速でテンプレ → Word 出力まで完了させる手順です。  
> VS Code を利用して、Pandoc などの依存関係をセットアップします。

---

### 0. 環境セットアップ（所要 5 分）

| OS | Git | VS Code | Docker Desktop¹ |
|----|-----|---------|-----------------|
| **Windows** | `winget install --id Git.Git -e` | `winget install --id Microsoft.VisualStudioCode -e` | [Download](https://www.docker.com/products/docker-desktop/) |
| **macOS** | `brew install git` | `brew install --cask visual-studio-code` | 同上 |
| **Ubuntu** | `sudo apt install git` | `sudo snap install code --classic` | `sudo apt install docker.io docker-compose` |

> ¹ Docker は必須ではありませんが、入れておくと将来的な拡張性が高まります。  
> ² PATH が反映されない場合は再ログインしてください。

詳細な環境セットアップ手順は[環境セットアップガイド](docs/00_environment_setup.md)を参照してください。

---

### 1. レポジトリを取得（1 分）

```bash
git clone https://github.com/SRWS-PSG/writing_with_ai.git
cd writing_with_ai
```

> Git が使えない PC では
> 1. GitHub → 「🡇 Code」→ Download ZIP をクリック
> 2. ZIP を展開してフォルダを開く

---

### 2. VS Code で開く（1 分）

```bash
code .
```

VS Code が起動したら、必要な拡張機能をインストールします  
（Markdown All in One、markdownlint、Pandoc Citer など）

---

### 3. テンプレートを複製（30 秒）

1. Ctrl + Shift + P → Templates: New Paper

2. フォーマットを選択（例：IMRaD）

3. paper.md が作成される

---

### 4. Word ファイルを生成（30 秒）

1. Ctrl + Shift + B

2. タスク一覧から Generate Word (Pandoc) を選択

3. out/paper.docx に出力されれば成功！

---

### 5. よくあるエラー & 対処

- **依存関係エラー**: 必要なパッケージ（Pandoc、LaTeX など）がインストールされているか確認してください
- **ビルドエラー**: VS Code のターミナルでエラーメッセージを確認し、必要なパッケージをインストールしてください
- **テンプレート選択エラー**: 手動で templates フォルダからテンプレートをコピーして使用することもできます

---

### Codespaces / ブラウザだけで始める

Git & Docker を入れられない場合は次のボタンから GitHub Codespaces を起動すれば、ブラウザだけで上記 2‑4 章が実行できます。

[![Open in Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=SRWS-PSG/writing_with_ai)

---

### 次に読む

- [docs/01_overview.md](docs/01_overview.md) – リポジトリ概要とガイド
- [docs/02_markdown.md](docs/02_markdown.md) – 医学論文向け Markdown の書き方
- [docs/03_ai_workflow.md](docs/03_ai_workflow.md) – Copilot・Cline を使った AI 改稿フロー
- [docs/04_git_gov.md](docs/04_git_gov.md) – 共同執筆のための Git 運用とガバナンス

> 質問や不具合は Issues へどうぞ。Happy writing!

## 🗺️ リポジトリマップ

```
writing_with_ai/
├── docs/                # 読むだけで理解できる学習ガイド
│   ├── 00_environment_setup.md # 環境セットアップガイド
│   ├── 01_overview.md   # サイトマップ & 学習ルート
│   ├── 02_markdown.md   # Markdown 超入門
│   ├── 03_ai_workflow.md # AIを活用した執筆ワークフロー
│   ├── 04_git_gov.md    # ブランチ/PR 運用 & CODEOWNERS
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

詳細は[AIを活用した執筆ワークフロー](docs/03_ai_workflow.md)を参照してください。

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

複数のファイルを一括処理する場合は、VS Codeのエクスプローラービューで各ファイルを開いて処理するか、サポートが必要な場合は[Gitとガバナンス](docs/04_git_gov.md)を参照してください。

## 🙋‍♂️ よくある質問

### Pandocのインストール方法は？

**手動インストールの場合**:
- **Windows**: [Pandocダウンロードページ](https://pandoc.org/installing.html)からインストーラー(.msi)をダウンロードして実行
- **macOS**: [Pandocダウンロードページ](https://pandoc.org/installing.html)からパッケージ(.pkg)をダウンロードして実行、またはHomebrewで`brew install pandoc`
- **Ubuntu**: `sudo apt install pandoc`

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


詳細は[VS Codeのインストール方法](docs/00_environment_setup.md#vs-codeの拡張機能)を参照してください。

## 貢献について

このリポジトリへの貢献を歓迎します。改善案やバグ報告は、Issueを作成するか、Pull Requestを送信してください。
