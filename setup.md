# 自分専用の執筆リポジトリを作る (AIへの指示)

実践編の冒頭で使う。IDEで本リポジトリ (道具箱) を開いた状態で、AIチャットに次のように依頼する。

> `@setup.md` を読んで、私用の執筆リポジトリを作ってください。

AIは、GitHub に自分専用の **private リポジトリ** (以下「親リポジトリ」) を作り、その中に本リポジトリを **git submodule** として `writing_with_ai/` に取り込むところまで、このファイルの指示に沿って実行する。

できあがる形:

```text
my-writing/                 # 親リポジトリ (private)。原稿はここに書く
├── CLAUDE.md               # 親リポジトリ用の AI 向けメモ
├── AGENTS.md
├── .gitignore
├── projects/<名前>/        # 実際の原稿
└── writing_with_ai/        # 公開の道具箱 (submodule)。ここは読むだけ
```

一言でいうと、**道具は公開の submodule から読み、原稿は自分の private リポジトリに書く**。

---

## 前提

- `env_check.md` を実施済みで、`git` と `pandoc` が入っている。
- GitHub のアカウントを持っている。
- 本リポジトリは参考として開いているだけ。新しいリポジトリは、**本リポジトリのフォルダの中ではなく、別のフォルダ**に作る。**クラウド同期フォルダ (OneDrive / Google Drive / Dropbox / iCloud) の中にも作らない** (同期と git が競合して壊れることがあるため)。

---

## AIへの依頼 (このセクションを順に実行)

### 0. 参加者に最初に聞くこと (まとめて1回だけ聞く)

1. 新しいリポジトリの名前 (提案: `my-writing`。半角の英字・数字・ハイフンのみ)
2. 作成先の親フォルダ (提案: `codes` または `Documents` の下のフォルダ。クラウド同期の外)

答えが返ってから手順に進む。以降、リポジトリ名を `<name>`、親フォルダを `<親フォルダ>` と書く。

### 1. GitHub CLI の確認

```text
gh --version
```

バージョンが出れば OK。見つからない場合は、下記「インストール手順」の該当OSのコマンドを**提示して**、参加者がインストールを終えるまで先に進まない。

### 2. GitHub へのログイン確認

```text
gh auth status
```

ログイン済みなら手順3へ。未ログインなら、参加者に **「これからブラウザが開きます。画面に出るワンタイムコードを入力して『承認』を押してください」と一言伝えた上で**、AI が次を実行する。

```text
gh auth login --hostname github.com --git-protocol https --web
```

- ターミナルにワンタイムコードが表示され、ブラウザが開く。参加者がコードを入力して承認する (この部分は AI が代行できない)。
- 終わったら、もう一度 `gh auth status` を実行してログインできたことを確認する。

続けて、コミットに記録される名前とメールアドレスが設定されているかを確認する (未設定だと手順7の `git commit` が `Please tell me who you are` で失敗する)。

```text
git config --global user.name
git config --global user.email
```

どちらかが空なら、参加者に使う名前とメールアドレスを聞いてから設定する。AI が名前やアドレスを推測して入れない。

```text
git config --global user.name "<名前>"
git config --global user.email "<メールアドレス>"
```

### 3. private リポジトリの作成とクローン

作成先の親フォルダに移動してから実行する。

```text
cd <親フォルダ>
gh repo create <name> --private --clone
cd <name>
```

`<name>` フォルダが作られ、その中に入ったことを確認する。

### 4. 公開範囲の確認 (ここを通らなければ進まない)

```text
gh repo view --json visibility,nameWithOwner
```

`visibility` が `PRIVATE` のときだけ手順5へ進む。`PRIVATE` 以外だった場合は、**何も push せずに止まり**、参加者に状況を伝える。

### 5. 道具箱を submodule として追加

```text
git submodule add https://github.com/SRWS-PSG/writing_with_ai.git writing_with_ai
```

`writing_with_ai/` フォルダができ、`.gitmodules` が作られたことを確認する。

### 6. 親リポジトリ用のひな形をコピー

`writing_with_ai/templates/private_repo/` にあるひな形を、新しいリポジトリの直下にコピーする。`gitignore` は先頭にドットの付かない名前で置いてあるので、`.gitignore` に名前を変えてコピーする。あわせて `projects/.gitkeep` (空ファイル) を作る。

**PowerShell:**

```powershell
Copy-Item writing_with_ai/templates/private_repo/CLAUDE.md CLAUDE.md
Copy-Item writing_with_ai/templates/private_repo/AGENTS.md AGENTS.md
Copy-Item writing_with_ai/templates/private_repo/gitignore .gitignore
New-Item -ItemType Directory -Force projects | Out-Null
New-Item -ItemType File projects/.gitkeep | Out-Null
```

**macOS / bash:**

```bash
cp writing_with_ai/templates/private_repo/CLAUDE.md CLAUDE.md
cp writing_with_ai/templates/private_repo/AGENTS.md AGENTS.md
cp writing_with_ai/templates/private_repo/gitignore .gitignore
mkdir -p projects
touch projects/.gitkeep
```

### 7. コミットと push

`git add -A` や `git add .` は使わず、パスを指定して追加する。

```text
git add .gitmodules writing_with_ai CLAUDE.md AGENTS.md .gitignore projects/.gitkeep
git commit -m "Add writing_with_ai submodule and repository templates"
git push -u origin HEAD
```

ブランチ名 (`main` など) は決め打ちしない。`git push` がエラーになったら、エラーの文面を報告して止まる。

### 8. citeguard の確認

```text
citeguard --version
```

バージョンが出れば OK。見つからない場合は、参加者に「引用チェックのツール (citeguard) を入れてよいか」を**1回だけ**聞き、了承が得られたら次を実行する。

```text
pip install citeguard
```

### 9. 最終確認

```text
git submodule status
gh repo view --json visibility
```

- `git submodule status` の出力に `writing_with_ai` が含まれる。
- `visibility` が引き続き `PRIVATE` である。

### 10. 結果サマリー

以下のフォーマットで報告する。

```text
リポジトリ:       <owner/name>
公開範囲:         <PRIVATE | PRIVATE 以外 → 手順4で停止>
submodule:        <writing_with_ai のコミット (git submodule status の先頭の ID)>
citeguard:        <0.x.x | 未インストール → 参加者が見送り>
ローカルのフォルダ: <作成したフォルダの絶対パス>
```

### 11. 参加者に必ず伝える3点 (最後に、やさしい言葉で)

1. **private にしても、AI に見せた本文は AI の提供元に送られる。** GitHub で他人に見えないことと、AI 事業者に渡ることは別の話。学習に使われるかどうかは、使っている AI の設定と契約で決まる。患者情報を含む原稿は、所属施設の規程に従う。
2. **原稿は `projects/<名前>/` に書く。** `writing_with_ai/` の中には書かない。そこは公開リポジトリの写しで、道具を読む場所。
3. **道具を新しくするとき**は、`git submodule update --remote writing_with_ai` を実行したあと、親リポジトリで `git add writing_with_ai` してコミットする。**別の PC に持っていくとき**は、`git clone --recurse-submodules <自分のリポジトリのURL>` を使う。

---

## インストール手順

### Windows: GitHub CLI

```powershell
winget install --id GitHub.cli
```

### macOS: GitHub CLI

```bash
brew install gh
```

確認 (インストール後、ターミナルまたは IDE を開き直してから):

```text
gh --version
```

> インストール直後は、すでに起動しているシェルが新しい PATH を拾えず、入っているのに `gh` が見つからないことがある。`env_check.md` の pandoc と同じ扱いで、まず現在のシェルの PATH を再読込する。
>
> **Windows (PowerShell):**
>
> ```powershell
> $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
> gh --version
> ```
>
> **macOS:** Homebrew の環境を現シェルに反映する。
>
> ```bash
> if [ -x /opt/homebrew/bin/brew ]; then eval "$(/opt/homebrew/bin/brew shellenv)"; \
> elif [ -x /usr/local/bin/brew ]; then eval "$(/usr/local/bin/brew shellenv)"; fi
> gh --version
> ```
>
> それでも見つからなければ、ターミナルを一度閉じて開き直す。IDE 内ターミナルを使っている場合は、IDE 自体を再起動しないと PATH が反映されないことがある。

---

## 制約 (AIへ)

- **リポジトリを public にする操作は絶対に実行しない**: `gh repo edit --visibility ...` や `gh repo create --public` など
- **リポジトリを削除しない**
- **force push をしない**
- **`writing_with_ai/` の中ではコミットも push もしない**: そこは公開リポジトリの写しで、道具を読む場所
- **`git add -A` / `git add .` を使わない**: 追加するファイルはパスで指定する
- **秘密情報や `.env` ファイルをリポジトリに入れない**
- **手順2のブラウザでの承認は参加者の操作**: AI は代行できない
- **どこかの手順が失敗したら、エラーの文面をそのまま報告して止まる**: 同じ効果を持つ別のコマンドに切り替えて続行しない
- **このファイルに記載のないものをインストールするよう提案しない**: GitHub CLI と citeguard 以外は不要
