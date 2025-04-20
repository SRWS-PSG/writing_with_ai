FROM mcr.microsoft.com/devcontainers/universal:2

# 非対話モードでのデバッグ情報を抑制
ENV DEBIAN_FRONTEND=noninteractive

# git-lfsリポジトリを無効化して問題を回避
RUN rm -f /etc/apt/sources.list.d/github_git-lfs.list || true

# パッケージリストを更新し、必要なパッケージをインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Pandocのcitation processorを確保
RUN pandoc --version

# Node.jsパッケージをグローバルにインストール
RUN npm install -g \
    markdownlint-cli \
    markdown-spellcheck

# 日本語フォントのインストール
RUN rm -f /etc/apt/sources.list.d/github_git-lfs.list || true && \
    apt-get update && apt-get install -y --no-install-recommends \
    fonts-ipafont \
    fonts-ipaexfont \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 環境変数をリセット
ENV DEBIAN_FRONTEND=dialog
