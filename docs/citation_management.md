# VS Codeで論文執筆: BibTeXとPandocを使った引用管理ガイド

VS CodeとMarkdownを使って論文を執筆する際に、BibTeXファイル（`.bib`）で参考文献を管理し、Pandocを使って引用を含む最終的なドキュメント（特にWord形式）を生成する方法について説明します。特に初心者の方がつまずきやすいポイント（引用が出力されない問題）に焦点を当てて解説します。

## 目次

1. [必要なツール](#必要なツール)
2. [BibTeXファイル (`.bib`) の準備](#bibteXファイル-bib-の準備)
3. [Markdownファイルでの設定と引用方法](#markdownファイルでの設定と引用方法)
4. [VS Code拡張機能「Pandoc Citer」による自動補完](#vs-code拡張機能pandoc-citerによる自動補完)
5. [Pandocによるドキュメント生成](#pandocによるドキュメント生成)
6. [フォルダ構造チェックリスト](#フォルダ構造チェックリスト)
7. [トラブルシューティング Q&A](#トラブルシューティング-qa)
8. [VS Code 連携 Tips](#vs-code-連携-tips)
9. [まとめ](#まとめ)

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

### BibTeXファイルの取得方法1: Citation Managerからのエクスポート

参考文献管理ソフトウェア（Citation Manager）からBibTeXファイルを直接エクスポートする方法は、最も効率的で正確にBibTeXファイルを作成する方法です。主要な文献管理ソフトウェアでの操作手順を説明します。

#### Zoteroからのエクスポート

1. **コレクション単位でのエクスポート**:
   - Zoteroのライブラリで、エクスポートしたいコレクション（フォルダ）を右クリック
   - 「エクスポート...」を選択
   - 形式として「BibTeX」を選択
   - 「エクスポート先...」をクリックし、論文プロジェクトのフォルダを選択
   - ファイル名を「references.bib」などとして保存

2. **自動更新の設定（推奨）**:
   - Zoteroに「Better BibTeX」プラグインをインストール ([Better BibTeXのGitHub](https://github.com/retorquere/zotero-better-bibtex/releases/))
   - コレクションを右クリック→「Better BibTeX」→「コレクションをエクスポート...」を選択
   - 形式として「Better BibTeX」を選択
   - 「ファイルへ自動エクスポート」にチェック
   - 自分がローカルで論文プロジェクトフォルダに「references.bib」として保存
   - これにより、Zoteroのコレクションを更新すると自動的に.bibファイルも更新されます

#### Mendeleyからのエクスポート

1. **フォルダ単位でのエクスポート**:
   - Mendeleyの左側パネルで、エクスポートしたいフォルダを選択
   - 含まれている文献を全て選択（Ctrl+A）
   - 右クリックして「Export...」を選択
   - 「BibTeX (.bib)」を選択
   - 論文プロジェクトフォルダに「references.bib」として保存

2. **自動同期の設定**:
   - Mendeley Desktop上部メニューから「Tools」→「Options」を選択
   - 「BibTeX」タブを選択
   - 「Enable BibTeX syncing」にチェック
   - 同期先フォルダとファイル名を設定
   - 「Sync automatically」にチェック

#### EndNoteからのエクスポート

1. **グループからのエクスポート**:
   - EndNote内で、エクスポートするレファレンスを含むグループを選択
   - 全てのレファレンスを選択（Ctrl+A）
   - 「File」→「Export...」を選択
   - 「出力形式」として「BibTeX Export」を選択
   - 論文プロジェクトフォルダに「references.bib」として保存

### BibTeXファイルの取得方法2: Google Scholarからの引用情報取得

論文管理ソフトを使用していない場合でも、Google Scholarから直接BibTeX形式の引用情報を取得できます。以下に詳細な手順を説明します。

#### Google Scholarから単一の論文のBibTeX情報を取得する手順

1. **Google Scholarにアクセス**:
   - ブラウザで [Google Scholar](https://scholar.google.com/) を開きます

2. **論文を検索**:
   - 検索ボックスに論文のタイトルや著者名などのキーワードを入力
   - 検索ボタン（虫眼鏡アイコン）をクリックまたはEnterキーを押す

3. **引用オプションを表示**:
   - 検索結果から目的の論文を見つける
   - 論文タイトルの下にある「引用」（" マークのアイコン）をクリック
   ![Google Scholar引用ボタン](https://example.com/images/quote_button.jpg)

4. **BibTeX形式を選択**:
   - 表示されるポップアップウィンドウで、下部の「BibTeX」リンクをクリック
   ![BibTeXリンク](https://example.com/images/bibtex_link.jpg)

5. **BibTeX情報をコピー**:
   - 新しいウィンドウに表示されるBibTeX形式のテキストを全て選択（Ctrl+A）
   - コピー（Ctrl+C）
   ![BibTeX情報コピー](https://example.com/images/bibtex_copy.jpg)

6. **テキストエディタでBibTeXファイルを開く/作成**:
   - VS Codeなどのエディタで「references.bib」ファイルを開く（なければ新規作成）
   - ファイル末尾にカーソルを移動
   - コピーしたBibTeX情報を貼り付け（Ctrl+V）

7. **引用キーの編集（オプション）**:
   - BibTeX情報の先頭にある引用キー（例: `@article{zhang2019,`の`zhang2019`部分）を
     必要に応じて編集
   ```bibtex
   @article{zhang2019,  ← この部分が引用キー
     title={Paper title},
     author={Zhang, X and ...},
     ...
   }
   ```

8. **ファイルの保存**:
   - テキストエディタで「references.bib」ファイルを保存（Ctrl+S）

#### 複数の論文のBibTeX情報を効率的に取得する方法

1. **検索結果の絞り込み**:
   - Google Scholarで検索後、左側のフィルターを使用して検索結果を絞り込み
   - 年代、関連性などで並べ替え

2. **複数論文の選択**:
   - 引用したい各論文の左側にあるチェックボックスにチェック
   ![チェックボックス選択](https://example.com/images/checkboxes.jpg)

3. **一括引用**:
   - 検索結果上部に表示される「⋮」（縦の三点リーダー）アイコンをクリック
   - 「引用」を選択
   - 「BibTeX」を選択
   ![一括引用](https://example.com/images/batch_citation.jpg)

4. **BibTeX情報の保存と編集**:
   - 表示されるBibTeX情報を全てコピー
   - 「references.bib」ファイルに追加
   - 必要に応じて引用キーを編集

#### BibTeXファイルの管理のベストプラクティス

1. **一貫した引用キーの命名規則を使用**:
   - 例: `著者名+年度`（higgins2021）や`著者名+年度+キーワード`（smith2020review）

2. **定期的なバックアップ**:
   - .bibファイルを定期的にバックアップまたはバージョン管理システム（GitなどのVC）に保存

3. **重複エントリの確認**:
   - 同じ文献を複数回追加していないか確認
   - Zoteroの「Better BibTeX」プラグインなどのツールで重複を自動検出

4. **引用キーの衝突を避ける**:
   - 異なる文献に同じ引用キーを使用しないよう注意

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

Markdownファイルと `.bib` ファイルが準備できたら、Pandocコマンドを使って最終的なドキュメント（Word形式）を生成します。ターミナル（VS Code内蔵ターミナルでも可）で以下のコマンドを実行します。

### 目的別に最低限必要なPandocオプション

**重要:** Pandoc 3系では、`--citeproc` オプションを付け忘れると引用が正しく処理されません。特にWord (docx) 出力では、このオプションがないと文献が挿入されない現象が発生します。

| 出力形式 | 最低限必要なコマンド例 | ワンポイント |
|---------|----------------------|-------------|
| **Word (docx)** | `pandoc paper.md --citeproc --bibliography=references.bib --csl=vancouver-brackets.csl -o paper.docx` | `--citeproc` を付けないと Pandoc 3 系では _docx の⾃前 citation 機構_ が優先され、文献が挿入されません |

- `paper.md`: あなたのMarkdownファイル名
- `--citeproc`: **必須オプション**。引用処理エンジンを有効にします。Pandoc 3.x以降では、これがないと引用が正しく処理されません。
- `--bibliography=references.bib`: 使用するBibTeXファイルを指定します。（YAMLで指定していても、コマンドラインで明示するのが確実です）
- `--csl=vancouver-brackets.csl`: 引用スタイルを指定します。このリポジトリでは臨床医学論文でよく使用されるVancouverスタイル（角括弧）を採用しています。
- `-o paper.docx`: 出力ファイル名を指定します。

### YAMLメタデータとCLIオプションの関係

Markdownファイルの先頭にYAMLメタデータで設定した情報と、コマンドラインオプションの関係は以下のようになります：

```yaml
---
bibliography: references.bib
csl: vancouver-brackets.csl   # Vancouver 系
...
---
```

**重要ポイント:**
- YAMLに書いても `--citeproc` は必須です
- コマンドラインオプションはYAMLの設定より優先されます
- 両方に指定がある場合はコマンドラインの指定が使用されます

### Windows/PowerShellでの実行例

PowerShellでは、長いコマンドを複数行に分ける場合、バックスラッシュ (`\`) ではなく、バッククォート (`` ` ``) を使用します：

```powershell
pandoc paper.md --citeproc `
  --bibliography=references.bib `
  --csl=vancouver-brackets.csl `
  -o paper.docx
```

Pandocは、Markdownファイル内の `[@引用キー]` を解釈し、`.bib` ファイルの情報に基づいて文中の引用表記と巻末の参考文献リストを自動的に生成します。参考文献のスタイルはCSL (Citation Style Language) ファイルを使ってカスタマイズすることも可能です。このリポジトリでは臨床医学論文でよく使用されるVancouverスタイル（角括弧）を採用しています。

## フォルダ構造チェックリスト

引用処理がうまく機能しない場合は、以下のフォルダ構造を確認してください：

- `paper.md`、`references.bib`、`*.csl` ファイルが同じフォルダにあるか
- `pandoc.exe` はPATHが通っているか（フォルダに直接置く必要はありません）

PowerShellで現在のフォルダ内のファイルを確認するコマンド：

```powershell
Get-ChildItem -Path . -File
```

再帰的に全てのファイルを確認する場合：

```powershell
Get-ChildItem -Path . -Recurse -File
```

## トラブルシューティング Q&A

| 症状 | 主な原因 | 解決策 |
|------|---------|--------|
| 引用が[?]で表示される・本文中に残る | `--citeproc` なし | `--citeproc` オプションを付ける |
| 参考文献リストが空 | `.bib` へパス誤り／キーが未使用 | ファイルパスを確認・不要エントリ削除 |
| 文献が2重出力 | Pandoc 3.6+ で `--citeproc` を付けずにWord出力 | `--citeproc` を明示する（3.6.4のリリースノート参照） |

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

## VS Code 連携 Tips

### Tasks.jsonでビルドタスクを登録

VS Codeの `.vscode/tasks.json` にPandocビルドタスクを登録すると、ショートカットキー（Ctrl+Shift+B）で簡単にドキュメント生成ができます：

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Build Word Document",
      "type": "shell",
      "command": "pandoc ${file} --citeproc --bibliography=references.bib --csl=vancouver-brackets.csl -o ${fileBasenameNoExtension}.docx",
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

### Pandoc Citer拡張機能の活用

「Pandoc Citer」拡張機能の設定をカスタマイズすることで、より効率的に引用を挿入できます：

1. VS Codeの設定（Settings）を開く
2. 「Pandoc Citer」で検索
3. 以下の設定をカスタマイズ：
   - `pandocciter.biblioFiles`: 複数の.bibファイルを指定
   - `pandocciter.triggerCharacter`: 引用補完を開始する文字（デフォルトは`@`）

### Better BibTeX + Zoteroで.bibを自動エクスポート

Zoteroの「Better BibTeX」プラグインを使用すると、文献管理と.bibファイルの自動更新が可能になります：

1. Zoteroに「Better BibTeX」プラグインをインストール
2. コレクションを右クリック→「Better BibTeX」→「自動エクスポート」を選択
3. 出力先を論文プロジェクトフォルダに設定
4. 「自動更新を有効にする」にチェック

これにより、Zoteroで文献を追加・編集すると自動的に.bibファイルが更新されます。

## 参考リソース

:::info
**重要な参考リンク**

- [Pandoc 公式マニュアル「9 Citations」](https://pandoc.org/chunkedhtml-demo/9-citations.html)
- [CSL 公式スタイルレポジトリ](https://github.com/citation-style-language/styles)
- [Pandoc FAQ "Why don't my citations appear?"](https://pandoc.org/faqs.html)
:::

## まとめ

1. **準備:** Pandocをインストールし、`.bib` ファイルを用意し、VS Codeに「Pandoc Citer」拡張機能をインストールします。
2. **設定:** Markdownファイルの**先頭**に `---` で囲まれたYAMLメタデータブロックを記述し、`bibliography: [your_bib_file.bib]` で参照する `.bib` ファイルを指定します。**必ずファイルを保存します。**
3. **執筆:** 本文中に `[@引用キー]` 形式で引用を挿入します。「Pandoc Citer」が `@` 入力時に候補を表示してくれます。
4. **生成:** Pandocコマンドを使って、Markdownファイルと `.bib` ファイルから引用処理済みの最終ドキュメント（Word形式）を生成します。**必ず `--citeproc` オプションを付けてください。**

この手順に従えば、VS Code上で効率的に参考文献を管理しながら論文を執筆できるはずです。特に、YAMLメタデータブロックの正確な記述とファイルの保存が引用補完機能を動作させる鍵となり、`--citeproc` オプションの指定が正しい引用処理の鍵となります。
