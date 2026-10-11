# 環境チェック (AIへの指示)

WS当日の冒頭で使う。IDEで本リポジトリを開いた状態で、AIチャットに次のように依頼する。

> `@env_check.md` を読んで、私のPC環境を順に確認してください。

AIはOS判定→必須ツール確認→不足分のインストール手順提案、までをこのファイルの指示に沿って実行する。

---

## AIへの依頼 (このセクションを順に実行)

### 1. OS判定

OSを判定し、結果を1行で宣言する。

- **Windows** の場合: `$PSVersionTable.OS` または `systeminfo | findstr /B /C:"OS Name"` を実行
- **macOS** の場合: `uname -sr` を実行
- それ以外 (Linux等) はサポート対象外として、Windows / macOS のどちらに近いか確認しつつユーザーに判断を仰ぐ

### 2. 必須ツールの確認

以下のコマンドを順に実行し、それぞれのバージョン (1行目で十分) を報告する。コマンドが見つからない場合は「未インストール」と報告する。

| 項目 | 確認コマンド | 必須度 |
|------|--------------|--------|
| pandoc | `pandoc --version` | **必須** |
| git | `git --version` | 推奨 |
| rclone | `rclone version` | 推奨 |

#### インストール直後の「偽陰性」に注意 (pandoc)

`pandoc --version` が「未インストール」と出ても**即断しない**。インストール直後は、すでに起動しているシェル (AI のツールセッションや IDE 内ターミナル) が新しい PATH を拾えておらず、入っているのに見つからないことがある。「未インストール」と報告する前に、AI は次を順に試す。

**Windows:**

- (a) 現セッションの PATH をレジストリから再読込する (シェルを閉じずに反映)。

  ```powershell
  $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
  pandoc --version
  ```

- (b) それでも見つからなければ既知のインストール先を直接探索し、見つかればフルパスで実行する。

  ```powershell
  @("$env:ProgramFiles\Pandoc\pandoc.exe","$env:LOCALAPPDATA\Pandoc\pandoc.exe","$env:LOCALAPPDATA\Microsoft\WinGet\Links\pandoc.exe") | Where-Object { Test-Path $_ }
  # 見つかったパスで:  & "<path>" --version
  ```

**macOS:**

- (a) Homebrew の環境を現シェルに反映する (Apple Silicon / Intel 両対応)。

  ```bash
  if [ -x /opt/homebrew/bin/brew ]; then eval "$(/opt/homebrew/bin/brew shellenv)"; \
  elif [ -x /usr/local/bin/brew ]; then eval "$(/usr/local/bin/brew shellenv)"; fi
  pandoc --version
  ```

- (b) それでも見つからなければ既知のインストール先を直接探索し、見つかればフルパスで実行する。

  ```bash
  for p in /opt/homebrew/bin/pandoc /usr/local/bin/pandoc; do [ -x "$p" ] && echo "$p"; done
  # 見つかったパスで:  <path> --version
  ```

(a) または (b) で動いた場合は「**インストール済みだが PATH 未反映**」として切り分けて報告する (下記サマリー参照)。

### 3. rclone × Google Drive 接続確認 (rclone がインストール済みの場合のみ)

`rclone version` が通った場合、以下を順に実行する。`rclone` 自体が未インストールの場合はこのステップを丸ごとスキップする。

1. `rclone listremotes` — 設定済みリモート一覧を取得し、`gdrive:` (または相当する Google Drive リモート) があるか確認する。
2. `gdrive:` がある場合: `rclone lsd gdrive:` を実行して接続が生きているかを確認する (トップ階層のフォルダ一覧が返れば OK)。エラーが出た場合は短く報告するのみで、深追いしない。
3. `gdrive:` が無い場合: 参加者に **「これからブラウザを起動して Google Drive の認証を行います。ブラウザが開いたら Google アカウントで『許可』を押してください」と一言伝えた上で**、AI が次の一発コマンドを実行する。

   ```powershell
   rclone config create gdrive drive scope=drive
   ```

   - rclone が自動でローカル Web サーバを起動し、ブラウザで Google OAuth 画面を開く。参加者はブラウザ上で「許可」を押すだけ。ターミナル操作は不要。
   - コマンドが正常終了したら `rclone lsd gdrive:` を実行して動作確認する。
   - 60 秒以上応答が無い、またはエラーで終了した場合は深追いせず「未設定のまま」と報告し、講師画面のデモ案内に切り替える。

### 4. 不足分のインストール提案

未インストールのツールがある場合のみ、下記「インストール手順」のうち該当OS・該当ツールの手順を **提示する**。**自動でインストールを実行しない** (参加者が読んで実行可否を判断する)。

すでに入っている場合は「OK」と短く返し、インストール手順は提示しない。

### 5. 結果サマリー

最後に、以下のフォーマットで結果を報告する。

```text
OS:            <Windows 11 | macOS 14.5 | ...>
pandoc:        <2.x.x | インストール済みだが PATH 未反映 → シェル/ターミナル(または IDE)再起動が必要 | 未インストール → 手順を上に提示>
git:           <2.x.x | 未インストール → 手順を上に提示>
rclone:        <1.x.x | 未インストール → 手順を上に提示 / スキップ (任意)>
gdrive remote: <設定済み (接続OK) | 未設定 → 手順を上に提示 | スキップ (rcloneが無い場合)>
```

---

## インストール手順

### Windows: pandoc

**winget が使える場合 (推奨)**:

```powershell
winget install --id JohnMacFarlane.Pandoc -e
```

**Chocolatey が使える場合**:

```powershell
choco install pandoc -y
```

**それ以外**: <https://pandoc.org/installing.html> から `pandoc-X.Y-windows-x86_64.msi` をダウンロードしてインストール。

確認 (PowerShellを再起動してから):

```powershell
pandoc --version
```

> `pandoc` がコマンドとして見つからない場合、まず現在のシェルで PATH を再読込する。閉じて開き直す前に次のワンライナーを試すと、シェルを閉じずに反映できる。
>
> ```powershell
> $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
> pandoc --version
> ```
>
> それでも見つからなければ PowerShell を一度閉じて開き直す。IDE 内ターミナルを使っている場合は、IDE 自体を再起動しないと PATH が反映されないことがある。

### macOS: pandoc

**Homebrew が入っている場合 (推奨)**:

```bash
brew install pandoc
```

**Homebrew が入っていない場合**: まず Homebrew をインストール。

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

確認:

```bash
pandoc --version
```

> `pandoc` が見つからない場合、まず現在のシェルに Homebrew の環境を反映する (特に Apple Silicon は `/opt/homebrew/bin` が既存シェルの PATH に無い)。
>
> ```bash
> if [ -x /opt/homebrew/bin/brew ]; then eval "$(/opt/homebrew/bin/brew shellenv)"; \
> elif [ -x /usr/local/bin/brew ]; then eval "$(/usr/local/bin/brew shellenv)"; fi
> pandoc --version
> ```
>
> 恒久的に反映するには、`brew` が案内する `eval "$(... brew shellenv)"` の行を shell プロファイル (`~/.zprofile` など) に追記する。IDE 内ターミナル使用時は IDE 自体の再起動が必要なことがある。

### Windows: git

```powershell
winget install --id Git.Git -e
```

### macOS: git

`git --version` を初回実行すると Xcode Command Line Tools のインストールダイアログが出るので、そのまま進めれば入る。明示的に入れたい場合:

```bash
brew install git
```

### Windows: rclone

生成した `draft.docx` をコマンドラインから Google Drive にアップロード/同期するために使う。Web UI でも代替可能。

```powershell
winget install Rclone.Rclone
```

### macOS: rclone

```bash
brew install rclone
```

### rclone × Google Drive 初期設定 (パターンA: OAuth のみ)

個人利用・WS用途ならこれで十分。Client ID は rclone 内蔵の共有 ID を使うので、Google Cloud Console 側の設定は不要。

#### 推奨: 非対話モード (AI 経由・ターミナル操作なし)

AI が以下のコマンドを一発実行する。対話プロンプトは出ず、rclone が自動でブラウザを開いて OAuth 画面を表示するので、**参加者の操作はブラウザの「許可」クリックのみ**。

```powershell
rclone config create gdrive drive scope=drive
```

動作確認:

```powershell
rclone lsd gdrive:
rclone copy demo/output/draft.docx gdrive:writing_with_AI/
```

#### フォールバック: 手動の対話モード (AI を使わない場合)

AI 経由で上記が失敗した場合や、ドキュメントを後日 1 人で読みながらセットアップしたい場合に使う。

```text
rclone config
```

対話プロンプトでの選択:

1. `n` (New remote)
2. name: 任意 (例: `gdrive`)
3. Storage: `drive` (Google Drive) を選ぶ
4. **client_id**: 空欄のまま Enter
5. **client_secret**: 空欄のまま Enter
6. scope: `1` (Full access) でOK
7. service_account_file: 空欄
8. Edit advanced config: `n`
9. Use auto config: `y` → ブラウザが開くので Google アカウントで承認
10. Configure this as a Shared Drive: `n`
11. 確認画面で `y` → `q` で終了

> ⚠️ 共有 Client ID は全 rclone ユーザーで共用されているため、大量ファイル転送時に API レート制限 (`User Rate Limit Exceeded`) が出ることがある。頻繁に使うなら自前 Client ID 作成を推奨 → [rclone_advanced.md](rclone_advanced.md) を参照。

---

## 制約 (AIへ)

- **削除、初期化、不要なOS設定変更は提案しない**: このファイルに記載のないコマンド (`rm -rf`、`Remove-Item -Recurse`、レジストリ変更、`sudo` 不要な操作の `sudo` 化など) は提案しない
- **このファイルに記載のないパッケージを追加で提案しない**: pandoc / git / rclone 以外のインストール提案 (LaTeX, Node, Python など) は不要
- **管理者権限が必要な操作は明示する**: `sudo` や「管理者として実行」が必要なら、その旨を一言添える
- **インストールコマンドは自動実行しない**: `winget install ...` / `brew install ...` などのインストール系はユーザーに提示するだけにとどめ、`pandoc --version` のような **確認系コマンド** のみ実行する
- **PATH 再読込・既知パス探索は確認系として AI が実行してよい**: 現セッションの PATH 再読込ワンライナー (Windows の `$env:Path = ...` / macOS の `eval "$(... brew shellenv)"`)、既知インストール先の `Test-Path` 探索、フルパスでの `... --version` 実行は、いずれもインストールや設定変更を伴わない確認系なので AI が実行してよい。ただし shell プロファイルへの追記など**恒久的な設定変更は提示のみ**にとどめる
- **`rclone config create gdrive drive scope=drive` は AI が実行してよい**: 非対話の一発コマンドであり、参加者のターミナル操作を省略するために使う。**対話モードの `rclone config` (11 ステップのプロンプト) は AI が実行しない** (途中で停止すると復旧が面倒なため)
- **rclone OAuth のブラウザ承認は参加者必須**: 上記コマンドが rclone から自動でブラウザを開くが、Google アカウントでの「許可」クリック自体は AI が代行できない
- **rclone のクォータ/Client ID 自作 (パターンB) はこのファイルでは扱わない**: 質問されたら `rclone_advanced.md` を案内する
- **10分で `pandoc --version` が通らなければ深追いしない**: 個別環境の解決にこだわらず、講師画面のデモを追う案内に切り替える
