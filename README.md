# Writing with AI — 参加者用リポジトリ

SRWS-PSG ハンズオンカフェ「Writing with AI」(2026-05-13 17:30-18:30) で使う最小ファイル一式。

## このリポジトリの位置づけ

「文章作成も、コード作成と同じく **プロジェクトをIDEで開き、ファイルをAIに見せながら、小さく直して、レンダリングして確認する** 作業にできる」を体験するためのデモ素材。

前提:

- 前提資料「もうコードは書かない！臨床疫学のためのVibe Coding完全ガイド」を実施済み
- Antigravity をインストール済みで、AIチャットが動く

## 当日やること

1. このリポジトリを `git clone` または ZIP ダウンロードでローカルに置く

   ```powershell
   git clone https://github.com/youkiti/writing_with_AI.git
   ```

2. IDE (Antigravity / VS Code 等) でフォルダごと開く
3. `env_check.md` を開き、AIチャットに次のように頼む

   ```text
   @env_check.md を読んで、私のPC環境を順に確認してください。
   ```

   pandoc が未インストールなら、AIに案内された手順に沿って入れる（**pandoc 関連のコマンドだけ許可**。それ以外は拒否）。

## 当日の流れ

1. 練習では `demo/draft.md` をIDEで開く。実際の原稿を書くときは `projects/<project_name>/` の下に置く
2. 下の「コピペ用プロンプト集」のプロンプトを見ながら、AIに部分修正を依頼する
3. `demo/protocol.md` + `demo/analysis.R` を `@` で読ませて、`draft.md` の Methods のたたき台を AI に書かせる
4. 生成した Methods を `protocol.md` / `analysis.R` と突き合わせて整合を確認する
5. `demo/assets/figure1.png` を本文に埋め込む（draw.io でひな型を作るのもあり）
6. 引用は Zotero / Paperpile から BibTeX を取り出して `refs.bib` に貼る（AI に citation を作らせない）
7. pandoc で `demo/output/draft.docx` を作る（下の「pandoc コマンド」をコピペ）
8. 生成した `draft.docx` を Google Docs にアップロード→共有

---

## コピペ用プロンプト集

> 参加者が当日コピペする内容はすべてここに集約しています。スライド (`20260513writing with ai.pdf`) のクリーム色ふきだしと同じ内容です。AIチャットにそのまま貼ってください。

### 1. 環境確認（スライド p.8）

```text
@env_check.md を読んで、私のPC環境を順に確認してください。
```

### 2. `@` でファイルを指定して部分修正（スライド p.21）

基本形:

```text
@draft.md を読んでください。
Background セクションだけを対象に、以下の方針で修正してください。
・内容は増やさない
・300 words 以内
・臨床疫学の研究計画書として自然な文体
・修正案だけでなく、どこを変えたかも短く説明
```

その他の言い方:

```text
@draft.md の Methods だけ、PECO が明確になるように直して
```

```text
@draft.md の Discussion だけ、言い過ぎを弱めて
```

```text
@draft.md 全体を読んで、論理の飛びだけ指摘して。本文は書き換えないで
```

### 3. protocol + code から Methods を書く（スライド p.23）

```text
@protocol.md と @analysis.R を読んで、
@draft.md の Methods セクションのたたき台を書いてください。

構成:
1. Study design and setting
2. Participants (組み入れ・除外)
3. Exposure and outcome definitions
4. Statistical analysis (モデル、調整変数、欠測)

ルール:
・事実は protocol.md と analysis.R に書かれている内容に限定
・書かれていない数値は [TODO: 確認] と明示し、勝手に補完しない
・各段落2〜4文
```

### 4. 生成された Methods を突き合わせる（スライド p.24）

```text
@protocol.md と @analysis.R を見て、
@draft.md の Methods に protocol/code と食い違う記述や、
根拠が見当たらない記述がないか指摘してください。
```

### 5. PRISMA フローチャートを draw.io で作らせる（スライド p.27）

```text
PRISMAフローチャートのひな型を draw.ioフォーマットで作って
```

### 6. draft.md に直接コメントで指示して「なおして」（スライド p.29）

`draft.md` の図を入れたい位置に、こんなコメントを書く:

```text
# ここに demo\assets\study_flow.drawio からpngにして追加して
```

そのうえで Chat に短く:

```text
なおして
```

### 7. Skill で文体をそろえる（スライド p.31）

```text
SKILL の方針で
@draft.md の Discussion を書き直して
```

> このリポジトリの [skills/humanizer_academic/](skills/humanizer_academic/) が松井健太郎先生由来の文体 Skill。Antigravity 側で Skill が読み込まれていれば、上のように短く頼むだけで効く。

### 8. pandoc で Markdown → Word（スライド p.41-42）

AIに作らせる場合（スライドの例）:

```text
@projects¥chatgpt_diagnostic_study¥sample_draft¥draft_manuscript.md を @reference.bib @american-medical-association.csl を使ってdocxに pandocでレンダリング
```

> 要点は **テキストファイル + リファレンスファイル + citation スタイル + 出力形式 + pandoc** を渡すこと。コマンドを覚えてなくても、`ファイル名 + pandocでdocxにして` で OK。

そのまま使う場合（ルートから実行）:

```powershell
cd demo
pandoc draft.md --citeproc --bibliography refs.bib --csl styles/american-medical-association.csl -o output/draft.docx
```

スクリプト経由（ルートから実行）:

```powershell
powershell -ExecutionPolicy Bypass -File demo/render_docx.ps1
```

### 9. Markdown を Google Document にアップロード（スライド p.43）

```text
@draft.mdをレンダリングして、Google documentにアップロード
```

> Skill: [skills/render_and_upload/](skills/render_and_upload/)

### 10. Google Docs の編集を Skill で取り込む（スライド p.43）

```text
`Google docのurl` をskillを使ってチェックしてもらえる？
```

> Skill: [skills/fetch_gdoc_changes/](skills/fetch_gdoc_changes/)

### 11. 共著者コメントに対応した v2 を Google Docs に返す

```text
review/v1/report.md を読んで対応表 (response_table.md) を作って。
それに沿って draft.md を直して。
できたら tracked_revision Skill で、変更履歴とコメント返答入りの v2 の docx を作って。
```

> Skill: [skills/tracked_revision/](skills/tracked_revision/)

---

## フォルダ構成

```text
.
├── README.md                    # このファイル
├── CLAUDE.md                    # AIアシスタント向けの運用メモ
├── env_check.md                 # 環境チェック (AIに読ませて使う)
├── demo/                        # ハンズオンの最小プロジェクト
│   ├── README.md
│   ├── draft.md                 # 本文 (Markdown)
│   ├── protocol.md              # 研究計画書サンプル (Methods生成用)
│   ├── analysis.R               # 解析コードサンプル (Methods生成用)
│   ├── refs.bib                 # 引用に使ってよい文献リスト
│   ├── render_docx.ps1          # pandoc 実行スクリプト
│   ├── assets/                  # 図 (PNG, Mermaid, HTML, draw.io XML)
│   │   ├── figure1.png
│   │   ├── study_flow.mmd
│   │   ├── study_flow.html
│   │   ├── study_flow.drawio
│   │   └── study_flow.png
│   ├── styles/
│   │   └── american-medical-association.csl  # 引用スタイル
│   └── output/
│       └── draft.docx           # pandocで生成済みの完成見本
├── projects/                    # 実際の執筆プロジェクト置き場
│   └── .gitkeep                 # projects/ 自体を残すための空ファイル
└── skills/                          # AI アシスタント用 Skill 群 (使い分けは CLAUDE.md 参照)
    ├── case_report_workflow/        # 症例報告のエンドツーエンド・オーケストレータ (+ style_discipline.md = 英文スタイル正本)
    ├── letter_to_editor/            # Letter to the Editor オーケストレータ (日本語メモ → 英文レター)
    ├── similar_cases_search/        # PubMed 検索 → refs.bib 候補 (scripts/pubmed_search.py)
    ├── citation_verify/             # refs.bib を citeguard で Crossref/PubMed 照合
    ├── bottom_line_message/         # 松原メソッド「2つのわかったこと」抽出
    ├── care_check/                  # CARE 2013 チェックリスト監査
    ├── deidentify_check/            # 症例報告の個人情報チェック
    ├── case_timeline/               # 経過の Mermaid timeline 図化
    ├── peer_review_simulator/       # 症例報告の査読シミュレーション (非 CARE)
    ├── letter_review_simulator/     # レターの査読シミュレーション
    ├── submission_guidelines_check/ # 投稿規定の抽出・照合
    ├── humanizer_academic/          # AI 文体の除去 (スライド §7)
    ├── render_and_upload/           # Markdown → docx → Google Docs (スライド §9)
    ├── fetch_gdoc_changes/          # Google Docs の suggestion / コメント取り込み (スライド §10)
    └── tracked_revision/            # コメント対応表 → 修正 → 変更履歴+返答入り v2 (§11)
```

各 Skill の詳細は `skills/<name>/SKILL.md` を参照。多くの Skill は `tests/` に回帰用フィクスチャを持つ。症例報告をゼロから書くときは `case_report_workflow`、既発表論文への批評レターは `letter_to_editor` が起点 (CLAUDE.md 参照)。

## 実際の原稿を書く場所

実際の論文原稿、症例報告、共同研究メモ、未公開データは `projects/<project_name>/` の下に置く。

`projects/*` は `.gitignore` によりデフォルトで Git 管理外。個人情報や未公開データを誤って GitHub に push しないため、教材として共有するファイルは `demo/`、実案件の作業ファイルは `projects/` に分ける。

どうしても `projects/` 配下のファイルを共有リポジトリに入れる場合は、内容を確認したうえで `.gitignore` に明示的な例外を追加する。

## ボトムライン

- **Markdown が真実のソース**、`docx` はビルド成果物。Word 保存ではなく `pandoc` で都度生成する
- **AIには `refs.bib` の中の文献だけを使わせる**。hallu-citation を防ぐ
- **`@` でファイル指定して部分修正**。本文全体を一度に書き換えさせない
- **Methods は `protocol.md` + `analysis.R` から「翻訳」できる**。AI の活躍場面
- **実際の原稿は `projects/` 配下に置く**。配下はデフォルトで Git 管理外
- **レビューを受けたら「変更履歴 + 元コメントへの返答 + 対応表」で返す**。修正版だけ送り返すと、どこをどう直したか共著者に伝わらない

## 関連

- 前提WS: もうコードは書かない！臨床疫学のための Vibe Coding 完全ガイド
- 公式ドキュメント: [pandoc](https://pandoc.org/), [Mermaid](https://mermaid.js.org/), [draw.io](https://www.drawio.com/)
- 引用スタイル: [Citation Style Language (CSL)](https://citationstyles.org/)
