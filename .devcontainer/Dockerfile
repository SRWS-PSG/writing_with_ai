FROM mcr.microsoft.com/devcontainers/universal:2

# パッケージインストール時に非対話モードを設定
ENV DEBIAN_FRONTEND=noninteractive

# git-lfsリポジトリの問題を回避し、パッケージリストを一度だけ更新
RUN rm -f /etc/apt/sources.list.d/github_git-lfs.list || true && \
    apt-get update

# 必要なパッケージ（Pandoc, TeX Live, 日本語フォント）をまとめてインストール
RUN apt-get install -y --no-install-recommends \
    pandoc \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    fonts-ipafont \
    fonts-ipaexfont \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Pandocのバージョンを確認
RUN pandoc --version

# Node.jsパッケージをグローバルにインストール
RUN npm install -g \
    markdownlint-cli \
    markdown-spellcheck
