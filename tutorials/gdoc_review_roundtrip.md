# Google Docs のコメントに返信しながら、修正を「提案」として渡す

Markdown から作った Google ドキュメントに共著者がコメントを付けたあと、
修正版を **変更履歴（提案モード）＋コメントへの返信つき** の Google ドキュメントとして渡す手順です。

Google Docs API では「提案」を作れないため、変更履歴とコメントの入った Word ファイル（docx）を作り、
それを Google ドキュメントに変換します。変換すると、変更履歴は「提案」、コメントは返信つきのスレッドになります。

```
v1 の Google Doc（コメント付き）
   │ ① コメントを JSON で取得し、返信を書き足す
   ▼
paper_v1.md ──② 差分──> paper_v2.md
   │ ③ scripts/md_to_gdoc_review.py
   ▼
review.docx（変更履歴＋コメント＋返信）
   │ ④ Google ドライブに「Google ドキュメントとして」アップロード
   ▼
v2 の Google Doc（提案モード＋返信つきコメント）
```

## 1. 前回の Markdown（v1）を用意する

Google Docs にしたときの版をコミットしておくと、あとで取り出せます。

```bash
git show <そのときのコミット>:paper.md > paper_v1.md
```

## 2. コメントを JSON で取得する

Drive API の `comments.list` の結果をそのまま使います。

```bash
FILE_ID=<Google ドキュメントの URL の /d/ と /edit の間の文字列>
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/drive/v3/files/$FILE_ID/comments?pageSize=100&fields=comments(id,content,author/displayName,createdTime,resolved,deleted,quotedFileContent,replies(content,author/displayName,createdTime,deleted))" \
  > comments.json
```

`$TOKEN` は [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/) で
`https://www.googleapis.com/auth/drive.readonly` を許可すると取得できます。
API を使わずに、Claude（Google Drive コネクタ）にコメントの取得と JSON 化を頼むこともできます。

## 3. 返信を書き足す

`comments.json` の各コメントに `"reply"` を追加します。これがスレッドの最後の返信になります。

```json
{
  "comments": [
    {
      "content": "Cite a reference here.",
      "author": {"displayName": "Reviewer A"},
      "quotedFileContent": {"value": "common cause of death in the ICU"},
      "replies": [{"content": "Agree.", "author": {"displayName": "Reviewer B"}}],
      "reply": "参考文献を追加し、表現を修正しました。"
    }
  ]
}
```

- すでに付いている返信（`replies`）もそのままスレッドに残ります。
- 解決済み（`"resolved": true`）のコメントは既定では入れません。入れる場合は `--include-resolved` を付けます。

## 4. docx を作る

```bash
python3 scripts/md_to_gdoc_review.py paper_v1.md paper.md \
  -c comments.json -o review.docx --author "Yuki Kataoka" \
  -- --citeproc --bibliography references.bib --csl vancouver-brackets.csl
```

- `--author` は変更履歴と返信の作成者名です（Google アカウントとは結び付きません）。
- `--` 以降は pandoc にそのまま渡されます（引用文献の設定や `--reference-doc` など）。
- コメントの位置は、コメントされた文字列（`quotedFileContent`）を v1 の本文から探して決めます。
  見つからなかったコメントは文書の先頭に付け、本文の頭に `[元の箇所が見つかりません: …]` と書き添えます。

## 5. Google ドキュメントにする

Google ドライブに `review.docx` をアップロードし、右クリック →「アプリで開く」→「Google ドキュメント」で開きます
（設定の「アップロードしたファイルを Google ドキュメント エディタ形式に変換する」をオンにしておくと自動で変換されます）。

変換後は次のようになります。

- 変更は **提案** として表示され、共著者が 1 件ずつ承認・却下できます。
- コメントは元のコメント → これまでの返信 → あなたの返信、の順でスレッドになります。

## 注意点

- できあがるのは **新しい Google ドキュメント** です。元のドキュメントのコメントはそのまま残ります。
- 差分は段落ごと・単語ごとに取ります。半分以上書き直した段落は、段落ごと「削除＋挿入」になります。
- 表やコードブロックが変わった場合は、まるごと「削除＋挿入」になります。
- 引用文献（`[@key]`）は pandoc の `--citeproc` で番号に変わるので、コメントの文字列に引用番号が含まれていると位置合わせに失敗することがあります（その場合は先頭 40 文字で探し直します）。
