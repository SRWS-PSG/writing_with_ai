# DetectorScope で「AI らしく見える箇所」を見つける

[DetectorScope](https://github.com/google-deepmind/detectorscope) (Google DeepMind・ペンシルベニア大学、EMNLP 2026) は、英文が AI 生成かを判定する検出器です。判定の根拠を「名前の付いた特徴」(例: `repeated phrases or sequences in text`) の和として返し、それぞれの特徴が本文のどの語で効いているかも示します。

このリポジトリでは、DetectorScope を**英文校正の下調べ**として使います。「どの言い回しが AI らしさの根拠として拾われているか」を一覧にし、直す作業は `humanizer_academic` Skill や自分の手で行います。Skill やスクリプトとしては組み込んでいないので、使う人が自分の PC に入れて動かします。

## 使う前に知っておくこと

- **AI 生成かどうかの判定には使いません**。作者自身が「個人に関する判断 (学術上の不正、採用、出版可否) の根拠にしてはならない」と明記しています。人が書いた文章でも間違えます。
- **確率 (`p_ai`) と判定ラベル (`label`) は見ません**。下の手順のスクリプトも、特徴と該当箇所だけを表示します。数字を下げること自体を目標にすると、意味を変えてでも検出を逃れる書き換えに寄るためです。
- **医学論文での精度は検証されていません**。学習データはニュース・エッセイ・レビューなど (`detector-scope`) と、機械学習分野の査読コメント (`detector-scope-peer-review-*`) です。拾われた特徴は「直す候補」であり、直す義務ではありません。医学論文として正しい定型表現 (例: `was measured`、`Notably,`) は、拾われても残します (`humanizer_academic` の「Preserve Legitimate Academic Phrases」節と同じ考え方です)。
- **英文専用**です。和文には使えません。
- 1 回に読めるのは 1024 トークン (英文でおよそ 700 語) までで、それを超えた部分は黙って切り捨てられます。段落ごとに流します。
- **未公開原稿を外部に送りません**。モデルを一度ダウンロードした後は、手元の PC の中だけで動きます (Hugging Face のデモページに原稿を貼るのは避けてください)。

## 準備 (初回だけ)

必要なもの: Python 3.10 以上、空き容量およそ 15 GB (PyTorch とモデル)、メモリ 16 GB 程度。GPU は不要です (NVIDIA GPU があれば自動で使い、なければ CPU で動きます。Mac の GPU は使いません)。CPU だと 1 段落に数十秒から数分かかります。

リポジトリの外に専用の環境を作ります (`projects/` や Skill のフォルダには入れません)。

```bash
python -m venv ~/detectorscope-env
```

```bash
source ~/detectorscope-env/bin/activate
```

```bash
pip install detectorscope
```

Windows (PowerShell) では 2 行目を `~\detectorscope-env\Scripts\Activate.ps1` にします。

初回の実行時にモデル (Gemma-2-2b を含む数 GB) が Hugging Face から自動でダウンロードされます。

## 使い方

### 1. 調べたい段落をテキストファイルにする

`projects/<name>/scope/input.txt` に、調べたい英文を置きます。**段落と段落の間は空行**にします。引用番号 (`[1]`)、表、見出しは除いておくと結果が読みやすくなります。

### 2. スクリプトを保存する

次の内容を `~/detectorscope-env/scope_report.py` として保存します (リポジトリには置きません)。

```python
"""DetectorScope の特徴と該当箇所を、段落ごとに Markdown で書き出す。

確率 (p_ai) と判定ラベル (label) は意図して出力しない。
使い方: python scope_report.py input.txt report.md [モデル名]
"""
import sys

from detectorscope import AuditableDetector

TOP_N = 8  # 段落ごとに表示する特徴の数

src, dst = sys.argv[1], sys.argv[2]
repo = sys.argv[3] if len(sys.argv) > 3 else "liamdugan/detector-scope"

detector = AuditableDetector.from_pretrained(repo, torch_dtype="bfloat16")

text = open(src, encoding="utf-8").read()
paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

out = [f"# DetectorScope report ({repo})", ""]
for n, para in enumerate(paragraphs, 1):
  det = detector(para, return_highlights=True)
  out += [f"## 段落 {n}", "", f"> {para[:200]}{'...' if len(para) > 200 else ''}", ""]
  out += ["| 向き | 特徴 | 本文で強く効いている語 |", "|---|---|---|"]
  for f in det.features[:TOP_N]:
    side = "AI 寄り" if f.importance > 0 else "人間寄り"
    spots = sorted(f.highlights or [], key=lambda h: -h[1])[:5]
    words = ", ".join(
        "`" + "".join(det.tokens[max(t - 2, 0):t + 3]).strip().replace("|", "/") + "`"
        for t, _ in spots
    )
    out.append(f"| {side} | {f.description or '(説明なし)'} | {words} |")
  out.append("")

open(dst, "w", encoding="utf-8").write("\n".join(out))
print(f"wrote {dst}")
```

### 3. 実行する

リポジトリのフォルダで、環境を有効にしてから実行します。

```bash
python ~/detectorscope-env/scope_report.py projects/<name>/scope/input.txt projects/<name>/scope/report_before.md
```

3 つめの引数でモデルを変えられます。査読コメント (レビュアーへの返答や Letter) に近い文章なら、`liamdugan/detector-scope-peer-review-gpt4o` も試せます。

### 4. 結果を読んで直す

`report_before.md` には段落ごとに、効いている特徴が強い順に並びます。

- **AI 寄り** の特徴: AI らしさの根拠として拾われた性質です。右の列の語が、本文の該当箇所 (前後 2 トークン込み) です。
- **人間寄り** の特徴: 人が書いた文章らしさとして拾われた性質です。直すときに消さないよう参考にします。

直すときは、AI チャットに `humanizer_academic` と一緒に渡すと、該当箇所に絞って書き換え案を出させられます。

```text
@skills/humanizer_academic/SKILL.md に従って、@projects/<name>/draft.md の英文を見直してください。
@projects/<name>/scope/report_before.md の「AI 寄り」の特徴と該当語を、直す候補の手がかりにしてください。
ただし医学論文として正しい定型表現は残し、数値・主張の強さ・引用との対応は変えないでください。
```

直したら同じ手順で `report_after.md` を作り、前後を並べて「どの特徴が消えたか、意味は変わっていないか」を見ます。比べるのは特徴と該当語であり、確率ではありません。

## 関連する Skill

- `humanizer_academic`: AI 文体の痕跡を消す書き換え。DetectorScope の結果はこの Skill の手がかりとして使う
- `sentence_rhythm_review`: 文の長さの分布とリズムの計測
- `skills/case_report_workflow/style_discipline.md`: 英文スタイルの正本ルール (em-dash 禁止など)

## 出典

Dugan L, McDougall CS, Denton M, Pham P, Kaeser-Chen C, Callison-Burch C. Building Auditable AI Text Detectors with Sparse Autoencoders. Proceedings of EMNLP 2026. https://aclanthology.org/2026.emnlp-main.762/

ソフトウェアは Apache License 2.0、モデルなどその他の素材は CC BY 4.0 です。
