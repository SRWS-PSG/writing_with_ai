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
この順序は論文の構造とは異なりますが、研究設計の効率的な構築のために SRWS-PSG によって推奨されています。
各セクションは MECIR 基準を満たした時点で完了としてマークし、すべて完了後に DOCX へエクスポートします。

steps:

# STEP 1 — Research question

- id: rq
  file: your_docs/review_protocol_draft.md
  section: "## 2. Research question"
  criteria: |
  Defines the review objectives in advance, specifying Population (P), Intervention (I), Comparison (C), and Outcomes (O) (PICO) (C2);
  Ensures the review question, particularly the outcomes, addresses issues important to review users (e.g., consumers, health professionals, policy makers) (C1);
  Considers relevance to specific populations and equity where appropriate (C4);

  Defines in advance outcomes critical to the review, including potential benefits and harms, and any additional important outcomes (O) (C3, C14, C15).

# STEP 2 — Method

- id: method_type_studies
  file: your_docs/review_protocol_draft.md
  section: "#### 3.2.1 Type of studies"
  criteria: |
  Defines eligibility criteria for participants (P) (C5), interventions (I), and comparators (C) (C7);
  Defines in advance clear and unambiguous eligibility criteria for study designs, focusing on features rather than labels (C9);
  Includes randomized trials if feasible for the review's questions (C10);
  Justifies the choice of eligible study designs, especially if including non-randomized studies or restricting to certain designs (C11);
  Clarifies if specific outcomes are used as criteria for including studies (C8);
  Defines in advance how studies that include only a subset of relevant participants will be addressed (C6).

- id: method_search
  file: your_docs/review_protocol_draft.md
  section: "### 3.4 Search method"
  criteria: |
  Plans in advance methods for identifying studies, including databases to be searched, key search terms, and other sources;
  Designs searches to capture as many eligible studies as possible, covering relevant time periods;
  Ensures searches are not restricted by language or publication status unless explicitly justified (C12, C19).

- id: method_bias
  file: your_docs/review_protocol_draft.md
  section: "### 3.6 Assessment of risk of bias in included studies"
  criteria: |
  Plans in advance the methods for assessing risk of bias in included studies, including the specific tool(s) to be used (e.g., Cochrane 'Risk of Bias' tool for RCTs);
  Describes how the tool(s) will be implemented and the criteria for assigning judgements (e.g., low, high, unclear risk of bias) (C20);
  Specifies process for resolving disagreements between assessors.

- id: method_effects
  file: your_docs/review_protocol_draft.md
  section: "### 3.7 Measures of treatment effects"
  criteria: |
  Specifies the choice of effect measure for different types of data (e.g., odds ratio, risk ratio, risk difference for dichotomous outcomes; mean difference, standardized mean difference for continuous outcomes) (C21);
  Identifies methods for data synthesis, including whether a quantitative synthesis (meta-analysis) is planned, and the statistical methods for meta-analysis (e.g., inverse variance or Mantel Haenszel, fixed-effect or random-effects model) (C21).

- id: method_analysis_issues
  file: your_docs/review_protocol_draft.md
  section: "### 3.8 Unit of analysis issues"
  criteria: |
  Addresses how unit of analysis issues (e.g., crossover trials, cluster-RCTs, multiple observations for the same outcome) will be handled in the analysis, as part of the pre-specified plan for synthesizing results (related to C21).

- id: method_missing_data
  file: your_docs/review_protocol_draft.md
  section: "### 3.9 Dealing with missing data"
  criteria: |
  Describes the planned approach for dealing with missing data for outcomes, as part of the pre-specified plan for synthesizing results (related to C21).

- id: method_heterogeneity
  file: your_docs/review_protocol_draft.md
  section: "### 3.10 Assessment of heterogeneity"
  criteria: |
  Explains methods planned for assessing statistical heterogeneity (e.g., visual inspection of forest plots, Chi² test, I² statistic) and criteria for interpreting its extent, as part of the synthesis plan (C21).

- id: method_subgroup
  file: your_docs/review_protocol_draft.md
  section: "### 3.13 Subgroup analysis and investigation of heterogeneity"
  criteria: |
  Predefines any planned subgroup analyses, specifying potential effect modifiers;
  Restricts the number of subgroup analyses and provides a clear rationale for each (C22).

- id: method_sof
  file: your_docs/review_protocol_draft.md
  section: "### 3.15 Summary of findings table"
  criteria: |
  Plans in advance the methods for assessing the quality of evidence (e.g., GRADE approach) for the main outcomes (C23);
  Specifies which outcomes (typically up to seven critical or important outcomes for decision making, as defined in C14, C15) will be included in the 'Summary of Findings' table and how they will be presented (C23);
  Defines acceptable outcome measures, selection from multiple measures, and time points of interest for these outcomes if not covered elsewhere (C16, C17, C18).

- id: method_complete
  file: your_docs/review_protocol_draft.md
  section: "## 3. Method"
  criteria: |
  All method subsections are complete, adhering to MECIR standards, with appropriate detail and rigor.
  Data collection, synthesis plans, and analysis approaches are well-defined and pre-specified.

# STEP 3 — Introduction

- id: intro
  file: your_docs/review_protocol_draft.md
  section: "## 1. Introduction"
  criteria: |
  Provides background on the topic, explains the rationale for the review, and justifies its necessity by identifying gaps or uncertainties in existing evidence, thereby relating to the importance for review users (related to C1, C2);
  May cite prior relevant studies or reviews.

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
