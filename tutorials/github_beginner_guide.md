# GitHub初心者ガイド：リポジトリのフォークとクローン

このガイドでは、GitHubの基本操作、特にリポジトリのフォークとローカルへのクローン方法について、PC初心者向けに詳しく説明します。

## 目次

1. [GitHubアカウントの作成](#githubアカウントの作成)
2. [リポジトリのフォーク（コピー）](#リポジトリのフォーク)
3. [Gitのインストール](#gitのインストール)
4. [リポジトリのクローン（ダウンロード）](#リポジトリのクローン)
5. [GitHub Desktopの使い方](#github-desktopの使い方)
6. [推奨拡張機能のインストール](#推奨拡張機能のインストール)
7. [VS Codeでの作業](#vs-codeでの作業)
8. [よくある質問](#よくある質問)

## GitHubアカウントの作成

GitHubを使うには、まずアカウントが必要です。

1. [GitHub公式サイト](https://github.com/)にアクセスします
2. 右上の「Sign up」ボタンをクリックします
3. 指示に従って以下の情報を入力します：
   - メールアドレス
   - パスワード
   - ユーザー名（他のユーザーと重複しない一意の名前）
4. 「Create account」ボタンをクリックします
5. メールアドレス確認のためのコードを入力します
6. 簡単なアンケートに回答します（スキップも可能）
7. 無料プラン（Free）を選択します

これでGitHubアカウントの作成は完了です。

## リポジトリのフォーク

フォークとは、他の人のリポジトリ（プロジェクト）を自分のGitHubアカウントにコピーすることです。

1. フォークしたいリポジトリ（例：[SRWS-PSG/writing_with_ai](https://github.com/SRWS-PSG/writing_with_ai)）のページにアクセスします
2. 右上の「Fork」ボタンをクリックします

   ![Forkボタンの位置](https://docs.github.com/assets/cb-40742/mw-1440/images/help/repository/fork-button.webp)

3. 「Create a new fork」画面が表示されます
4. 必要に応じてリポジトリ名を変更できます（変更しなくても問題ありません）
5. 「Create fork」ボタンをクリックします

これで、リポジトリが自分のGitHubアカウントにコピーされました。URLが `https://github.com/あなたのユーザー名/writing_with_ai` のようになっていることを確認してください。

## Gitのインストール

リポジトリをローカルPCにダウンロード（クローン）するには、Gitというソフトウェアが必要です。

### Windowsの場合

1. [Git for Windows](https://gitforwindows.org/)にアクセスします
2. 「Download」ボタンをクリックしてインストーラーをダウンロードします
3. ダウンロードしたインストーラーを実行します
4. 基本的にはデフォルト設定のまま「Next」ボタンを押していきます
   - 「Adjusting your PATH environment」の画面では「Git from the command line and also from 3rd-party software」を選択します
   - 「Configuring the line ending conversions」の画面では「Checkout Windows-style, commit Unix-style line endings」を選択します
5. インストールが完了したら「Finish」ボタンをクリックします

### Macの場合

1. ターミナルを開きます（Finderで「アプリケーション」→「ユーティリティ」→「ターミナル」）
2. 以下のコマンドを入力してEnterキーを押します：
   ```
   xcode-select --install
   ```
3. 表示されるダイアログで「インストール」をクリックします
4. インストールが完了するまで待ちます

## リポジトリのクローン

クローンとは、GitHubのリポジトリをローカルPC（自分のパソコン）にダウンロードすることです。

### Windowsの場合

1. フォークした自分のリポジトリページ（`https://github.com/あなたのユーザー名/writing_with_ai`）にアクセスします
2. 緑色の「Code」ボタンをクリックします

   ![Codeボタンの位置](https://docs.github.com/assets/cb-20363/mw-1440/images/help/repository/code-button.webp)

3. 「HTTPS」タブが選択されていることを確認し、URLをコピーします
4. スタートメニューから「Git Bash」を検索して起動します
5. クローンしたいフォルダに移動します（例：デスクトップの場合）：
   ```
   cd ~/Desktop
   ```
6. 以下のコマンドを入力します（URLは先ほどコピーしたものに置き換えてください）：
   ```
   git clone https://github.com/あなたのユーザー名/writing_with_ai.git
   ```
7. Enterキーを押すと、ダウンロードが始まります

### Macの場合

1. フォークした自分のリポジトリページにアクセスします
2. 緑色の「Code」ボタンをクリックし、HTTPSのURLをコピーします
3. ターミナルを開きます
4. クローンしたいフォルダに移動します（例：デスクトップの場合）：
   ```
   cd ~/Desktop
   ```
5. 以下のコマンドを入力します（URLは先ほどコピーしたものに置き換えてください）：
   ```
   git clone https://github.com/あなたのユーザー名/writing_with_ai.git
   ```
6. Enterキーを押すと、ダウンロードが始まります

## GitHub Desktopの使い方

コマンドラインが苦手な方は、GitHub Desktopというグラフィカルなアプリケーションを使うと、より簡単にGitHubのリポジトリを管理できます。

### GitHub Desktopのインストール

1. [GitHub Desktop公式サイト](https://desktop.github.com/)にアクセスします
2. 「Download for Windows」または「Download for macOS」ボタンをクリックします
3. ダウンロードしたインストーラーを実行します
4. 画面の指示に従ってインストールを完了します

### GitHub Desktopでリポジトリをクローンする

1. GitHub Desktopを起動します
2. 「File」メニューから「Clone Repository」を選択します

   ![Clone Repository](https://docs.github.com/assets/cb-19595/mw-1440/images/help/desktop/clone-file-menu-mac.webp)

3. 「GitHub.com」タブを選択します
4. 自分のアカウントに表示されるリポジトリ一覧から、クローンしたいリポジトリ（例：あなたのユーザー名/writing_with_ai）を選択します
   - リストに表示されない場合は、検索ボックスにリポジトリ名を入力して検索します
   - または「URL」タブを選択し、リポジトリのURLを直接入力することもできます

   ![Clone Repository Dialog](https://docs.github.com/assets/cb-33207/mw-1440/images/help/desktop/clone-repository-dialog.webp)

5. 「Local Path」でクローン先のフォルダを選択します
6. 「Clone」ボタンをクリックします

これで、リポジトリがローカルPCにクローンされます。

### GitHub Desktopでの基本操作

#### 変更の確認と保存（コミット）

1. ファイルを編集すると、GitHub Desktopの左側に変更されたファイルが表示されます
2. 変更内容を確認し、コミットメッセージ（変更内容の説明）を入力します
3. 「Commit to main」ボタンをクリックして変更を保存します

   ![Commit Changes](https://docs.github.com/assets/cb-32137/mw-1440/images/help/desktop/commit-button.webp)

#### 変更のアップロード（プッシュ）

1. 変更をコミットした後、「Push origin」ボタンをクリックして変更をGitHubにアップロードします

   ![Push Changes](https://docs.github.com/assets/cb-49882/mw-1440/images/help/desktop/push-origin-button.webp)

#### 最新の変更を取得（プル）

1. 他の人が変更を加えた場合、「Fetch origin」ボタンをクリックして最新の変更を確認します
2. 変更がある場合は「Pull origin」ボタンが表示されるので、クリックして最新の変更を取り込みます

#### ブランチの作成と切り替え

1. 現在のブランチ名が表示されているボタンをクリックします
2. 「New Branch」ボタンをクリックします
3. ブランチ名を入力して「Create Branch」ボタンをクリックします

   ![Create Branch](https://docs.github.com/assets/cb-45366/mw-1440/images/help/desktop/click-create-branch.webp)

4. 作成したブランチに自動的に切り替わります
5. 別のブランチに切り替えるには、ブランチ名が表示されているボタンをクリックし、切り替えたいブランチを選択します

### VS Codeとの連携

GitHub Desktopは、VS Codeと簡単に連携できます。

1. リポジトリを選択した状態で、「Repository」メニューから「Open in Visual Studio Code」を選択します

   ![Open in VS Code](https://docs.github.com/assets/cb-54129/mw-1440/images/help/desktop/open-in-vscode.webp)

2. VS Codeが起動し、リポジトリのフォルダが開きます

これにより、GitHub Desktopでリポジトリを管理しながら、VS Codeでコードを編集することができます。

## 推奨拡張機能のインストール

リポジトリをクローンして VS Code で開くと、このプロジェクトに推奨される拡張機能をインストールするよう案内されることがあります。推奨拡張機能をインストールすることで、プロジェクトのコード規約に合わせた開発環境が自動的に整います。

1. VS Code でクローンしたリポジトリフォルダを開きます
2. 右下に「Install recommended extensions for this workspace?」（このワークスペースの推奨拡張機能をインストールしますか？）というポップアップが表示されたら、「Install」ボタンをクリックします

   ![推奨拡張機能のポップアップ](https://code.visualstudio.com/assets/docs/editor/extension-marketplace/recommendations-notification.png)

3. これで必要な拡張機能が自動的にインストールされます

ポップアップが表示されない場合は、次の手順で手動でインストールできます：

1. VS Code の左側のアクティビティバーにある拡張機能アイコン（四角が重なったアイコン）をクリックします
2. 上部の「RECOMMENDED」タブを選択します

   ![推奨タブの位置](https://code.visualstudio.com/assets/docs/editor/extension-marketplace/extensions-recommended.png)

3. 表示された拡張機能リストから「Install」ボタンをクリックします

これで、リポジトリで推奨されている拡張機能がすべてインストールされ、最適な開発環境が整いました。

## VS Codeでの作業

クローンしたリポジトリをVS Codeで開いて作業を始めましょう。

### VS Codeのインストール

まだVS Codeをインストールしていない場合は、[VS Codeのインストール方法](vs_code_installation.md)を参照してください。

### リポジトリを開く

1. VS Codeを起動します
2. メニューから「ファイル」→「フォルダーを開く」を選択します
3. クローンしたリポジトリのフォルダ（例：`Desktop/writing_with_ai`）を選択して「開く」をクリックします
4. 左側のエクスプローラーパネルにファイルが表示されます
5. ファイルをクリックして編集を始めることができます

## よくある質問

### Q: GitHubのアカウントは有料ですか？
A: 基本的な機能は無料で利用できます。公開リポジトリの作成や既存リポジトリへの貢献は無料プランで十分です。

### Q: フォークとクローンの違いは何ですか？
A: フォークはGitHub上でリポジトリを自分のアカウントにコピーする操作、クローンはGitHub上のリポジトリをローカルPC（自分のパソコン）にダウンロードする操作です。

### Q: パスワードを入力するよう求められますが、キーボードで入力しても何も表示されません
A: セキュリティ上の理由から、パスワードやトークンを入力しても画面には表示されません。見えなくても正しく入力されていますので、入力後にEnterキーを押してください。

### Q: 「git」コマンドが見つかりませんというエラーが出ます
A: Gitが正しくインストールされていないか、PATHが設定されていない可能性があります。インストール手順を再確認するか、PCを再起動してみてください。

### Q: クローン後にファイルが見つかりません
A: クローンしたフォルダに移動しているか確認してください。Windowsの場合は「cd writing_with_ai」、Macの場合も同様のコマンドでフォルダに移動できます。

### Q: 推奨拡張機能のポップアップが表示されません
A: VS Codeのバージョンが古い場合や、設定によっては表示されないことがあります。その場合は、左側の拡張機能アイコンをクリックし、「RECOMMENDED」タブから手動でインストールしてください。

### Q: 推奨拡張機能は必ずインストールする必要がありますか？
A: 必須ではありませんが、プロジェクトのコード規約に合わせた開発環境を簡単に整えられるため、インストールすることをお勧めします。チーム開発では、メンバー間で同じ環境を共有するために重要です。

### Q: 別のリポジトリも使いたい場合、同じフォルダでクローンしても良いですか？
A: いいえ、絶対に避けてください。Gitの仕組み上、1つのフォルダ（とその子フォルダ）には1つのリポジトリ（1つの.gitディレクトリ）しか存在できません。別のリポジトリを使用したい場合は、必ず別のフォルダを作成してそこにクローンしてください。例えば、「project-A」と「project-B」という2つのリポジトリを扱う場合、それぞれ別のフォルダにクローンする必要があります。

---

さらに詳しい情報は[GitHub公式ドキュメント](https://docs.github.com/ja)を参照してください。
