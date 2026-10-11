# Claude / AI Assistant Notes (私用の執筆リポジトリ)

このリポジトリは、所有者本人の実際の論文原稿を置く **private の作業リポジトリ**である。執筆の道具 (Skill、demo、テンプレート) はここには置かず、公開リポジトリ `writing_with_ai` を **git submodule** として `writing_with_ai/` に取り込んで読む。

説明は日本語で行うこと。<!-- 返信の言語を変えたいときは、この行を書き換える (例: 説明は英語で行うこと) -->

## 2つの層

| 層 | 場所 | 中身 | 書き込み |
|---|---|---|---|
| 親リポジトリ (private) | この直下 | `projects/<名前>/` の原稿、`refs.bib`、出力物 | する |
| 道具 (公開) | `writing_with_ai/` | `skills/`、`demo/`、`templates/` | **しない** |

ルール: **道具はサブモジュールから読み、成果物は親リポジトリに書く。**

## パスの読み替え (重要)

`writing_with_ai/` の Skill に書かれているコマンドは、道具箱のルートからの相対パス (`skills/...`、`demo/styles/...`) で書かれている。このリポジトリで実行するときは、**道具箱のパスの先頭に `writing_with_ai/` を付ける**。原稿側のパス (`projects/<名前>/...`) は付けない。

例1: `skills/render_and_upload/SKILL.md` のレンダリングコマンド

```powershell
# Skill に書かれている形 (道具箱のルートで実行する前提)
pandoc $p/<input>.md --reference-doc demo/styles/reference.docx `
  --citeproc --bibliography $p/refs.bib --csl demo/styles/american-medical-association.csl `
  --resource-path $p `
  -o $p/output/<input>.docx

# このリポジトリで実行する形 ($p = "projects/<名前>" はそのまま)
pandoc $p/<input>.md --reference-doc writing_with_ai/demo/styles/reference.docx `
  --citeproc --bibliography $p/refs.bib --csl writing_with_ai/demo/styles/american-medical-association.csl `
  --resource-path $p `
  -o $p/output/<input>.docx
```

例2: `skills/zotero_csl/SKILL.md` の CSL 検索コマンド

```bash
# Skill に書かれている形
python skills/zotero_csl/scripts/fetch_csl.py search --query "<journal name>"

# このリポジトリで実行する形
python writing_with_ai/skills/zotero_csl/scripts/fetch_csl.py search --query "<journal name>"
```

## どこから始めるか

- `writing_with_ai/CLAUDE.md`: どの作業にどの Skill を使うかの一覧
- `writing_with_ai/README.md`: そのまま貼れるプロンプト集

## 守ること

- **Markdown が真実のソース**。docx は `pandoc` で都度生成するビルド成果物で、docx を直接編集しない。
- **引用は `projects/<名前>/refs.bib` にあるものだけ使う**。AI は文献を創作しない。足りない文献は、本人が Zotero / Paperpile などから BibTeX を取り出して `refs.bib` に入れる。
- **部分修正は `@ファイル` で範囲を指定する**。本文全体を一度に書き換えさせない。
- **`writing_with_ai/` の中でコミットも push もしない**。ファイルを編集もしない。
- **このリポジトリの公開範囲を変えない** (public にしない)。削除や force push もしない。
- 秘密情報、`.env`、患者が特定できる情報はコミットしない。

## 道具の更新と持ち出し

```text
git submodule update --remote writing_with_ai
git add writing_with_ai
git commit -m "Update writing_with_ai"
```

別の PC に持っていくときは、submodule ごと取得する。

```text
git clone --recurse-submodules <自分のリポジトリのURL>
```
