# Git 基本ガイド

このガイドでは、GitHub Desktop と VS Code を使用した Git の基本的な操作方法を説明します。コマンドラインを使わずに、グラフィカルなインターフェースで Git を操作する方法を学びましょう。

## Git とは？

Git は、ファイルの変更履歴を管理するためのバージョン管理システムです。複数人での共同作業や、自分の作業の履歴を残すのに役立ちます。

## GitHub Desktop のインストール

1. [GitHub Desktop のダウンロードページ](https://desktop.github.com/)にアクセスします
2. お使いのオペレーティングシステム（Windows/macOS）用のインストーラーをダウンロードします
3. ダウンロードしたインストーラーを実行し、画面の指示に従ってインストールします
4. インストール完了後、GitHub Desktop を起動します
5. GitHub アカウントでサインインします

![GitHub Desktop インストール](https://desktop.github.com/images/github-desktop-screenshot-windows.png)

## 基本的な Git ワークフロー

Git を使った基本的な作業の流れは以下の通りです：

1. **クローン（Clone）**: リポジトリをローカルにコピーする
2. **ブランチ作成（Branch）**: 作業用のブランチを作成する
3. **変更（Change）**: ファイルを編集する
4. **コミット（Commit）**: 変更を記録する
5. **プッシュ（Push）**: 変更をリモートリポジトリに送信する
6. **プルリクエスト（Pull Request）**: 変更を本流に取り込むよう依頼する

以下では、それぞれの操作を GitHub Desktop と VS Code を使って行う方法を説明します。

## 1. リポジトリのクローン

リポジトリをクローンするとは、GitHub 上のリポジトリを自分のコンピュータにコピーすることです。

### GitHub Desktop でクローンする方法

1. GitHub Desktop を起動します
2. 「File」メニューから「Clone Repository」を選択します
3. 「URL」タブを選択します
4. リポジトリの URL（例：`https://github.com/SRWS-PSG/writing_with_ai.git`）を入力します
5. ローカルパスを選択します（クラウドストレージと同期しているフォルダは避けてください）
6. 「Clone」ボタンをクリックします

![リポジトリのクローン](../_assets/git_clone.png)

## 2. ブランチの作成

ブランチを作成すると、メインの開発ラインから分岐して作業できます。これにより、メインブランチに影響を与えずに変更を加えることができます。

### GitHub Desktop でブランチを作成する方法

1. GitHub Desktop で、「Current Branch」ボタンをクリックします
2. 表示されるドロップダウンメニューから「New Branch」ボタンをクリックします
3. 新しいブランチの名前を入力します（例：`feature/add-new-template`）
4. 「Create Branch」ボタンをクリックします

![ブランチの作成](../_assets/git_branch.png)

## 3. ファイルの変更

ブランチを作成したら、VS Code でファイルを編集します。

### VS Code でファイルを編集する方法

1. GitHub Desktop の「Open in Visual Studio Code」ボタンをクリックします
2. VS Code が起動し、リポジトリのファイルが表示されます
3. 編集したいファイルをクリックして開きます
4. 必要な変更を加えます
5. 「ファイル」メニューから「保存」を選択するか、Ctrl+S（Windows）または Command+S（macOS）を押して変更を保存します

![ファイルの編集](../_assets/git_edit.png)

## 4. 変更のコミット

変更を加えたら、その変更をコミットします。コミットとは、変更を Git の履歴に記録することです。

### GitHub Desktop で変更をコミットする方法

1. GitHub Desktop に戻ります
2. 左側のパネルに変更したファイルが表示されます
3. 変更内容を確認します
4. 左下の「Summary」欄にコミットメッセージを入力します（例：「テンプレートを追加」）
5. 必要に応じて「Description」欄に詳細な説明を入力します
6. 「Commit to [ブランチ名]」ボタンをクリックします

![変更のコミット](../_assets/git_commit.png)

## 5. 変更のプッシュ

コミットした変更をリモートリポジトリ（GitHub）に送信します。

### GitHub Desktop で変更をプッシュする方法

1. コミット後、「Push origin」ボタンをクリックします
2. これにより、ローカルの変更が GitHub に送信されます

![変更のプッシュ](../_assets/git_push.png)

## 6. プルリクエストの作成

変更が完了したら、プルリクエスト（Pull Request）を作成して、変更をメインブランチに取り込むよう依頼します。

### GitHub Desktop でプルリクエストを作成する方法

1. 変更をプッシュした後、「Create Pull Request」ボタンをクリックします
2. ブラウザが開き、GitHub のプルリクエスト作成ページが表示されます
3. プルリクエストのタイトルと説明を入力します
4. 「Create pull request」ボタンをクリックします

![プルリクエストの作成](../_assets/git_pr.png)

## よくある質問

### Q: コミットを間違えてしまった場合はどうすればいいですか？

A: GitHub Desktop の「History」タブで右クリックし、「Undo last commit」を選択すると、最後のコミットを取り消すことができます。

### Q: 他の人の変更を取り込むにはどうすればいいですか？

A: GitHub Desktop の「Fetch origin」ボタンをクリックし、その後「Pull origin」ボタンをクリックすると、リモートリポジトリの最新の変更を取り込むことができます。

### Q: ブランチを切り替えるにはどうすればいいですか？

A: GitHub Desktop の「Current Branch」ボタンをクリックし、切り替えたいブランチを選択します。

## 次のステップ

Git の基本的な操作方法を理解したら、[README.md](../README.md)に戻り、実際に論文執筆を始めましょう。より詳細な Git の使い方については、[GitHub Desktop ドキュメント](https://docs.github.com/ja/desktop)を参照してください。
