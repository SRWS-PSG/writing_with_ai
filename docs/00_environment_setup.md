# 環境セットアップガイド

このガイドでは、論文執筆に必要なツールのインストールと基本的なセットアップ方法を説明します。以下の手順に従って、執筆環境を整えましょう。

## 目次

1. [必要なツール](#必要なツール)
2. [VS Codeのインストール](#vs-codeのインストール)
3. [Pandocのインストール](#pandocのインストール)
4. [GitHub Desktopのインストール](#github-desktopのインストール)
5. [リポジトリのクローン](#リポジトリのクローン)
6. [VS Code拡張機能のインストール](#vs-code拡張機能のインストール)
7. [次のステップ](#次のステップ)

## 必要なツール

論文執筆のために以下のツールをインストールする必要があります：

- **VS Code**: テキストエディタ（Markdownファイルの編集に使用）
- **Pandoc**: ドキュメント変換ツール（MarkdownをWordファイルに変換）
- **GitHub Desktop**: リポジトリ管理ツール（オプション、共同執筆時に便利）

## VS Codeのインストール

### Windows

1. [VS Code公式サイト](https://code.visualstudio.com/)にアクセスします
2. ダウンロードボタンをクリックし、インストーラーをダウンロードします
3. ダウンロードしたインストーラーを実行し、画面の指示に従ってインストールを完了します
   - 「PATHへの追加」オプションを有効にすることをお勧めします
   - 「ファイルコンテキストメニューに追加」オプションも便利です

### macOS

1. [VS Code公式サイト](https://code.visualstudio.com/)にアクセスします
2. ダウンロードボタンをクリックし、macOS用のzipファイルをダウンロードします
3. ダウンロードしたzipファイルを解凍し、「Visual Studio Code.app」をApplicationsフォルダにドラッグ＆ドロップします

### VS Codeの日本語化

VS Codeの表示言語を日本語に変更するには：

1. VS Codeを起動します
2. 左側のサイドバーから拡張機能アイコン（四角が4つあるアイコン）をクリックします
3. 検索ボックスに「Japanese」と入力します
4. 「Japanese Language Pack for Visual Studio Code」をインストールします
5. インストール完了後、右下に表示される「Restart to apply」をクリックしてVS Codeを再起動します

## Pandocのインストール

Pandocは、Markdownファイルを様々な形式（Word、PDF、HTMLなど）に変換するためのツールです。

### Windows

1. [Pandocダウンロードページ](https://pandoc.org/installing.html)にアクセスします
2. Windowsインストーラー(.msi)をダウンロードします
3. ダウンロードしたファイルをダブルクリックして指示に従いインストールします

### macOS

1. [Pandocダウンロードページ](https://pandoc.org/installing.html)にアクセスします
2. macOSパッケージ(.pkg)をダウンロードします
3. ダウンロードしたファイルをダブルクリックして指示に従いインストールします

**または**:
- Homebrewがインストールされている場合は、「Homebrew」アプリから検索してインストールできます

## GitHub Desktopのインストール

GitHub Desktopは、コマンドラインを使わずにGitリポジトリを管理するためのグラフィカルツールです。

### Windows / macOS

1. [GitHub Desktop公式サイト](https://desktop.github.com/)にアクセスします
2. 「Download for Windows」または「Download for macOS」ボタンをクリックします
3. ダウンロードしたインストーラーを実行し、画面の指示に従ってインストールを完了します
4. インストール後、GitHub Desktopを起動し、GitHubアカウントでサインインします
   - アカウントをお持ちでない場合は、[GitHub公式サイト](https://github.com/)で作成できます

## リポジトリのクローン

リポジトリをローカルコンピュータにコピー（クローン）するには：

1. GitHub Desktopを開きます
2. 「File」→「Clone Repository」をクリックします
3. URLタブを選択し、以下のURLを入力します：
   ```
   https://github.com/SRWS-PSG/writing_with_ai.git
   ```
4. ローカルパスを選択し、「Clone」ボタンをクリックします
5. クローンが完了すると、リポジトリのファイルがローカルコンピュータに保存されます

## VS Code拡張機能のインストール

論文執筆に役立つVS Code拡張機能をインストールします：

1. VS Codeを起動します
2. 左側のサイドバーから拡張機能アイコン（四角が4つあるアイコン）をクリックします
3. 以下の拡張機能を検索してインストールします：
   - **Markdown All in One**: Markdownの編集をサポートする総合的な拡張機能
   - **markdownlint**: Markdownの文法チェックを行う拡張機能
   - **Pandoc Citer**: BibTeXファイルからの引用をサポートする拡張機能
   - **GitHub Copilot**（オプション）: AIによるコード補完機能
   - **GitHub Copilot Chat**（オプション）: AIとのチャット機能

## 次のステップ

環境のセットアップが完了したら、次は[リポジトリの概要](01_overview.md)に進み、リポジトリの構造と使い方について学びましょう。
