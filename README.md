# 論文執筆支援リポジトリ (Academic Writing Support Repository)

このリポジトリは、AIを活用した論文執筆をサポートするためのリソースを提供します。初学者でも簡単に論文執筆を始められるよう、必要なツールのインストール方法や使い方を解説しています。

## 目次

1. [VS Codeのインストール方法](docs/vs_code_installation.md)
2. [BibTeXとPandocを使った引用管理ガイド](docs/citation_management.md)
3. [論文執筆のテンプレート](templates/)
4. [参考資料](resources/)
5. [トラブルシューティング](#トラブルシューティング)

## Pandoc 3.x対応について（重要）

**注意**: Pandoc 3.x以降では引用処理の方法が変更されています。引用処理を行う場合は必ず以下の点に注意してください：

1. `--citeproc`オプションを必ず指定する
   ```bash
   pandoc paper.md --citeproc -o paper.docx
   ```

2. YAMLフロントマターでの参考文献指定は角括弧なしの形式を推奨
   ```yaml
   ---
   bibliography: references.bib  # 角括弧なし
   ---
   ```

3. CSLファイル（引用スタイル）は検証済みのものを使用する
   ```yaml
   csl: templates/vancouver-brackets.csl
   ```

詳細については[BibTeXとPandocを使った引用管理ガイド](docs/citation_management.md)を参照してください。

## 使い方

1. このリポジトリをフォークして自分のGitHubアカウントにコピーします
2. ローカルにクローンして作業を開始します
3. 各ガイドに従ってツールをセットアップします
4. テンプレートを使って論文執筆を始めましょう
5. Pandocでの変換時は`--citeproc`オプションを忘れずに指定してください

## トラブルシューティング

### よくある問題

#### 1. 引用処理エラー: `CiteprocParseError: No citation element present`

- **原因**: Pandoc 3.x以降で`--citeproc`オプションが欠けている、またはCSLファイルに問題がある
- **解決策**: 
  - コマンドに`--citeproc`を追加する
  - 正しいCSLファイルを使用する
  - 絶対パスまたは正確な相対パスでファイルを指定する

#### 2. Wordファイルへの変換が失敗する

- **原因**: 出力ファイルが他のアプリケーションで開かれている
- **解決策**: 
  - Wordを閉じてから変換を実行する
  - 別のファイル名を指定する（例: `paper_new.docx`）

#### 3. 引用が正しく表示されない

- **原因**: YAMLフロントマターの設定が正しくない、または引用記法に誤りがある
- **解決策**:
  - YAMLフロントマターの形式を確認する（`---`で囲む）
  - 正しい引用記法を使用する（例: `[@citation_key]`）
  - Pandocコマンドに`--bibliography`と`--csl`オプションを明示的に指定する

詳細なトラブルシューティングについては[BibTeXとPandocを使った引用管理ガイド](docs/citation_management.md)のトラブルシューティングセクションを参照してください。

## 貢献について

このリポジトリへの貢献を歓迎します。改善案やバグ報告は、Issueを作成するか、Pull Requestを送信してください。
