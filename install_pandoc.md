# pandoc インストールメモ

当日は詳しく説明しすぎず、「MarkdownをWordやPDFに変換するアプリ」として扱う。

## Windows

PowerShellで確認:

```powershell
pandoc --version
```

入っていなければ、AIチャットに次のように依頼する。

```text
Windowsにpandocをインストールする手順を、私の環境に合わせて案内してください。
インストール後に pandoc --version で確認するところまでお願いします。
```

wingetが使える場合:

```powershell
winget install --id JohnMacFarlane.Pandoc -e
```

## macOS

```bash
brew install pandoc
pandoc --version
```

## PDFについて

PDF出力はLaTeXなど追加環境が必要で詰まりやすい。今回の必須到達点は `docx` とする。

