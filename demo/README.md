# demo

当日ハンズオンでそのまま使う最小の文章作成プロジェクト。

## 使い方

1. この `demo/` フォルダをIDEで開く
2. `draft.md` を開く
3. ルートの `README.md`「コピペ用プロンプト集」のプロンプトを使ってAIに部分修正を依頼する
4. pandocでWordファイルを作る

```powershell
pandoc draft.md --reference-doc styles/reference.docx --citeproc --bibliography refs.bib --csl styles/american-medical-association.csl -o output/draft.docx
```

`--reference-doc styles/reference.docx` が体裁の雛形。本文=Times New Roman・行間1.5倍、見出し（`#`〜）=黒・Arial（ゴシック）・太字。体裁を変えたいときは Word で `styles/reference.docx` を開き「標準」「見出し2」等のスタイルを編集して保存する（Markdown 側は触らない）。

PowerShellスクリプトで実行する場合:

```powershell
.\render_docx.ps1
```

## ファイル

- `draft.md`: Markdown原稿
- `refs.bib`: 引用に使ってよい文献リスト
- `styles/american-medical-association.csl`: pandoc用の引用スタイル
- `styles/reference.docx`: pandoc用の体裁雛形（本文Times New Roman・行間1.5倍、見出し黒Arial太字）
- `assets/figure1.png`: PNG埋め込みデモ
- `assets/study_flow.mmd`: Mermaid図のデモ
- `assets/study_flow.html`: HTML図のデモ
- `assets/study_flow.drawio`: draw.ioで手直しするデモ
- `output/`: docxなどの出力先

