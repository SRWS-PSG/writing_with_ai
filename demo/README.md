# demo

当日ハンズオンでそのまま使う最小の文章作成プロジェクト。

## 使い方

1. この `demo/` フォルダをIDEで開く
2. `draft.md` を開く
3. `../prompts/writing_prompts.md` のプロンプトを使ってAIに部分修正を依頼する
4. pandocでWordファイルを作る

```powershell
pandoc draft.md --citeproc --bibliography refs.bib --csl styles/american-medical-association.csl -o output/draft.docx
```

PowerShellスクリプトで実行する場合:

```powershell
.\render_docx.ps1
```

## ファイル

- `draft.md`: Markdown原稿
- `refs.bib`: 引用に使ってよい文献リスト
- `styles/american-medical-association.csl`: pandoc用の引用スタイル
- `assets/figure1.png`: PNG埋め込みデモ
- `assets/study_flow.mmd`: Mermaid図のデモ
- `assets/study_flow.html`: HTML図のデモ
- `assets/study_flow.drawio`: draw.ioで手直しするデモ
- `output/`: docxなどの出力先

