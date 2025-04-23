# writing_with_ai

> 医療者向け「AI × Markdown × GitHub」で英語論文を書くスターターキット

このリポジトリは、英語論文を書くことが苦手な医療者が、AI ツール（GitHub Copilot や Claude）とテンプレートを活用して、効率的に臨床医学論文を執筆できるようにすることを目的としています。

## :beginner: Quick Start – まず 10 分で書き始める

> **対象:**  
> _英語論文執筆に不慣れな臨床医_ が **Git 未経験でも** 最速でテンプレ → Word 出力まで完了させる手順です。  
> VS Code + Dev Container を利用するため、Pandoc などの依存は自動で設定できます。

---

### 0. 環境セットアップ（所要 5 分）

Docker + DevContainer を使った簡単セットアップ方法：

1. [VS Code](https://code.visualstudio.com/) をインストール
2. VS Code で「Dev Containers」拡張機能をインストール
   - 拡張機能タブ（左側バー）→「Dev Containers」で検索 → インストール
3. [Docker Desktop](https://www.docker.com/products/docker-desktop/) をインストール
   - インストール後、起動しておく
4. [GitHub アカウント](https://github.com/)の作成
   - GitHub 公式サイトにアクセス
   - 「Sign up」ボタンをクリック
   - 指示に従ってメールアドレス、パスワード、ユーザー名を入力
   - アカウント作成後、メール認証を完了

---

### 1. レポジトリを取得（1 分）

> リポジトリ（Repository）とは、ファイルやフォルダの集まりで、その変更履歴も含めて保存される場所です。このリポジトリには論文テンプレートやツール、ドキュメントなどが格納されています。

1. VS Code を起動
2. 左側のアクティビティバーから「ソース管理」アイコン（分岐アイコン）をクリック
3. 「リポジトリのクローン」ボタンをクリック
4. 「https://github.com/SRWS-PSG/writing_with_ai.git」などのリポジトリURLを入力
5. クローン先のローカルフォルダを選択 (このときクラウドストレージと同期しているフォルダを使わないこと！)
6. 一番左上のドキュメントアイコンをクリック

> これで、レポジトリを取得できました。クローンは、クラウド上のレポジトリを自分の PC にコピーすることを指します。

4. クローンしたフォルダを VS Code で開く
5. 画面左下の「><」アイコンをクリック →「Reopen in Container」を選択

これだけで完了！Pandoc など必要なツールが全て自動的にインストールされます。

---

### 2. テンプレートを確認（30 秒）

1. VS Code のファイルエクスプローラーで [`templates` フォルダ](templates/)を開く

2. テンプレートファイル（例：[`paper_template.md`](templates/paper_template.md)または[`results_first_template.md`](templates/results_first_template.md)）をクリックして開く

3. 「ファイル」→「名前を付けて保存」で `paper.md` として保存
   > テンプレートを上書きしないため

---

### 3. Word ファイルを生成（30 秒）

1. Markdown ファイル（paper.md）を開いた状態で Ctrl + Shift + B を押す
2. ビルドタスク「build-docx」が自動的に実行される
   （タスク一覧が表示された場合は「build-docx」を選択）

3. 保存したファイルと同じフォルダに paper.docx が生成されれば成功！

---

### 4. よくあるエラー & 対処

- **ビルドエラー**: VS Code のターミナルでエラーメッセージを確認し、必要なパッケージをインストールしてください
- **引用文献エラー**: Pandoc 3.x を使用している場合は、`--citeproc` オプションが必要です（VS Code のビルドタスクには既に含まれています）
- **ファイルが見つからないエラー**: 参考文献ファイル（`.bib`）が Markdown ファイルと同じディレクトリにあることを確認してください

---

### Codespaces / ブラウザだけで始める

Git を入れられない場合は次のボタンから GitHub Codespaces を起動すれば、ブラウザだけで下記 1-4 章が実行できます。環境には必要なツール（Pandoc など）が自動的にインストールされます。

[![Open in Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/SRWS-PSG/writing_with_ai)

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
├── .devcontainer/       # Codespaces/Dev Container設定
│   ├── devcontainer.json # 開発環境設定
│   └── Dockerfile       # 環境構築設定
├── resources/           # 各種リソース
│   ├── csl/             # 引用スタイル
│   └── prompts/         # AIプロンプトライブラリ
└── README.md            # はじめに + 最短10分で動かす手順
```

## 🤖 AI ワークフロー チートシート

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

各ステップでの AI ツール活用ポイント：

- **結果の整理**: [section_outline.prompt](resources/prompts/section_outline.prompt)を使用
- **結果セクション**: [stats2sentence.prompt](resources/prompts/stats2sentence.prompt)を使用
- **文章洗練**: [refinement.prompt](resources/prompts/refinement.prompt)を使用

詳細は[AI を活用した執筆ワークフロー](docs/03_ai_workflow.md)を参照してください。

## 🛠️ ビルド & チェック機能

VS Code では以下のタスクが利用可能です：

- **ビルド**: `Ctrl+Shift+B` - Markdown ファイルを docx に変換
- **リント**:
  1. `Ctrl+Shift+P`でコマンドパレットを開く
  2. `Tasks: Run Task`と入力
  3. `lint-md`を選択 - Markdown の文法チェック
- **スペルチェック**:
  1. `Ctrl+Shift+P`でコマンドパレットを開く
  2. `Tasks: Run Task`と入力
  3. `spell-check`を選択 - スペルチェック

複数のファイルを一括処理する場合は、VS Code のエクスプローラービューで各ファイルを開いて処理するか、サポートが必要な場合は[Git とガバナンス](docs/04_git_gov.md)を参照してください。

## 🙋‍♂️ よくある質問

### DevContainer が起動しません

以下を確認してください：

- Docker Desktop が起動しているか
- VS Code の「Dev Containers」拡張機能がインストールされているか
- 十分なディスク容量があるか（最低 10GB 以上の空き容量を推奨）

### 引用文献が正しく処理されません

以下を確認してください：

1. YAML フロントマターに`bibliography`と`csl`が正しく設定されているか
2. 参考文献ファイル（`.bib`）が Markdown ファイルと同じディレクトリにあるか

VS Code では、`Ctrl+Shift+B`を押すことで自動的に`--citeproc`オプション付きでビルドが実行されます。

### DevContainer の利点は？

- **環境構築が簡単**：Pandoc、LaTeX、各種ツールが自動インストール
- **環境の一貫性**：全員が同じ環境で作業できるため「動かない」問題が発生しにくい
- **VS Code 拡張の自動設定**：Markdown 編集に便利な拡張機能が自動的にインストール
- **複数 OS 対応**：Windows、Mac、Linux で同じ環境が利用可能

### 論文なのでprivateレポジトリで編集したい

方法 | 手順の概要 | 備考
GitHub Importer で新規リポジトリとして取り込む | 1. https://github.com/new/import へアクセス2. フォーク元の URL を入力3. Privacy を Private に設定してインポート | インポートしたリポジトリは元リポジトリとの「フォーク関係」がなく、プルリクエストのやり取りは自動では行えません。
ローカルで clone → 新規プライベートリポジトリに push | 1. git clone でローカルに取得2. GitHub で空のプライベートリポジトリを作成3. git remote set-url origin <新リポジトリURL>4. git push -u origin main | 完全に独立したコピーになります。

## 貢献について

このリポジトリへの貢献を歓迎します。改善案やバグ報告は、Issue を作成するか、Pull Request を送信してください。
