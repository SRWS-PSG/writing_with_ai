---
name: fetch_gdoc_changes
description: Fetch tracked changes (suggestions) and comments from a Google Doc via rclone, without using a browser.
---

# Fetch Google Doc Track Changes & Comments via rclone

Google ドキュメントの「変更提案 (suggestion)」と「コメント」を、ブラウザを開かずに取得する手順。
DOCX としてエクスポートすると、現在オープン中の suggestion は Word のトラック変更 (`w:ins` / `w:del`) として、コメントは `comments.xml` として保持されるので、それをローカルでパースする。

## 前提条件

- `rclone` がインストール済みで、`gdrive:` リモートが設定されていること
- Python 3 が利用可能であること（標準ライブラリのみで動作）
- 対象 Google Doc のファイル ID（URL `https://docs.google.com/document/d/<FILE_ID>/edit` の `<FILE_ID>` 部分）

## 実行手順

### 1. DOCX としてエクスポート

ファイル ID を直接指定して落とす:

```bash
mkdir -p /c/tmp/gdoc_changes
rclone backend copyid gdrive: \
  <FILE_ID> \
  /c/tmp/gdoc_changes/ \
  --drive-export-formats docx
```

または、Drive 内のパスがわかっているなら:

```bash
rclone copy "gdrive:path/to/doc" /c/tmp/gdoc_changes/ \
  --drive-export-formats docx
```

エクスポートされた `<docname>.docx` には、開いている suggestion がトラック変更として、コメントも併せて含まれる。

### 2. DOCX をパースして変更とコメントを抽出

コミット済みのスクリプト [`scripts/parse_docx_changes.py`](scripts/parse_docx_changes.py)
(stdlib のみで動作) を実行する。`report.md` と `report.json` を書き出す。
スクリプトを保存し直す必要はない。

引数は `<docx> [<report_dir>]`。**第 2 引数 (出力先フォルダ) は省略可**で、
省略すると DOCX と同じディレクトリに書く。

```bash
# 省略時: DOCX と同じフォルダに report.md / report.json を書く
python skills/fetch_gdoc_changes/scripts/parse_docx_changes.py /c/tmp/gdoc_changes/draft.docx

# 出力先を指定する場合 (共著者レビューのラウンドごとに分けたいときなど)
python skills/fetch_gdoc_changes/scripts/parse_docx_changes.py \
  /c/tmp/gdoc_changes/draft.docx projects/<name>/review/v1
```

出力先を明示的に分けるのは、`tracked_revision` Skill の Step 5 (送付前検証) の
ように**入力の report.json を上書きしたくない**場合。レビュー取り込み用の
`review/vN/` と検証用の `output/vN/check/` を別フォルダにする。

スクリプトの中身: `w:ins` / `w:del` (トラック変更) を段落コンテキスト付きで、
`comments.xml` (コメント) を `commentRangeStart/End` 由来のアンカーテキスト
付きで抽出する。

## 取得できるもの / 取得できないもの

| 対象 | rclone + DOCX で取れる? | 補足 |
|---|---|---|
| 現在オープン中の suggestion（trackあり編集） | ✅ | `w:ins` / `w:del` |
| 現在のコメント本文・著者・日時 | ✅ | `comments.xml` |
| コメントのアンカーテキスト | ✅ | `commentRangeStart` / `commentRangeEnd` |
| Accept/Reject 済を含む全リビジョン履歴 | ❌ | Drive `revisions.list` API が必要 |
| コメントの返信スレッド構造 | △ | DOCX には返信もまとまって入るが構造は浅い。完全な木構造は Drive `comments`/`replies` API |

## 注意事項

- `--drive-export-formats docx` は **エクスポート** 用のフラグ（Google Doc → DOCX）。アップロード時の `--drive-import-formats docx` とは別物なので混同しない。
- Google Docs では「すでに accept した変更」は track changes として残らないため、DOCX 経由では取得できない。レビュー前の生の suggestion を保全したいなら、レビュアーが accept する前に取得する運用にする。
- 出力 `report.md` をそのままレビューコメントの一覧として AI への入力に使える。

## コメントに返答して v2 を返すとき

このスキルは取得だけを行う。コメント 1 件ごとの対応表を作り、`draft.md` を直し、
変更履歴 + 元コメント + 返答入りの docx を新しい Google Doc としてアップロードする
一連の流れは `tracked_revision` Skill (`skills/tracked_revision/SKILL.md`) を使う。

「すでに accept した変更」も含めて、変更履歴の外で本文が直接書き換えられていないかを
確認したい場合は、`tracked_revision` Skill 付属の
[`scripts/check_direct_edits.py`](../tracked_revision/scripts/check_direct_edits.py)
(`--reviewed-docx` にこのスキルでエクスポートした DOCX、`--snapshot` にレビューへ
出した時点の Markdown を渡す) を使う。
