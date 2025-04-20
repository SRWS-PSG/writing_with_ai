# 論文執筆支援リポジトリ (Academic Writing Support Repository)

このリポジトリは、AIを活用した論文執筆をサポートするためのリソースを提供します。初学者でも簡単に論文執筆を始められるよう、必要なツールのインストール方法や使い方を解説しています。

## AIを活用した論文執筆ワークフロー

以下は、AIツール（GitHub CopilotやClaude）を活用した論文執筆の基本的なワークフローです：

```mermaid
graph LR
  A[研究計画] -->|Copilot Outline| B(Draft.md)
  B -->|Cline Polishing| C(Review PR)
  C --> D[最終原稿]
  
  style A fill:#f9f9f9,stroke:#333,stroke-width:1px
  style B fill:#e1f5fe,stroke:#0288d1,stroke-width:1px
  style C fill:#e8f5e9,stroke:#388e3c,stroke-width:1px
  style D fill:#fff3e0,stroke:#f57c00,stroke-width:1px
```

各ステップでのAIツール活用ポイント：
- **研究計画**: [section_outline.prompt](resources/prompts/section_outline.prompt)を使用して論文の骨子を生成
- **ドラフト作成**: GitHub Copilotを使用して各セクションの文章を生成・補完
- **文章洗練**: [refinement.prompt](resources/prompts/refinement.prompt)を使用して医学雑誌スタイルに調整
- **統計結果の記述**: [stats2sentence.prompt](resources/prompts/stats2sentence.prompt)を使用して統計結果を英文に変換

## 目次

1. [VS Codeのインストール方法](docs/vs_code_installation.md)
2. [BibTeXとPandocを使った引用管理ガイド](docs/citation_management.md)
3. [論文執筆のテンプレート](templates/)
4. [参考資料](resources/)
5. [トラブルシューティング](#トラブルシューティング)

## 使い方

1. このリポジトリをフォークして自分のGitHubアカウントにコピーします
2. ローカルにクローンして作業を開始します
3. 各ガイドに従ってツールをセットアップします
4. テンプレートを使って論文執筆を始めましょう

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
