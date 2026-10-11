---
title: "AI-assisted manuscript drafting in clinical epidemiology"
author: "Workshop participant"
date: "2026-05-13"
bibliography: refs.bib
csl: styles/american-medical-association.csl
---

# Background

Clinical epidemiology projects often require repeated rewriting of the same core ideas for protocols, abstracts, manuscripts, and responses to reviewers. Large language models can support this process, but [Please cite evidence for this claim, or soften it.]{.comment-start id="1" author="Yuki Kataoka" date="2026-09-12T02:55:46Z"}[\[修正\] 表現を can に弱め、AI 生成引用の評価研究を引用しました (Background 第1段落)。]{.comment-start id="1000" author="Taro Yamada" date="2026-09-12T00:00:00Z"}uncontrolled use [may]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"}[can]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} introduce fabricated citations[]{.comment-end id="1000"}[]{.comment-end id="1"} or wording that overstates the [evidence.]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"}[evidence, as reported in recent evaluations of AI-generated references [@page2021prisma].]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} Reporting guidelines such as PRISMA and STROBE remain useful anchors when researchers use AI during drafting [@page2021prisma; @vonelm2007strobe].

# Objective [and scope]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"}

This short demonstration shows how a manuscript draft can be managed as a project folder in an IDE. The goal is to separate the human decisions about structure, evidence, and interpretation from the AI-assisted work of revising language and generating document outputs.

# Methods

The draft is written in Markdown. References are stored in `refs.bib`, and citations are rendered with pandoc using a CSL file. Figures are stored under `assets/` and embedded by relative path.

![Figure 1. Workflow for writing with AI.](assets/figure1.png)

The workflow has four steps:

1. Write or paste a rough draft into `draft.md`.
2. [Why one section at a time? Explain the rationale in one sentence.]{.comment-start id="2" author="Yuki Kataoka" date="2026-09-12T02:55:46Z"}[\[修正\] 「プロトコルと突き合わせて確認できるように」という理由を1文追加しました (Methods, 手順 2)。]{.comment-start id="1001" author="Taro Yamada" date="2026-09-12T00:00:00Z"}Ask the AI to revise one section at a [time.]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"}[time, so that each change can be reviewed against the protocol.]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"}[]{.comment-end id="1001"}[]{.comment-end id="2"}
3. Keep citations restricted to entries in `refs.bib`.
4. Render the document to Word with pandoc.

# Results

The main output is a Word document generated from the Markdown file. The generated document [shoud]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"}[should]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} be checked manually, especially citation placement, figure captions, and any claim about study design or interpretation.

| [Step]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | [Tool]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | [Output]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} |
|------|------|--------|
| [Draft]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | [IDE + AI]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | [draft.md]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} |
| [Render]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | [pandoc]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | [draft.docx]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} |
| [Review]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | [Google Docs]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | [comments, suggestions]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} |

# [ここに　demo\assets\study_flow.drawio　からpngにして追加して]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"}

# Discussion

AI-assisted writing is most useful when the project files are explicit and the revision target is narrow. For example, asking the AI to revise only the Background section is easier to review than asking it to rewrite the whole manuscript. [Add a sentence on how disagreements between AI output and the protocol are resolved.]{.comment-start id="3" author="Reviewer B" date="2026-09-12T02:55:46Z"}[\[修正\] プロトコル優先とし、食い違いはプロジェクトログに記録する旨を Discussion 末尾に追加しました。]{.comment-start id="1002" author="Taro Yamada" date="2026-09-12T00:00:00Z"}The researcher remains responsible for the argument,[]{.comment-end id="1002"}[]{.comment-end id="3"} the evidence, and the final wording. [When AI output conflicts with the protocol, the protocol takes precedence and the discrepancy is recorded in the project log.]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"}

# [Journals increasingly require the exact model version; keep this section.]{.comment-start id="4" author="Reviewer B" date="2026-09-12T02:55:46Z"}[\[修正せず\] ご指摘のとおりこのセクションは維持します。バージョン表記は投稿時に最終確認します。]{.comment-start id="1003" author="Taro Yamada" date="2026-09-12T00:00:00Z"}AI disclosure example[]{.comment-end id="1003"}[]{.comment-end id="4"}

We used Antigravity 1.18.3 with Claude Opus 4.6 (Anthropic) and/or Gemini 3.1 pro etc. to assist in editing manuscript. All outputs were critically reviewed, executed, and verified by the authors.
