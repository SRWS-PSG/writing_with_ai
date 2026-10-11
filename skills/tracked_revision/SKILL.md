---
name: tracked_revision
description: Turn co-author comments on a Google Doc into a point-by-point response table, revise the Markdown, and upload a v2 Google Doc that carries (1) tracked changes against the reviewed version, (2) the original comments, and (3) the author's reply to each comment.
---

# Tracked Revision Skill (コメント対応版を「対応表 + 変更履歴 + 元コメント+返答」で返す)

共著者がコメントした Google Doc に対して、

1. コメント 1 件 1 行の **対応表** (`response_table.md`) を作り、
2. Markdown 本文 (`draft.md`) を直し、
3. **前版に対する変更履歴 (Google Docs の「提案」) と、元のコメント + 返答が入った v2 Doc** を新規にアップロードする

ところまでを行う。「md を直して docx を作り直してアップロードして送る」と、共著者のコメントが消え、
どこを直したかも分からなくなる。この Skill はそれを防ぐための固定手順。

査読対応と同じ考え方 (コメント → 返事 → 修正箇所が本文で分かる) を共著者間でも使う。

## 前提条件

- `pandoc` が PATH にあること (docx の変更履歴とコメントは pandoc が書く)
- Python 3 (標準ライブラリのみ。追加パッケージ不要)
- `rclone` + `gdrive:` リモート (Google Doc の取得/アップロードに使う)
- コンソールは cp932 なので、Python を実行する前に一度 `$env:PYTHONUTF8="1"` を設定する

## フォルダ構成 (`projects/<name>/` 配下)

```text
projects/<name>/
├── draft.md                       # 作業中の本文 (常に最新版)
├── versions/
│   ├── versions.md                # 台帳 (versions_ledger.py が管理)
│   ├── draft.v1.md                # v1 としてアップロードした時点のスナップショット
│   └── draft.v2.md                # v2 としてアップロードした時点のスナップショット
├── review/
│   ├── v1/                        # v1 Doc に付いたレビュー (round 1)
│   │   ├── draft_v1_reviewed.docx
│   │   ├── report.md / report.json
│   │   └── response_table.md
│   └── v2/                        # v2 Doc に付いたレビュー (round 2)
│       └── ...
└── output/
    ├── v2/                        # round 1 の対応結果として作る v2
    │   ├── draft_v2_tracked.md
    │   ├── draft_v2_tracked.md.summary.md
    │   ├── draft_v2_tracked_<hash>.docx  # アップロードした実体 (ハッシュ付き)
    │   └── check/                 # 送付前の検証 (review/ の report を上書きしない)
    └── v3/                        # round 2 の対応結果
        └── ...
```

「round N」= `review/vN/` のレビューに対応して `output/v{N+1}/` を作り、v{N+1} として
アップロードすること。台帳の `versions/draft.vN.md` が round N の基準版になる。

## 0. アップロード手順 (v1 も v2 以降も共通)

`render_and_upload` で最初の v1 をアップロードするときも、この Skill で v2 以降を
アップロードするときも、**同じ手順**を使う。`versions_ledger.py` の `--help` と
docstring に手順の理由が書かれている。以下はリポジトリのルートから実行する前提で、
プロジェクトフォルダを変数 `$p` に入れておく (プロジェクト配下のファイルは常に
`$p/...`、Skill のスクリプトは `skills/...`、共有の体裁雛形/CSL は `demo/styles/...`)。

```powershell
$env:PYTHONUTF8="1"
$p = "projects/<name>"

# 1. レンダリング (v2 以降は Step 4 の make_tracked_md.py の出力を使う)
pandoc $p/output/v2/draft_v2_tracked.md --reference-doc demo/styles/reference.docx `
  --citeproc --bibliography $p/refs.bib `
  --csl demo/styles/american-medical-association.csl `
  --resource-path $p `
  -o $p/output/v2/draft_v2_tracked.docx

# 2. 内容ハッシュ付きのファイル名を作る (アップロード事故防止)
python skills/tracked_revision/scripts/versions_ledger.py name `
  --docx $p/output/v2/draft_v2_tracked.docx --stem draft_v2_tracked
# 例: draft_v2_tracked_1a2b3c4d.docx

# 3. その名前でコピーする
Copy-Item $p/output/v2/draft_v2_tracked.docx $p/output/v2/draft_v2_tracked_1a2b3c4d.docx

# 4. 台帳に無いか確認する (exit 3 = 既にアップロード済み。止める)
python skills/tracked_revision/scripts/versions_ledger.py check `
  --ledger $p/versions/versions.md --docx $p/output/v2/draft_v2_tracked_1a2b3c4d.docx

# 5. アップロード
rclone copy $p/output/v2/draft_v2_tracked_1a2b3c4d.docx gdrive:writing_with_AI/<name>/ `
  --drive-import-formats docx

# 6. 新しい Doc の ID を読む
rclone lsjson gdrive:writing_with_AI/<name>/ | Select-String "draft_v2_tracked_1a2b3c4d"

# 7. 台帳に記録する (exit 3 = doc_id が重複 = 既存 Doc を上書きした徴候。Drive を確認する)
python skills/tracked_revision/scripts/versions_ledger.py record `
  --ledger $p/versions/versions.md --version v2 `
  --md $p/draft.md --docx $p/output/v2/draft_v2_tracked_1a2b3c4d.docx `
  --doc-id <FILE_ID>
```

**なぜハッシュ付きファイル名と `check`/`record` が要るか**: 2026-09-13 に実測した通り、
同じファイル名の docx を `rclone copy` で同じ Drive フォルダに入れると、既存の
Google Doc が**同じファイル ID のまま**上書きされる。共著者が付けたコメントスレッドは
docx の内容から作り直されるため、アップロード後に Google Docs 上で追加されたコメントが
消える。ファイル名にハッシュを埋めれば別ファイルとして扱われ、事故が起きない。

**`--md` には必ずレンダリング元の素の `$p/draft.md` を渡す**。`*_tracked.md` (差分マーク付き)
を渡さない — `record` はここから次回比較用のスナップショット (`$p/versions/draft.vN.md`) を作る。

## 1. レビュー済み Doc を取得し、直接編集がないか確認する

`fetch_gdoc_changes` Skill の rclone コマンドで `$p/review/vN/` にエクスポートする
(`$p = "projects/<name>"`、リポジトリのルートから実行する)。

```powershell
python skills/fetch_gdoc_changes/scripts/parse_docx_changes.py `
  $p/review/v1/draft_v1_reviewed.docx $p/review/v1
```

`$p/review/v1/report.md` にコメントと提案 (suggestion) が並ぶ。続けて、変更履歴の外で
直接書き換えられた箇所がないか確認する。

```powershell
python skills/tracked_revision/scripts/check_direct_edits.py `
  --reviewed-docx $p/review/v1/draft_v1_reviewed.docx `
  --snapshot $p/versions/draft.v1.md
```

- exit 0: 変更履歴をすべて Reject すればスナップショットに一致する (直接編集なし)
- exit 2: 一致しない箇所がある (提案モードを使わずに直接書き換えた、または提案を
  承認済み)。表示された段落を著者に見せ、それぞれ**採用するか/しないか**を決めて、
  Step 2 の対応表に ID の無い行として追加する (report.json 由来のコメント ID とは
  別枠なので、アンカー列に検出された段落の要約を書けばよい)
- **round 1 (`$p/versions/draft.v1.md` が基準) だけ**この比較が成立する。round 2 以降は
  アップロードした Doc 自体に自分たちの提案 (v1→v2 の変更履歴) が乗っているため、
  「すべて Reject」しても `draft.v2.md` には戻らない (v1 まで戻ってしまう)。round 2
  以降の直接編集チェックは手作業で行う (「制限事項」参照)。

## 2. コメント対応表を作る (AI が下書き、著者が確認)

`$p/review/vN/report.md` を読ませて、`$p/review/vN/response_table.md` を次の形式で書く。
**列名は固定**: `ID | 区分 | アンカー | コメント要旨 | 対応 | 返答`。
`make_tracked_md.py` がこの表を検証するので、形式はスクリプトの仕様と完全に一致させる。

```markdown
| ID | 区分 | アンカー | コメント要旨 | 対応 | 返答 |
|----|------|----------|--------------|------|------|
| 0 | typo | shoud | typo: should | 修正 | |
| 1 | 内容 | uncontrolled use may ... | 根拠を引用するか表現を弱める | 修正 | 表現を can に弱め、評価研究を引用しました (Background 第1段落)。 |
| 4 | 内容 | AI disclosure example | モデルのバージョンを残す | 修正せず | ご指摘のとおり維持します。 |
```

検証ルール (`make_tracked_md.py --responses` が守らせる):

- **区分**: `typo` (誤字・スペース・句読点) / `表記` / `内容` / `質問` など自由記述だが、
  `typo` の綴りは固定 (`--skip-kind` のデフォルトが `typo`)
- **対応**: `修正` / `一部修正` / `修正せず` / `保留`
- **返答**: `typo` 区分かつ対応が `修正` の行以外は**必須**。空だとエラーで止まる
- `$p/review/vN/report.json` に載っている**すべてのコメント**に 1 行が要る。ただし
  **著者自身 (`--author` と同名) の過去の返答コメントは既定で除外される** (前回の
  round で自分が付けた返答が、次のエクスポートに「コメント」として混ざって
  返ってくるのを除くため)。除外された自分のコメントの ID が summary に出る。
  含めたい場合だけ `make_tracked_md.py --include-own-comments` を付ける
- 表になく report.json にある ID、逆に report.json に無い ID の行があるとエラー。
  ID が重複してもエラー
- セル内にリテラルな `|` を書きたい場合は `\|` とエスケープする
- `typo` の行は、対応が `修正` のときだけ v2 の docx にコメントとして載せない
  (件数だけ summary と送付メッセージで伝える)。それ以外の行は元コメントの直後に
  返答コメントとして必ず載る
- 共著者の提案 (トラック変更) を受け入れる場合、対応表には書かず、Step 3 で本文に
  直接反映すればよい。受け入れない提案は ID 無しの行を足して理由を書く

AI への依頼文の例:

```text
@projects/<name>/review/v1/report.md を読んで、
projects/<name>/review/v1/response_table.md をこの Skill の形式で作ってください。
typo と内容を区別し、内容・質問には返答案を書いてください。まだ本文は直さないでください。
```

## 3. 本文 (draft.md) を直す

対応表の「修正」「一部修正」行に従って `projects/<name>/draft.md` を直す。`@` で
セクションを指定して小さく直す (README の作法)。英文プローズは
`skills/case_report_workflow/style_discipline.md` に従う。

- 引用は `projects/<name>/refs.bib` にあるものだけを使う。共著者コメントで新規文献の
  追加を求められた場合は、`similar_cases_search` Skill の `add` サブコマンドで
  `refs.bib` に追記し、`citation_verify` Skill で照合してから引用する。AI に
  citation を作らせない
- 共著者の提案 (トラック変更) を受け入れる行は、対応表に書かず本文にそのまま反映する

```text
@projects/<name>/review/v1/response_table.md の「修正」「一部修正」行に従って
@projects/<name>/draft.md を直してください。セクションごとに、どこを変えたか
短く報告してください。
```

## 4. 変更履歴 + コメント入りの Markdown を作り、docx にレンダリングする

```powershell
$env:PYTHONUTF8="1"
$p = "projects/<name>"

python skills/tracked_revision/scripts/make_tracked_md.py `
  --old $p/versions/draft.v1.md --new $p/draft.md `
  --report $p/review/v1/report.json --responses $p/review/v1/response_table.md `
  --author "Taro Yamada" `
  --out $p/output/v2/draft_v2_tracked.md

pandoc $p/output/v2/draft_v2_tracked.md --reference-doc demo/styles/reference.docx `
  --citeproc --bibliography $p/refs.bib --csl demo/styles/american-medical-association.csl `
  --resource-path $p `
  -o $p/output/v2/draft_v2_tracked.docx
```

`--reference-doc` / CSL のパスは `demo/render_docx.ps1` / `demo/README.md` に合わせる
(体裁: 本文 Times New Roman・行間 1.5 倍、見出し黒ゴシック太字)。`--resource-path` を
付けないと、`draft.md` と同じフォルダの画像が pandoc の実行ディレクトリ (リポジトリ
ルート) から見つからず解決に失敗する。

`--author` はレビュアーに見せる自分の名前。`make_tracked_md.py` がやること:

- 段落ごとに v1 と v2 を対応付け、語 (日本語は文字) 単位の差分を pandoc の
  `insertion` / `deletion` span にする
- 元コメントを同じアンカー位置に `comment-start` / `comment-end` として再挿入し、
  直後に `[対応] 返答` を自分名義のコメントとして付ける
- 表は行・セル単位で差分を出す。行の対応付けは既定でラベル列 (先頭の非数値列)
  を基準にする (`--row-match label` が既定。行削除と値変更を混同しない。
  旧来の行位置ベースの対応付けに戻すには `--row-match text`)
- コードブロック・生 HTML・YAML は差分表示できないので
  新版だけを出す (削除された側は summary に記録され、出力からは省かれる)

pandoc が span を Word の変更履歴 (`w:ins` / `w:del`) と `comments.xml` に変換する。
実行すると `$p/output/v2/draft_v2_tracked.md.summary.md` に件数と「載せられなかった
コメント」が出る (実際の文面はフィクスチャ実行で確認済み):

```text
# tracked summary — draft_v2_tracked.md

- 変更のあったブロック: 5 / 追加: 1 / 削除: 1
- 文書に載せたコメント: 4 件 (うち段落単位で近似アンカー: 0 件 → ID なし)
- 載せなかったコメント (区分 typo): 1 件 → ID 0
- 載せなかったコメント (位置を特定できない): 0 件
```

## 5. 送る前に検証する

**`review/` ではなく `output/vN+1/check/` に出す** (`review/` に出すと入力の
report.json を上書きしてしまう)。

```powershell
python skills/fetch_gdoc_changes/scripts/parse_docx_changes.py `
  $p/output/v2/draft_v2_tracked.docx $p/output/v2/check
```

`$p/output/v2/check/report.md` で次を確認する。

- 変更追跡の件数が 0 でない (対応表の「修正」行がすべて `修正せず`/`保留` の場合は
  0 でも正常)
- summary の「文書に載せたコメント」は**元コメント (original) の件数だけ**を数えている。
  対応表の「返答」は空欄禁止なので、載せた元コメント 1 件ごとに必ず返答コメントが
  1 件付く。よって docx 側の実コメント数 = 「元コメント (載せた数) + その返答の数」
  = summary の数字のちょうど 2 倍になる
- summary の「載せなかったコメント (位置を特定できない)」に ID が出ていたら、
  その ID の返答は Step 6 の送付メッセージに直接書く (docx には載っていない)

## 6. 新しい Google Doc としてアップロードする

**旧 Doc を上書きしない** (Step 0 の手順どおり、ハッシュ付きファイル名で新規
アップロードし、`versions_ledger.py record` で新しい Doc ID を記録する)。

送付メッセージのテンプレート (数字は summary からそのまま持ってくる):

```text
v2 をアップロードしました: https://docs.google.com/document/d/<FILE_ID>/edit
- 変更は v1 (レビュー版) に対する「提案」として表示されます (変更ブロック 5 / 追加 1 / 削除 1)
- いただいたコメントのうち typo 1 件は修正済み、残り 4 件は元コメントの直後に返答を付けています
- 修正せず/保留: ID 4 (理由: 投稿時に最終確認)
- コメントとして載せられなかった箇所: なし
```

## Round 2 以降 (v2 → v3, v3 → v4, ...)

- 基準は `$p/versions/draft.v2.md`、レビューは `$p/review/v2/`、出力は `$p/output/v3/`
- `make_tracked_md.py` は既定で著者自身の過去の返答コメントを除外するので、
  `$p/review/v2/response_table.md` には共著者のコメントだけを載せればよい
  (前回対応済みで未解決のスレッドも含む。下記参照)
- Step 1 の `check_direct_edits.py` による自動比較は round 2 以降は成立しない
  (アップロード済みの v2 Doc 自体に v1→v2 の提案が乗っているため)。かわりに、
  `$p/review/v2/report.md` の提案一覧を見て、**v2 で自分たちが出した提案のうち
  どれを共著者が Accept/Reject したか**を著者が手作業で突き合わせてから
  `$p/draft.md` を直す
- **コメント ID は round ごとに Google Docs が振り直す** (2026-09-13 実測:
  アップロードした v2 docx では ID `0, 1000, 1, 1001` だったものが、エクスポートし
  直すと `0, 1, 2, 3` になった)。round N の ID は round N-1 の ID と無関係なので、
  対応表は必ずその round の `report.json` から作り直す (前回の ID を使い回さない)
- 自分の返答コメントは著者名 (`--author`) で返ってくるので、既定の除外が効くのは
  **毎回まったく同じ `--author` 文字列を使ったとき**だけ。round ごとに表記を変えない
- v2 で対応済みでも Google Docs 上で「解決 (Resolve)」していないスレッドは、
  round 2 のエクスポートにそのまま出てくる (2026-09-13 実測)。エクスポート前に
  共著者へ「対応済みのスレッドは解決してほしい」と頼むのが望ましい (解決済み
  スレッドがエクスポートから外れるかは未確認なので、report.json で確かめる)。
  出てきたコメントには対応表に行を追加する (返答は空欄にできないので、例: 対応 = `対応済み`、返答 = 「v2 で対応済み
  (...)」)

## 制限事項

- 削除した引用文献も、tracked docx の巻末文献リストには**新旧両方**が載る
  (`--citeproc` が新旧両方の citekey を解決するため)
- 表を丸ごと挿入したブロックを共著者が全 Reject すると、空の表の骨組みが残る
- コード/生 HTML/YAML ブロックの変更は差分表示できない。新版だけが出力され
  (削除された側は出力から省かれる)、summary に一覧が出るので送付メッセージで伝える
- 表の中、またはアンカー文字列があいまい (複数箇所に一致し文脈でも一意に
  決まらない) なコメントは docx に載らない。summary の「位置を特定できない」に
  出るので、返答を送付メッセージに直接書く
- 段落を移動しただけの変更は「削除 + 挿入」として表示される (移動として検出しない)
- `check_direct_edits.py` は図表キャプション行 (pandoc plain の `: caption` 形式)
  を比較対象から外すので、キャプションだけの直接編集は検出できない
- round 2 以降の直接編集チェックは手作業 (上記「Round 2 以降」参照)
- Google Docs は返答コメントを元コメントのスレッド内の返信として表示する
  (2026-09-13 実測)。Word で開くと、元コメントと返答コメントは別々の 2 件として
  表示される

## 環境が違うときの代替

| 手段 | 必要なもの | 変更履歴 | 元コメント保持 |
|---|---|---|---|
| この Skill (pandoc + Python) | pandoc, Python 3 | ○ 語単位 | ○ 返答も付く |
| `pandiff old.md new.md -o diff.docx` | Node.js, pandoc | ○ 語単位 | × |
| Word「比較」(校閲 → 比較) | Word | ○ | ○ (設定で含める) |
| Google Docs 上で直接「提案モード」で編集 | ブラウザのみ | ○ | ○ |

どの手段でも、**対応表 (Step 2) と送付メッセージ (Step 6) は同じ**。
