# rclone × Google Drive アドバンスド設定

WS当日の最小セットアップは [env_check.md](env_check.md) を参照。このファイルは **事後** に rclone を本格運用したくなった人向けの追記資料。

## このファイルで扱うこと

- rclone 内蔵の共有 Client ID で発生する **API クォータ問題** の正体
- 自前 Client ID (パターンB) を Google Cloud Console で作る手順
- rclone への組み込み方
- トラブルシューティング

---

## クォータの話: なぜ自前 Client ID が必要になるか

### Google Drive API のクォータ構造

Google Drive API は **2 段階の制限** で守られている。

| 制限の種類 | 単位 | デフォルト上限 |
|------------|------|----------------|
| プロジェクト単位 | Queries per day | 1,000,000,000 (10億) |
| プロジェクト単位 | Queries per 100 seconds | 20,000 |
| **ユーザー単位** | Queries per 100 seconds **per user** | **12,000** |

ここで言う「プロジェクト」とは **Google Cloud Console で作るプロジェクト = Client ID の出処** のこと。

### パターンA (OAuth のみ) で何が起きるか

rclone をデフォルト設定で使うと、**世界中の rclone ユーザー全員が同じ Client ID** (Nick Craig-Wood 氏が rclone 公式として登録したもの) を共有している。

つまり:

- **「プロジェクト単位の 100秒あたり 20,000 クエリ」を全 rclone ユーザーで取り合っている**
- 自分は何も悪くなくても、他のユーザーの大量転送に巻き込まれてレート制限に当たる
- 症状: `User Rate Limit Exceeded` や `403: rateLimitExceeded` が頻発し、転送が遅くなる/失敗する

### パターンB (自前 Client ID) の効果

自分専用のプロジェクトを作って Client ID を発行すれば:

- プロジェクト単位のクォータ (1日 10億クエリ・100秒で 20,000 クエリ) を **自分だけで使える**
- ユーザー単位の 12,000/100秒 は変わらないが、これに当たることは普通ない
- 数十GB単位の同期でも詰まらず流れる

### コスト

**完全無料**。Google Cloud Console プロジェクトを作るだけで課金は発生しない (Drive API は無料枠のみ)。クレジットカード登録も不要。

---

## 自前 Client ID 作成手順 (パターンB)

### 0. 前提

- Google アカウント (個人の Gmail でOK)
- ブラウザ

### 1. Google Cloud プロジェクト作成

1. <https://console.cloud.google.com/> にアクセス
2. 画面上部のプロジェクト選択メニュー → 「**新しいプロジェクト**」
3. プロジェクト名: 任意 (例: `rclone-personal`)
4. 組織: なし (個人なら) / 該当組織
5. 「作成」 → プロジェクトが選択された状態にする

### 2. Google Drive API を有効化

1. 左メニュー → 「**APIとサービス**」 → 「**ライブラリ**」
2. 検索バーで `Google Drive API` を検索
3. クリックして 「**有効にする**」

### 3. OAuth 同意画面の設定

1. 左メニュー → 「**APIとサービス**」 → 「**OAuth 同意画面**」
2. User Type: **外部** を選択 → 作成
3. アプリ名: 任意 (例: `rclone`)
4. ユーザーサポートメール: 自分のメール
5. デベロッパー連絡先情報: 自分のメール
6. 「保存して次へ」
7. **スコープ** 画面: 何も追加せず「保存して次へ」(rclone 側で要求する)
8. **テストユーザー** 画面: 「+ ADD USERS」で **自分の Gmail アドレスを追加**
9. 「保存して次へ」 → 概要を確認して完了

> ℹ️ アプリは「テストモード」のままでOK。公開審査は不要。テストモードでも自分(テストユーザー)は使える。ただし `7日間でリフレッシュトークン失効` の制約があるバージョンと、未公開アプリでも失効しないバージョンがあるので、トークン切れが起きたら `rclone config reconnect gdrive:` で再認証する。

### 4. OAuth クライアント ID 作成

1. 左メニュー → 「**APIとサービス**」 → 「**認証情報**」
2. 「**+ 認証情報を作成**」 → 「**OAuth クライアント ID**」
3. アプリケーションの種類: **デスクトップアプリ**
4. 名前: 任意 (例: `rclone-desktop`)
5. 「作成」 → ダイアログで **クライアント ID** と **クライアントシークレット** が表示される
6. **両方コピーして保存** (後で見返せるが、最初にメモしておくとラク)

---

## rclone への組み込み

### 既存のリモートを更新する場合

```powershell
rclone config
```

1. `e` (Edit existing remote)
2. リモート名 (例: `gdrive`) を選択
3. `client_id`: コピーしておいた **Client ID** を貼り付け
4. `client_secret`: コピーしておいた **Client Secret** を貼り付け
5. 残りはそのままで OK
6. **再認証が必要**: `y` → ブラウザで承認
7. `q` で終了

### 新規リモートを作る場合

[env_check.md](env_check.md) のパターンA手順と同じ流れだが、**Step 4-5 で空欄ではなく Client ID/Secret を入力する**。

### 設定ファイルを直接編集してもOK

rclone の設定ファイルの場所:

```powershell
rclone config file
```

該当行を編集:

```ini
[gdrive]
type = drive
client_id = xxxxxxxxxxxxxxxx.apps.googleusercontent.com
client_secret = GOCSPX-xxxxxxxxxxxxxx
scope = drive
token = {"access_token":"..."}
```

`token` は次回コマンド実行時に自動で更新される。手動で編集後は `rclone config reconnect gdrive:` でトークン再取得を推奨。

---

## 動作確認とトラブルシューティング

### 正常動作の確認

```powershell
rclone lsd gdrive:
rclone about gdrive:
```

`about` でクォータ表示が出れば API は正しく叩けている。

### よくあるエラー

| エラー | 原因 | 対処 |
|--------|------|------|
| `Error 403: Access blocked: ... has not completed the Google verification process` | OAuth 同意画面のテストユーザーに自分を追加していない | 手順3-8でテストユーザー追加 |
| `Token has been expired or revoked` | テストモードでトークン失効 (7日) | `rclone config reconnect gdrive:` |
| `403: rateLimitExceeded` が **自前ID でも** 出る | ユーザー単位制限 (12,000/100秒) に到達 | `--tpslimit 10 --transfers 4` で速度抑制 |
| `403: userRateLimitExceeded` | 同上 | 同上 |
| `invalid_client` | Client ID/Secret の入力ミス | rclone config で再入力 |

### 速度チューニング

```powershell
rclone copy demo/output/ gdrive:writing_with_AI/ `
  --transfers 8 `
  --checkers 16 `
  --tpslimit 10 `
  --drive-chunk-size 64M `
  --progress
```

- `--transfers`: 並列アップロード数
- `--checkers`: 並列ファイルチェック数
- `--tpslimit`: 秒あたりの API 呼び出し上限 (10 = 1000/100秒、ユーザー制限 12000/100秒 内に収まる)
- `--drive-chunk-size`: チャンクサイズ。大きいほど大ファイル転送が速い (メモリも食う)

---

## セキュリティの注意

- Client ID 自体は半公開情報だが、**Client Secret は他人に渡さない**。GitHub などに rclone 設定ファイルをコミットしない (`~/.config/rclone/rclone.conf` または `%APPDATA%\rclone\rclone.conf`)
- `rclone config show` で設定が画面に出る。スクリーンショット共有時は注意
- 暗号化したい場合は `rclone config` の Advanced で `--rc-pass` パスワードを設定可能

---

## 参考リンク

- rclone 公式: Google Drive 設定ガイド <https://rclone.org/drive/>
- 自前 Client ID 作成手順 (rclone 公式): <https://rclone.org/drive/#making-your-own-client-id>
- Google Drive API クォータ: <https://developers.google.com/drive/api/guides/limits>
- OAuth 同意画面の公開ステータス: <https://support.google.com/cloud/answer/10311615>
