---
name: gdoc-review-roundtrip
description: Markdown 原稿から作った Google ドキュメントに付いたコメントへ返信しつつ、修正版を「提案（変更履歴）」つきの新しい Google ドキュメントとして渡す。「Google Docs のコメントに返信して」「コメント対応」「修正を提案モードで」「トラックつきで Google Doc にして」「共著者のコメントを反映して戻す」「変更履歴つきで Google ドキュメントに」などで使う。md の原稿と Google ドキュメントの URL がそろった文脈で、コメント対応や修正版の共有を頼まれたら必ずこの skill を使うこと。
---

# Google Docs コメント対応ラウンドトリップ

Google Docs API では「提案」を作れない。そこで **変更履歴＋コメント（返信スレッドつき）の docx を作り、Google ドキュメントに変換して取り込む**。
Google は docx の変更履歴を「提案」に、`commentsExtended.xml` の親子関係を返信スレッドに変換する（実地で確認済み）。

使うスクリプト:

- `scripts/gdoc_comments_from_docx.py` … Google Doc を書き出した docx から、コメントとスレッドを JSON にする
- `scripts/md_to_gdoc_review.py` … v1/v2 の md と コメント JSON から、変更履歴＋コメント返信入りの docx を作る

人向けの手順書は `tutorials/gdoc_review_roundtrip.md`。

## 手順

### 1. 材料をそろえる

- **Google ドキュメント**：URL の `/d/<fileId>/` から fileId を取る。
- **v1.md**（Google Doc にした時点の原稿）：`git log -- <原稿.md>` で Google Doc を作った頃のコミットを探し、`git show <commit>:<原稿.md> > v1.md` で取り出す。どのコミットか判断できなければユーザーに聞く。
- **v2.md**：修正後の原稿（通常は作業ツリーの最新版）。まだ修正していなければ、コメントを読んだうえで先に原稿を直す。

元の Google Doc に**共著者の未処理の提案**が残っていると、それは修正版に引き継がれない。あれば、先に承認・却下してもらうようユーザーに伝える。

### 2. コメントを取り出す

Google Drive コネクタの `download_file_content` で fileId を
`exportMimeType: application/vnd.openxmlformats-officedocument.wordprocessingml.document` で書き出す。
返ってきた base64 をスクラッチパッドにファイルとして保存してデコードし、JSON にする。

```bash
base64 -d export.b64 > export.docx
python3 scripts/gdoc_comments_from_docx.py export.docx -o comments.json
```

コネクタが使えない場合は、ユーザーに「ファイル → ダウンロード → Microsoft Word」で docx を書き出してもらう。
Drive API の `comments.list` の JSON でもよい（形式は同じ）。

### 3. 返信を書く

`comments.json` の各スレッドの `"reply"` に返信を書く。

- 何をどう直したかを v1→v2 の差分から具体的に書く。直さなかった場合は理由を書く。
- 返信はコメントと同じ言語で書く。
- 解決済み（`"resolved": true`）のスレッドは既定で出力しないので、返信は不要。
- 返信案は **docx を作る前に md の一覧（コメント／返信案の対応表）にしてユーザーに確認してもらう**。

### 4. docx を作る

```bash
python3 scripts/md_to_gdoc_review.py v1.md v2.md -c comments.json -o review.docx \
  --author "<ユーザーの名前>" -- --citeproc
```

`--` 以降は pandoc に渡る。原稿の YAML に `bibliography`/`csl` があれば `--citeproc` だけでよい。
`⚠️ コメント位置が見つからず…` と出たコメントは文書の先頭に付く。件数をユーザーに伝える。

### 5. Google ドキュメントにする

Google Drive コネクタの `create_file` で、`contentMimeType: application/vnd.openxmlformats-officedocument.wordprocessingml.document`、
`base64Content` に review.docx の base64 を入れてアップロードする（既定で Google ドキュメントに変換される）。
元の Doc と同じフォルダに置くなら `parentId` を指定する。タイトルは「<元のタイトル> v2（提案）」など。

できた Google ドキュメントの URL をユーザーに伝える。元の Doc とそのコメントはそのまま残ることも伝える。

## 動作の要点

- 差分は pandoc の AST で取る。英語は単語単位、日本語は文字単位。変更に挟まれた 1〜2 文字の一致は変更にまとめる。
- 半分以上書き直した段落、表やコードブロックの変更は「削除＋挿入」になる。
- コメントの位置は、コメントされた文字列を v1 側 → v2 側 → 先頭 40 文字の順で探して決める。
- 引用文献（`[@key]`）を含む箇所へのコメントは、引用番号との違いで位置合わせに失敗しやすい。
