# .clinerules/01-protocol-en.md

# -------------------------------------------------------------------

# Workflow: Systematic-Review Protocol (English)

# Copy template + CSL + Bib → work on the copies → export DOCX

# -------------------------------------------------------------------

setup:

# ── Step 0 ── テンプレートと引用スタイル & BibTeX を your_docs/ に複製

- command: >
  mkdir -p your_docs ;
  cp -n templates/systematic_review_protocol_template_en.md your_docs/review_protocol_draft.md ;
  cp -n templates/vancouver-brackets.csl your_docs/vancouver-brackets.csl ;
  cp -n templates/references_sr_protocol.bib your_docs/references_sr_protocol.bib

workflow:
name: SR_Protocol_Workflow_EN
description: |
作成順序は Research question → Method → Introduction の順で進行します。
この順序は論文の構造とは異なりますが、研究設計の効率的な構築のために推奨されています。
各セクションは基準を満たした時点で完了としてマークし、すべて完了後に DOCX へエクスポートします。

steps:

# STEP 1 — Research question

- id: rq
  file: your_docs/review_protocol_draft.md
  section: "## 2. Research question"
  criteria: |
  Clearly defines Population, Intervention, Comparison, Outcome (PICO)
  and states at least one primary outcome.

# STEP 2 — Method

- id: method_type_studies
  file: your_docs/review_protocol_draft.md
  section: "#### 3.2.1 Type of studies"
  criteria: |
  Clearly specifies study types to include and exclude,
  with appropriate justification.
- id: method_search
  file: your_docs/review_protocol_draft.md
  section: "### 3.4 Search method"
  criteria: |
  Describes comprehensive search strategy including databases,
  search terms, and additional resources.
- id: method_bias
  file: your_docs/review_protocol_draft.md
  section: "### 3.6 Assessment of risk of bias in included studies"
  criteria: |
  Specifies tools and methods for assessing risk of bias
  with clear process for resolving disagreements.
- id: method_effects
  file: your_docs/review_protocol_draft.md
  section: "### 3.7 Measures of treatment effects"
  criteria: |
  Defines how effects will be measured and pooled for
  both binary and continuous variables.
- id: method_analysis_issues
  file: your_docs/review_protocol_draft.md
  section: "### 3.8 Unit of analysis issues"
  criteria: |
  Addresses how to handle crossover trials, cluster-RCTs,
  and interventions with multiple dosages.
- id: method_missing_data
  file: your_docs/review_protocol_draft.md
  section: "### 3.9 Dealing with missing data"
  criteria: |
  Describes approach for handling missing data for both
  dichotomous and continuous outcomes.
- id: method_heterogeneity
  file: your_docs/review_protocol_draft.md
  section: "### 3.10 Assessment of heterogeneity"
  criteria: |
  Explains methods for assessing statistical heterogeneity
  and interpretation criteria.
- id: method_subgroup
  file: your_docs/review_protocol_draft.md
  section: "### 3.13 Subgroup analysis and investigation of heterogeneity"
  criteria: |
  Identifies planned subgroup analyses with clear rationale.
- id: method_sof
  file: your_docs/review_protocol_draft.md
  section: "### 3.15 Summary of findings table"
  criteria: |
  Specifies outcomes to be included in Summary of findings table
  and mentions GRADE approach for quality assessment.
- id: method_complete
  file: your_docs/review_protocol_draft.md
  section: "## 3. Method"
  criteria: |
  All method subsections are complete with appropriate detail and rigor.
  Data collection, synthesis plans, and analysis approaches are well-defined.

# STEP 3 — Introduction

- id: intro
  file: your_docs/review_protocol_draft.md
  section: "## 1. Introduction"
  criteria: |
  Explains the background/rationale, cites at least one prior study,
  and justifies the need for this systematic review.

modes:
default: plan # Cline starts in Plan mode

output:
on_complete: - command: >
mkdir -p dist ;
pandoc --strip-comments
--csl your_docs/vancouver-brackets.csl
--bibliography your_docs/references_sr_protocol.bib
your_docs/review_protocol_draft.md
-o dist/protocol_final.docx - message: |
🎉 All sections marked done! The finished DOCX (with Vancouver-style references) is saved to `dist/protocol_final.docx`.
