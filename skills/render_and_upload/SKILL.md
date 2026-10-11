---
name: render_and_upload
description: Render a Markdown manuscript to Word (docx) with pandoc and upload it to Google Drive as a Google Doc.
---

# Render and Upload Skill

指定された Markdown ファイルを Word (docx) にレンダリングし、Google ドライブに Google ドキュメント形式でアップロードする手順です。

## 前提条件

- `pandoc` がインストールされていること
- `rclone` がインストールされ、`gdrive:` リモートが設定されていること
- コンソールは cp932 なので、Python (`versions_ledger.py`) を実行する前に
  `$env:PYTHONUTF8="1"` を設定する

## 入力

- **必須**: レンダリング対象の Markdown パス (例: `projects/<name>/draft.md`)。
  指定がなければユーザーに確認する。`demo/draft.md` はワークショップ練習用。
- **任意**: `refs.bib` と CSL ファイル。入力と同じフォルダ (または
  `demo/styles/`) にあれば `--citeproc` 付きでレンダリングする。
- **任意**: アップロード先フォルダ (デフォルト:
  `gdrive:writing_with_AI/<プロジェクト名>/`)。

## 実行手順

1. **レンダリング**:
   引用がある原稿は bibliography + CSL + 体裁雛形を付けてレンダリングする。
   `--reference-doc` は `demo/styles/reference.docx` (本文 Times New Roman・
   行間 1.5 倍、見出し黒ゴシック太字) を `demo/render_docx.ps1` と同じ要領で使う。
   以下はリポジトリのルートから実行する前提で、プロジェクトフォルダを変数
   `$p` に入れておく (プロジェクト配下のファイルは常に `$p/...`、Skill の
   スクリプトは `skills/...`、共有の体裁雛形/CSL は `demo/styles/...`)。

   ```powershell
   $p = "projects/<name>"
   pandoc $p/<input>.md --reference-doc demo/styles/reference.docx `
     --citeproc --bibliography $p/refs.bib --csl demo/styles/american-medical-association.csl `
     -o $p/output/<input>.docx
   ```

   - 出力 docx は入力と同じプロジェクトフォルダ配下 (`$p/output/`) に置く。
     **実案件の成果物を `demo/output/` に置かない** (`demo/` は教材、
     `projects/` は実案件 — リポジトリの CLAUDE.md 参照)。
   - ワークショップ練習 (`demo/draft.md`) では `demo/render_docx.ps1` を
     そのまま実行してよい (出力は `demo/output/draft.docx`)。**`demo/` は
     教材であり、下の手順 2 の台帳には記録しない** — 台帳運用は
     `projects/<name>/` 配下の実案件だけに適用する。

2. **台帳に記録しつつアップロードする** (ハッシュ付きファイル名 →
   `check` → `rclone copy` → `rclone lsjson` → `record` の順)。手順の詳細と
   「なぜハッシュ付きファイル名が要るか」は `tracked_revision` Skill
   (`skills/tracked_revision/SKILL.md` の「0. アップロード手順」) を参照。
   最初のアップロードなので `--version v1` で記録する。台帳ファイルは常に
   `$p/versions/versions.md`。

   ```powershell
   $env:PYTHONUTF8="1"
   $p = "projects/<name>"
   python skills/tracked_revision/scripts/versions_ledger.py name `
     --docx $p/output/<docname>.docx --stem <docname>
   Copy-Item $p/output/<docname>.docx $p/output/<docname>_<hash>.docx
   python skills/tracked_revision/scripts/versions_ledger.py check `
     --ledger $p/versions/versions.md --docx $p/output/<docname>_<hash>.docx
   rclone copy $p/output/<docname>_<hash>.docx gdrive:writing_with_AI/<subfolder>/ `
     --drive-import-formats docx
   rclone lsjson gdrive:writing_with_AI/<subfolder>/<docname>_<hash>.docx
   python skills/tracked_revision/scripts/versions_ledger.py record `
     --ledger $p/versions/versions.md --version v1 `
     --md $p/<input>.md --docx $p/output/<docname>_<hash>.docx --doc-id <FILE_ID>
   ```

   `check` が exit 3 を返したら (=同じ内容を過去にアップロード済み) 止める。
   `record` が exit 3 を返したら (=doc_id が重複=既存 Doc を上書きした徴候)、
   Drive 上のファイルを確認する。`--md` には `*_tracked.md` ではなく素の
   Markdown を渡す。

## 注意事項

- Google ドキュメント形式に変換するため、`--drive-import-formats docx` フラグは必須です。
- 変換後のファイルは `rclone` 上でサイズが `-1` と表示されますが、これは正常な動作です。
- `projects/` 配下の実原稿 (未投稿原稿・個人情報を含み得る) をアップロードする場合は、アップロード先 Drive フォルダの共有範囲を著者が確認してから実行してください。
- 共著者のレビュー後に修正版 (v2 以降) を返すときは、この手順の続きとして
  `tracked_revision` Skill を使う。同じファイル名で再アップロードすると
  既存 Doc が上書きされ、共著者が付けたコメントが消える (2026-09-13 実測)。
