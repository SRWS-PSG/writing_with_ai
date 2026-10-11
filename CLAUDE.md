# Claude / AI Assistant Notes

このリポジトリでは、実際に書く原稿や個別案件の作業ファイルは `projects/` の下位フォルダに置く。

## `projects/` の扱い

- `projects/` 配下は、参加者・研究者ごとの実原稿、未公開データ、共同研究メモを置く作業領域。
- `projects/*` は `.gitignore` によりデフォルトで Git 管理外。
- サンプルとして共有する教材は `demo/` に置き、実案件の原稿やデータは `demo/` には置かない。
- `projects/` 配下のファイルを Git に追加する必要がある場合は、内容に個人情報、未公開データ、共同研究上の機密が含まれないことを確認してから、明示的に `.gitignore` の例外を追加する。

AI アシスタントは、ユーザーから明示された場合を除き、`projects/` 配下の実原稿やデータを Git 管理対象にしない。

## ケースレポートを書くとき

ケースレポート (症例報告) を最初から最後まで AI と一緒に書く場合は、`case_report_workflow` Skill (`skills/case_report_workflow/SKILL.md`) を起点にする。個別の作業 (CARE チェックだけ / 類似症例検索だけ など) は、対応する単体 Skill を直接呼ぶ。

## Letter to the Editor を書くとき

既発表論文への応答・批評として Letter to the Editor を AI と一緒に書く場合は、`letter_to_editor` Skill (`skills/letter_to_editor/SKILL.md`) を起点にする。日本語メモを入力に、`projects/<name>/` に英文レターのドラフトを生成する。レターは「(P1) 称賛 → (P2)(P3) 結論をゆがめるバイアス / 結果解釈の spin を指摘」の固定 3 段落構成。

- 対象論文ファイルは**著者が手で `projects/<name>/` に置く**。Skill は Read するだけで Web からは取得しない。
- 着手前に、対象論文の同定情報と批評対象の引用箇所を提示してユーザーと確認する human-in-the-loop ゲートを通す。
- 語数・文献数制限はメモ記載があればそれを使い、なければユーザーに確認する (Skill 側でガイドラインは取得しない)。
- 自験データ・症例を含むレターはこの Skill の対象外。その場合は `case_report_workflow` を使う。

個別の作業 (生成済みレターの査読だけ など) は、対応する単体 Skill を直接呼ぶ。レター固有の査読は `letter_review_simulator` Skill (`skills/letter_review_simulator/SKILL.md`)。

## 英文スタイル層の使い分け

英文プローズのルールはリポジトリ内に 2 層ある。重複するルール (em-dash 禁止など) は `style_discipline.md` を正とする。

- **`skills/case_report_workflow/style_discipline.md`** — 英文ドラフトの正本ルール (em-dash 禁止、1 文 ≤ 25 語、能動態、禁止語、引用形式)。`case_report_workflow` / `letter_to_editor` がドラフト生成・改稿時に読む。ルールを変えるときはこのファイルだけを更新する。
- **`humanizer_academic` Skill** — 既存テキストから AI 文体の痕跡 (AI 語彙、誇張、-ing 付加、synonym cycling など) を除去するときに単体で呼ぶ。オーケストレータのパイプラインには組み込まれていない。「AI っぽさを消して」「文体を自然に」系の依頼はこちら。

## ロジック層 (段落・論理構造の評価と改善)

英文スタイル層 (文レベル) とは別に、**文章を書いたあとに段落・論理構造を評価して直す層**がある。文体の良し悪しではなく「主張が 1 つに絞れているか、各段落の topic sentence と論理アーク、段落間の進行 (反復していないか)、段落順序」を見る。

- **`argument_logic_review` Skill** — 任意のプローズ (レター / 原稿 / abstract / Discussion / グラント) を対象に、ロジック欠陥 taxonomy (L1–L10) で診断し、構造だけを直した新規ファイル `<元ファイル>.logic.md` を出力する。元ファイルは read-only・上書きしない。「ロジックを評価して」「段落構成をチェック」「パラグラフライティングを見て」系はこちら。
- 棲み分け: 文体 (em-dash・語数・禁止語) は触らない → `proofread-manuscript`。AI 文体痕跡 → `humanizer_academic`。科学的妥当性・公正性・spin → `peer_review_simulator` / `letter_review_simulator`。このスキルは**並べ替え・統合・分割と既存文の最小修正のみ**で、内容・引用を新規創作しない。
- 順序の目安: ドラフト → **`argument_logic_review` (構造)** → `proofread-manuscript` (文体) → 内容/公正性レビュー。

## 共著者コメントに基づいて修正するとき

共著者が Google Doc にコメント・提案 (suggestion) を付けた版を、対応表付きで
Markdown に反映し、v2 以降の Google Doc として返すときは `tracked_revision` Skill
(`skills/tracked_revision/SKILL.md`) を起点にする。取得だけなら `fetch_gdoc_changes`
Skill、単純な新規アップロードだけなら `render_and_upload` Skill を直接呼ぶ。

省いてはいけない点:

- **アップロードのたびに `versions/` へスナップショットを取り、台帳
  (`versions_ledger.py`) に記録する**。次回の差分の基準がこれしかない
- **同じ Google Doc を上書きしない**。修正版は必ず新しい Doc としてアップロードする
  (同名ファイルで上書きすると、共著者が付けたコメントスレッドが消える)
- **本文を直す前に、コメント 1 件 1 行の対応表 (`response_table.md`) を作る**。
  対応表が無いまま直すと、どのコメントにどう応えたかが誰にも分からなくなる
- 英文の改稿は `skills/case_report_workflow/style_discipline.md` に従う

## 字数・分量の予算管理 (総枠制の媒体で書くとき)

依頼原稿・総説など「図表換算・文献欄込みで総字数◯字」型の媒体では、次を守る (手順の詳細は `skills/submission_guidelines_check/SKILL.md` の 2a 節)。

- **文献欄は初稿から投稿先の書式で出力して実測する**。見積もりは文献の追加・書式変更で大きく揺れ、本文の予算を黙って食う (実案件で 450→825 字に振れた)。作業用の CSL が投稿先と違うなら、計数用に投稿先書式で仮レンダリングしてでも測る。
- 本文・文献欄・図表換算・図説・付記を**別々に計数**し、算入が未確定の要素 (タイトル・所属・図説を総枠に含むか) は「未確定」のまま、厳しい側の合計も並記する。
- 図表を 1 点足す提案には「換算で何字増え、代わりに何を削るか」を同時に示す。
- **字数超過の解消で内容 (事例・図・段落) を落とすときは、何を落とすかを排他選択として著者に提示してから実行する**。AI が選ぶと後から逆転されて往復が増える。

## 引用チェックの二層 (書誌の実在と、主張との対応)

- `citation_verify` (citeguard) が見るのは**書誌の実在・撤回**だけ。引用が本文の主張を支えているかは見ない。
- 脱稿前に 1 回、本文の引用ごとに「引用文＋支えるべき主張」を並べて原文で対応を確認する工程を入れる (`citation_verify` SKILL.md の "Scope limit" 節)。書誌チェックの通過を「引用は大丈夫」と読み替えない。

## 外部 AI の推敲を取り込むとき

- 依頼時に変更してよい範囲を指定する: 元の字数を超えない、数値・主体・時点・因果関係・断定の強さ・引用と主張の対応を保つ、新しい事実や文献を加えない。意味を変える提案は本文に混ぜず理由つきで別記させる。
- 取り込み前に**意味の変化を差分で読む** (「目指す→達成する」「関連→原因」型の強まりが典型)。禁止語チェックだけでは意味の変化は拾えない。

## PubMed 文献検索 (検索式は projects 配下に保存)

レターやケースレポートの文献検索は、コミット済みの汎用スクリプト `skills/similar_cases_search/scripts/pubmed_search.py` を使う。Web 検索ツールを持たないモデル (例: 検索できない Gemini) に作業を渡しても、このスクリプトを実行すれば PubMed から根拠付き BibTeX を得られる。

- **検索式 (query) はリポジトリに置かず、gitignore された `projects/<name>/searches/<topic>.query.txt` に保存**してから使う。リポジトリにはエンジンだけを置き、案件固有の検索内容で汚さない。
- `search` サブコマンドはレビュー用ステージング `searches/<topic>.candidates.md` を出力する (これは `.bib` ではない)。`add` サブコマンドだけが、著者承認済み PMID をレンダリング正本の `refs.bib` に追記する。野良 `.bib` を作らないので、pandoc レンダリング時の取り違えを防ぐ。
- NCBI コンタクトメールはハードコードしない。`--email` か環境変数 `$NCBI_EMAIL` で渡す。
- 使い方の詳細は `skills/similar_cases_search/scripts/README.md`。
