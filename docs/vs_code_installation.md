# VS Codeのインストール方法

Visual Studio Code（VS Code）は、Microsoft社が開発した無料のコードエディタで、拡張機能を追加することで論文執筆にも最適なツールとなります。このガイドでは、VS Codeのインストール方法と論文執筆のための基本的なセットアップについて説明します。

## 目次

1. [VS Codeのインストール](#vs-codeのインストール)
2. [日本語化](#日本語化)
3. [論文執筆に役立つ拡張機能](#論文執筆に役立つ拡張機能)
4. [基本的な使い方](#基本的な使い方)

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
4. （オプション）ターミナルからVS Codeを起動できるようにするには：
   - VS Codeを起動し、コマンドパレット（⌘+Shift+P）を開きます
   - 「Shell Command: Install 'code' command in PATH」を検索して実行します

### Linux (Ubuntu/Debian)

```bash
# リポジトリの追加
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
rm -f packages.microsoft.gpg

# インストール
sudo apt update
sudo apt install code
```

## 日本語化

VS Codeの表示言語を日本語に変更するには：

1. VS Codeを起動します
2. 左側のサイドバーから拡張機能アイコン（四角が4つあるアイコン）をクリックします
3. 検索ボックスに「Japanese」と入力します
4. 「Japanese Language Pack for Visual Studio Code」をインストールします
5. インストール完了後、右下に表示される「Restart to apply」をクリックしてVS Codeを再起動します

## 論文執筆に役立つ拡張機能

論文執筆に特に役立つVS Code拡張機能をいくつか紹介します：

1. **Markdown All in One**
   - Markdownの編集をサポートする総合的な拡張機能
   - インストール方法：拡張機能タブで「Markdown All in One」を検索してインストール

2. **Pandoc Citer**
   - BibTeXファイルからの引用をサポート
   - インストール方法：拡張機能タブで「Pandoc Citer」を検索してインストール

3. **Markdown Preview Enhanced**
   - Markdownのリアルタイムプレビュー機能を強化
   - インストール方法：拡張機能タブで「Markdown Preview Enhanced」を検索してインストール

4. **Code Spell Checker**
   - スペルチェック機能（英語）
   - インストール方法：拡張機能タブで「Code Spell Checker」を検索してインストール

5. **Japanese Language Pack**
   - VS Codeの日本語化
   - インストール方法：拡張機能タブで「Japanese」を検索してインストール

## セットアップの注意点

### 同期フォルダでのリポジトリクローンに関する警告

DropboxやGoogle Driveなどの同期フォルダ内にGitリポジトリをクローンすると、同期プロセスがGitのファイル構造と競合し、以下のような問題が発生する可能性があります：

- ファイルロックの競合によりGit操作が失敗する
- 同期中のファイル変更によりリポジトリが破損する
- GitHubへのプッシュやプルが正常に機能しなくなる
- 予期しないマージ競合が発生する

**推奨事項：** 
- Gitリポジトリは常に同期フォルダの外（通常のドキュメントフォルダなど）にクローンしてください
- 必要に応じて、完成した論文ファイルのみを同期フォルダにコピーしてください

## 基本的な使い方

### VS Codeの基本操作

1. **ファイルを開く**
   - メニューから「ファイル」→「開く」を選択
   - または、`Ctrl+O`（Windows/Linux）、`Cmd+O`（macOS）のショートカットを使用

2. **フォルダを開く**
   - メニューから「ファイル」→「フォルダを開く」を選択
   - または、`Ctrl+K Ctrl+O`（Windows/Linux）、`Cmd+K Cmd+O`（macOS）のショートカットを使用

3. **ファイルの保存**
   - メニューから「ファイル」→「保存」を選択
   - または、`Ctrl+S`（Windows/Linux）、`Cmd+S`（macOS）のショートカットを使用

4. **コマンドパレットの使用**
   - `Ctrl+Shift+P`（Windows/Linux）、`Cmd+Shift+P`（macOS）で開く
   - VS Codeの様々な機能にアクセスできる便利なツール

### Markdownファイルの作成と編集

1. 新しいファイルを作成し、`.md`拡張子で保存します（例：`paper.md`）
2. Markdownの構文を使用して文書を作成します
3. プレビューを表示するには、エディタの右上にあるプレビューアイコンをクリックするか、`Ctrl+K V`（Windows/Linux）、`Cmd+K V`（macOS）のショートカットを使用します

詳細な引用管理については、[BibTeXとPandocを使った引用管理ガイド](citation_management.md)を参照してください。
