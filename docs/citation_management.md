# VS Codeで論文執筆: BibTeXとPandocを使った引用管理ガイド

VS CodeとMarkdownを使って論文を執筆する際に、BibTeXファイル（`.bib`）で参考文献を管理し、Pandocを使って引用を含む最終的なドキュメント（PDFやWordなど）を生成する方法について説明します。特に初心者の方がつまずきやすいポイント（引用のオートコンプリートが機能しない問題）に焦点を当てて解説します。

## 目次

1. [必要なツール](#必要なツール)
2. [BibTeXファイル (`.bib`) の準備](#bibteXファイル-bib-の準備)
3. [Markdownファイルでの設定と引用方法](#markdownファイルでの設定と引用方法)
4. [VS Code拡張機能「Pandoc Citer」による自動補完](#vs-code拡張機能pandoc-citerによる自動補完)
5. [Pandocによるドキュメント生成](#pandocによるドキュメント生成)
6. [まとめ](#まとめ)

## 必要なツール

まず、以下のツールが必要です。

1. **VS Code:** テキストエディタ本体。
2. **Pandoc:** Markdownファイルを様々な形式（PDF, DOCX, HTML, LaTeXなど）に変換するツール。引用処理も行います。
   - **インストール:** Pandocは別途インストールが必要です。[Pandoc公式サイト](https://pandoc.org/installing.html) からダウンロードしてインストールしてください。
3. **BibTeXファイル (`.bib`):** 参考文献情報を格納するファイル。例: `references.bib`
4. **VS Code拡張機能: Pandoc Citer:** Markdownファイル内で `@` を入力した際に、`.bib` ファイル内の引用キーを自動補完してくれる拡張機能。
   - **インストール:** VS Codeの拡張機能マーケットプレイスで "Pandoc Citer" を検索し、インストールします。（`notZaki.pandocciter`）

## BibTeXファイル (`.bib`) の準備

参考文献情報をBibTeX形式で記述したファイル（例: `references.bib`）を用意します。各文献には一意の「引用キー」（Citation Key）を付けます。

**例 (`references.bib`):**

```bibtex
@article{higgins2021,
  author  = {Higgins, J. P. T. and Thomas, J. and Chandler, J. and Cumpston, M. and Li, T. and Page, M. J. and Welch, V. A. (editors)},
  title   = {Cochrane Handbook for Systematic Reviews of Interventions version 6.2 (updated February 2021)},
  journal = {Cochrane},
  year    = {2021},
  url     = {www.training.cochrane.org/handbook}
}

@book{latexcompanion,
    author    = {Michel Goossens and Frank Mittelbach and Alexander Samarin},
    title     = {The \LaTeX\ Companion},
    year      = {1993},
    publisher = {Addison-Wesley},
    address   = {Reading, Massachusetts}
}
```

この例では、`higgins2021` や `latexcompanion` が引用キーです。

## Markdownファイルでの設定と引用方法

Markdownファイル（例: `paper.md`）で引用を行うには、以下の2つのステップが必要です。

### ステップ 3.1: YAMLメタデータブロックの設定 (最重要)

Markdownファイルの**一番最初**に、どの `.bib` ファイルを参照するかを指定する「YAMLメタデータブロック」を記述します。これはPandocと「Pandoc Citer」拡張機能の両方が参照する情報です。

```yaml
---
bibliography: [references.bib] # あなたの.bibファイル名に置き換えてください
# 必要に応じて他のメタデータも追加できます (title, authorなど)
# title: "論文タイトル"
# author: "著者名"
---

# ここから論文の本文を開始します

## はじめに

ここに本文を記述します。引用は角括弧と@マーク、引用キーを使って行います [@higgins2021]。
複数の引用はセミコロンで区切ります [@higgins2021; @latexcompanion]。
```

**【注意点】**
- **`---`が必須:** YAMLメタデータブロックは、必ずファイルの先頭に `---`（ハイフン3つ）で始まり、`---` で終わる必要があります。`bibliography: [references.bib]` だけを書いても認識されません。
- **ファイル名の指定:** `bibliography:` の後に、角括弧 `[]` で囲んで、使用する `.bib` ファイル名を正確に指定します。複数指定も可能です（例: `[refs1.bib, refs2.bib]`）。
- **保存が必須:** **YAMLメタデータブロックを追加・変更したら、必ずMarkdownファイルを保存（Save）してください。** 保存しないと、「Pandoc Citer」拡張機能が `.bib` ファイルの場所を認識できず、引用キーの自動補完が機能しません。

### ステップ 3.2: 引用の挿入

本文中で引用したい箇所に `[@引用キー]` の形式で記述します。
- 例: `[@higgins2021]`
- 複数引用: `[@higgins2021; @latexcompanion]`
- 文中での著者名表示など: `[@higgins2021, p. 34]` や `[see @higgins2021, chapter 2]` のような詳細な指定も可能です（Pandocのドキュメント参照）。

## VS Code拡張機能「Pandoc Citer」による自動補完

正しく設定されていれば、「Pandoc Citer」拡張機能が動作します。

1. Markdownファイルを開き、YAMLメタデータブロックが正しく記述され、**保存されている**ことを確認します。
2. 本文中で `@` または `[@` と入力し始めると、YAMLで指定された `.bib` ファイル内の引用キーの候補が自動的に表示されるはずです。
3. 候補から選択してEnterキーを押すと、引用キーが挿入されます。

**【トラブルシューティング】**
- `@higgin` と打っても候補が出ない場合は、YAMLメタデータブロックが正しく設定されていない（`---` がない、または保存されていない）ため、「Pandoc Citer」がどの `.bib` ファイルを参照すればよいか分からない可能性があります。
- 拡張機能のインストール後も動かない場合は、まずYAMLメタデータブロックの記述と**ファイルの保存**を確認し、それでもダメならVS Codeの再起動を試すと良いでしょう。

## Pandocによるドキュメント生成

Markdownファイルと `.bib` ファイルが準備できたら、Pandocコマンドを使って最終的なドキュメント（例: DOCXやPDF）を生成します。ターミナル（VS Code内蔵ターミナルでも可）で以下のコマンドを実行します。

### Pandoc 3.x以降での引用処理（重要）

**重要:** Pandoc 3.x以降では、引用処理を行うために`--citeproc`オプションが必須となりました。これがないと`CiteprocParseError`エラーが発生します。

**Word (DOCX) ファイルを生成する場合:**
```bash
pandoc paper.md --citeproc --bibliography=references.bib -o paper.docx
```

**PDFファイルを生成する場合:**
```bash
pandoc paper.md --citeproc --bibliography=references.bib -o paper.pdf
```

- `paper.md`: あなたのMarkdownファイル名
- `--citeproc`: 引用処理エンジンを有効にします（Pandoc 3.x以降で必須）
- `--bibliography=references.bib`: 使用するBibTeXファイルを指定します（YAMLで指定していても、コマンドラインで明示するのが確実です）
- `-o paper.docx` / `-o paper.pdf`: 出力ファイル名を指定します
- **PDF生成の注意:** 高品質なPDFを生成するには、通常LaTeX（TeX LiveやMiKTeXなど）の環境が別途必要になります

### 引用スタイル（CSL）の指定

引用スタイルを指定するには`--csl`オプションを使用します：

```bash
pandoc paper.md --citeproc --bibliography=references.bib --csl=vancouver-brackets.csl -o paper.docx
```

- `--csl=vancouver-brackets.csl`: 使用する引用スタイルファイル（CSL）を指定します

Pandocは、Markdownファイル内の `[@引用キー]` を解釈し、`.bib` ファイルの情報に基づいて文中の引用表記と巻末の参考文献リストを自動的に生成します。参考文献のスタイルはCSL (Citation Style Language) ファイルを使ってカスタマイズすることも可能です。このリポジトリでは臨床医学論文でよく使用されるVancouverスタイル（角括弧）を採用しています。

## トラブルシューティング

### よくあるエラーと解決策

#### 1. `CiteprocParseError: No citation element present`

このエラーは主に以下の原因で発生します：

1. **Pandoc 3.x使用時に`--citeproc`オプションが欠けている**
   - 解決策: コマンドに`--citeproc`を追加します

2. **CSLファイルに問題がある**
   - 解決策: 正しい構造の検証済みCSLファイルを使用します
   - 公式リポジトリから信頼できるCSLファイルを入手: [Citation Style Language](https://github.com/citation-style-language/styles)

3. **YAMLフロントマターのパス指定に問題がある**
   - 解決策: 絶対パスまたは正確な相対パスを使用し、角括弧は不要です
   ```yaml
   bibliography: path/to/references.bib  # 角括弧なし
   csl: path/to/citation-style.csl
   ```

4. **オプション指定の順序や形式に誤りがある**
   - 解決策: `--csl=style.csl`と`--bibliography=refs.bib`は別々のオプションとして指定します

#### 2. 引用が正しく処理されない

1. **`.bib`ファイルのフォーマットが正しくない**
   - 解決策: BibTeXの構文を確認し、必要なフィールドがすべて含まれているか確認します

2. **引用キーが間違っている**
   - 解決策: `.bib`ファイル内の正確な引用キーを使用しているか確認します

## まとめ

1. **準備:** Pandocをインストールし、`.bib` ファイルを用意し、VS Codeに「Pandoc Citer」拡張機能をインストールします。
2. **設定:** Markdownファイルの**先頭**に `---` で囲まれたYAMLメタデータブロックを記述し、`bibliography: [your_bib_file.bib]` で参照する `.bib` ファイルを指定します。**必ずファイルを保存します。**
3. **執筆:** 本文中に `[@引用キー]` 形式で引用を挿入します。「Pandoc Citer」が `@` 入力時に候補を表示してくれます。
4. **生成:** Pandocコマンドを使って、Markdownファイルと `.bib` ファイルから引用処理済みの最終ドキュメント（DOCX, PDFなど）を生成します。

この手順に従えば、VS Code上で効率的に参考文献を管理しながら論文を執筆できるはずです。特に、YAMLメタデータブロックの正確な記述とファイルの保存が、引用補完機能を動作させる鍵となります。
