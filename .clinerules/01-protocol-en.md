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

重要：

- 「DO NOT MODIFY THIS COMMENT BLOCK」で始まる HTML コメントブロックは参考資料として保持してください。 - 各セクションが完了した際は、対応するコメントブロック内の「\[ ] done」を「\[O] done」に変更してチェックを入れてください。

インタラクティブモード：

- 各セクションを記入する前に、ユーザーに選択肢や方向性を提示してください
- 完全な回答を自動生成せず、ユーザーの指示や選択に基づいて進めてください
- ユーザーが特定のアプローチや内容を選択できるようにしてください
- 提案を示した後、ユーザーの承認を得てから実際の内容を作成してください
- ユーザーがこのセクションの作成に苦労している場合は、HTML コメントブロック内の参考リンクを確認するよう促してください（例：「このセクションの作成に関するガイダンスについては、HTML コメントブロック内のリンクを参照すると役立つかもしれません」）

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

  重要：

  - 「DO NOT MODIFY THIS COMMENT BLOCK」で始まる HTML コメントブロックは参考資料として保持してください。 - 各セクションが完了した際は、対応するコメントブロック内の「\[ ] done」を「\[O] done」に変更してチェックを入れてください。

  インタラクティブモード：

  - 各セクションを記入する前に、ユーザーに選択肢や方向性を提示してください
  - 完全な回答を自動生成せず、ユーザーの指示や選択に基づいて進めてください
  - ユーザーが特定のアプローチや内容を選択できるようにしてください
  - 提案を示した後、ユーザーの承認を得てから実際の内容を作成してください
  - ユーザーがこのセクションの作成に苦労している場合は、HTML コメントブロック内の参考リンクを確認するよう促してください（例：「このセクションの作成に関するガイダンスについては、HTML コメントブロック内のリンクを参照すると役立つかもしれません」）

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

  重要：

  - 「DO NOT MODIFY THIS COMMENT BLOCK」で始まる HTML コメントブロックは参考資料として保持してください。 - 各セクションが完了した際は、対応するコメントブロック内の「\[ ] done」を「\[O] done」に変更してチェックを入れてください。

  インタラクティブモード：

  - 各セクションを記入する前に、ユーザーに選択肢や方向性を提示してください
  - 完全な回答を自動生成せず、ユーザーの指示や選択に基づいて進めてください
  - ユーザーが特定のアプローチや内容を選択できるようにしてください
  - 提案を示した後、ユーザーの承認を得てから実際の内容を作成してください
  - ユーザーがこのセクションの作成に苦労している場合は、HTML コメントブロック内の参考リンクを確認するよう促してください（例：「このセクションの作成に関するガイダンスについては、HTML コメントブロック内のリンクを参照すると役立つかもしれません」）

- id: method_search
  file: your_docs/review_protocol_draft.md
  section: "### 3.4 Search method"
  criteria: |
  Plans in advance methods for identifying studies, including databases to be searched, key search terms, and other sources;
  Designs searches to capture as many eligible studies as possible, covering relevant time periods;
  Ensures searches are not restricted by language or publication status unless explicitly justified (C12, C19).

  重要：

  - 「DO NOT MODIFY THIS COMMENT BLOCK」で始まる HTML コメントブロックは参考資料として保持してください。 - 各セクションが完了した際は、対応するコメントブロック内の「\[ ] done」を「\[O] done」に変更してチェックを入れてください。

  インタラクティブモード：

  - 各セクションを記入する前に、ユーザーに選択肢や方向性を提示してください
  - 完全な回答を自動生成せず、ユーザーの指示や選択に基づいて進めてください
  - ユーザーが特定のアプローチや内容を選択できるようにしてください
  - 提案を示した後、ユーザーの承認を得てから実際の内容を作成してください
  - ユーザーがこのセクションの作成に苦労している場合は、HTML コメントブロック内の参考リンクを確認するよう促してください（例：「このセクションの作成に関するガイダンスについては、HTML コメントブロック内のリンクを参照すると役立つかもしれません」）

- id: method_bias
  file: your_docs/review_protocol_draft.md
  section: "### 3.6 Assessment of risk of bias in included studies"
  criteria: |
  Plans in advance the methods for assessing risk of bias in included studies, including the specific tool(s) to be used (e.g., Cochrane 'Risk of Bias' tool for RCTs);
  Describes how the tool(s) will be implemented and the criteria for assigning judgements (e.g., low, high, unclear risk of bias) (C20);
  Specifies process for resolving disagreements between assessors.

  重要：

  - 「DO NOT MODIFY THIS COMMENT BLOCK」で始まる HTML コメントブロックは参考資料として保持してください。 - 各セクションが完了した際は、対応するコメントブロック内の「\[ ] done」を「\[O] done」に変更してチェックを入れてください。

  インタラクティブモード：

  - 各セクションを記入する前に、ユーザーに選択肢や方向性を提示してください
  - 完全な回答を自動生成せず、ユーザーの指示や選択に基づいて進めてください
  - ユーザーが特定のアプローチや内容を選択できるようにしてください
  - 提案を示した後、ユーザーの承認を得てから実際の内容を作成してください
  - ユーザーがこのセクションの作成に苦労している場合は、HTML コメントブロック内の参考リンクを確認するよう促してください（例：「このセクションの作成に関するガイダンスについては、HTML コメントブロック内のリンクを参照すると役立つかもしれません」）

- id: method_effects
  file: your_docs/review_protocol_draft.md
  section: "### 3.7 Measures of treatment effects"
  criteria: |
  Specifies the choice of effect measure for different types of data (e.g., odds ratio, risk ratio, risk difference for dichotomous outcomes; mean difference, standardized mean difference for continuous outcomes) (C21);
  Identifies methods for data synthesis, including whether a quantitative synthesis (meta-analysis) is planned, and the statistical methods for meta-analysis (e.g., inverse variance or Mantel Haenszel, fixed-effect or random-effects model) (C21).

  重要：

  - 「DO NOT MODIFY THIS COMMENT BLOCK」で始まる HTML コメントブロックは参考資料として保持してください。 - 各セクションが完了した際は、対応するコメントブロック内の「\[ ] done」を「\[O] done」に変更してチェックを入れてください。

  インタラクティブモード：

  - 各セクションを記入する前に、ユーザーに選択肢や方向性を提示してください
  - 完全な回答を自動生成せず、ユーザーの指示や選択に基づいて進めてください
  - ユーザーが特定のアプローチや内容を選択できるようにしてください
  - 提案を示した後、ユーザーの承認を得てから実際の内容を作成してください
  - ユーザーがこのセクションの作成に苦労している場合は、HTML コメントブロック内の参考リンクを確認するよう促してください（例：「このセクションの作成に関するガイダンスについては、HTML コメントブロック内のリンクを参照すると役立つかもしれません」）

- id: method_analysis_issues
  file: your_docs/review_protocol_draft.md
  section: "### 3.8 Unit of analysis issues"
  criteria: |
  Addresses how unit of analysis issues (e.g., crossover trials, cluster-RCTs, multiple observations for the same outcome) will be handled in the analysis, as part of the pre-specified plan for synthesizing results (related to C21).

  重要：

  - 「DO NOT MODIFY THIS COMMENT BLOCK」で始まる HTML コメントブロックは参考資料として保持してください。 - 各セクションが完了した際は、対応するコメントブロック内の「\[ ] done」を「\[O] done」に変更してチェックを入れてください。

  インタラクティブモード：

  - 各セクションを記入する前に、ユーザーに選択肢や方向性を提示してください
  - 完全な回答を自動生成せず、ユーザーの指示や選択に基づいて進めてください
  - ユーザーが特定のアプローチや内容を選択できるようにしてください
  - 提案を示した後、ユーザーの承認を得てから実際の内容を作成してください
  - ユーザーがこのセクションの作成に苦労している場合は、HTML コメントブロック内の参考リンクを確認するよう促してください（例：「このセクションの作成に関するガイダンスについては、HTML コメントブロック内のリンクを参照すると役立つかもしれません」）

- id: method_missing_data
  file: your_docs/review_protocol_draft.md
  section: "### 3.9 Dealing with missing data"
  criteria: |
  Describes the planned approach for dealing with missing data for outcomes, as part of the pre-specified plan for synthesizing results (related to C21).

  重要：

  - 「DO NOT MODIFY THIS COMMENT BLOCK」で始まる HTML コメントブロックは参考資料として保持してください。 - 各セクションが完了した際は、対応するコメントブロック内の「\[ ] done」を「\[O] done」に変更してチェックを入れてください。

  インタラクティブモード：

  - 各セクションを記入する前に、ユーザーに選択肢や方向性を提示してください
  - 完全な回答を自動生成せず、ユーザーの指示や選択に基づいて進めてください
  - ユーザーが特定のアプローチや内容を選択できるようにしてください
  - 提案を示した後、ユーザーの承認を得てから実際の内容を作成してください
  - ユーザーがこのセクションの作成に苦労している場合は、HTML コメントブロック内の参考リンクを確認するよう促してください（例：「このセクションの作成に関するガイダンスについては、HTML コメントブロック内のリンクを参照すると役立つかもしれません」）

- id: method_heterogeneity
  file: your_docs/review_protocol_draft.md
  section: "### 3.10 Assessment of heterogeneity"
  criteria: |
  Explains methods planned for assessing statistical heterogeneity (e.g., visual inspection of forest plots, Chi² test, I² statistic) and criteria for interpreting its extent, as part of the synthesis plan (C21).

  重要：

  - 「DO NOT MODIFY THIS COMMENT BLOCK」で始まる HTML コメントブロックは参考資料として保持してください。 - 各セクションが完了した際は、対応するコメントブロック内の「\[ ] done」を「\[O] done」に変更してチェックを入れてください。

  インタラクティブモード：

  - 各セクションを記入する前に、ユーザーに選択肢や方向性を提示してください
  - 完全な回答を自動生成せず、ユーザーの指示や選択に基づいて進めてください
  - ユーザーが特定のアプローチや内容を選択できるようにしてください
  - 提案を示した後、ユーザーの承認を得てから実際の内容を作成してください
  - ユーザーがこのセクションの作成に苦労している場合は、HTML コメントブロック内の参考リンクを確認するよう促してください（例：「このセクションの作成に関するガイダンスについては、HTML コメントブロック内のリンクを参照すると役立つかもしれません」）

- id: method_subgroup
  file: your_docs/review_protocol_draft.md
  section: "### 3.13 Subgroup analysis and investigation of heterogeneity"
  criteria: |
  Predefines any planned subgroup analyses, specifying potential effect modifiers;
  Restricts the number of subgroup analyses and provides a clear rationale for each (C22).

  重要：

  - 「DO NOT MODIFY THIS COMMENT BLOCK」で始まる HTML コメントブロックは参考資料として保持してください。 - 各セクションが完了した際は、対応するコメントブロック内の「\[ ] done」を「\[O] done」に変更してチェックを入れてください。

  インタラクティブモード：

  - 各セクションを記入する前に、ユーザーに選択肢や方向性を提示してください
  - 完全な回答を自動生成せず、ユーザーの指示や選択に基づいて進めてください
  - ユーザーが特定のアプローチや内容を選択できるようにしてください
  - 提案を示した後、ユーザーの承認を得てから実際の内容を作成してください
  - ユーザーがこのセクションの作成に苦労している場合は、HTML コメントブロック内の参考リンクを確認するよう促してください（例：「このセクションの作成に関するガイダンスについては、HTML コメントブロック内のリンクを参照すると役立つかもしれません」）

- id: method_sof
  file: your_docs/review_protocol_draft.md
  section: "### 3.15 Summary of findings table"
  criteria: |
  Plans in advance the methods for assessing the quality of evidence (e.g., GRADE approach) for the main outcomes (C23);
  Specifies which outcomes (typically up to seven critical or important outcomes for decision making, as defined in C14, C15) will be included in the 'Summary of Findings' table and how they will be presented (C23);
  Defines acceptable outcome measures, selection from multiple measures, and time points of interest for these outcomes if not covered elsewhere (C16, C17, C18).

  重要：

  - 「DO NOT MODIFY THIS COMMENT BLOCK」で始まる HTML コメントブロックは参考資料として保持してください。 - 各セクションが完了した際は、対応するコメントブロック内の「\[ ] done」を「\[O] done」に変更してチェックを入れてください。

  インタラクティブモード：

  - 各セクションを記入する前に、ユーザーに選択肢や方向性を提示してください
  - 完全な回答を自動生成せず、ユーザーの指示や選択に基づいて進めてください
  - ユーザーが特定のアプローチや内容を選択できるようにしてください
  - 提案を示した後、ユーザーの承認を得てから実際の内容を作成してください
  - ユーザーがこのセクションの作成に苦労している場合は、HTML コメントブロック内の参考リンクを確認するよう促してください（例：「このセクションの作成に関するガイダンスについては、HTML コメントブロック内のリンクを参照すると役立つかもしれません」）

- id: method_complete
  file: your_docs/review_protocol_draft.md
  section: "## 3. Method"
  criteria: |
  All method subsections are complete, adhering to MECIR standards, with appropriate detail and rigor.
  Data collection, synthesis plans, and analysis approaches are well-defined and pre-specified.

  重要：

  - 「DO NOT MODIFY THIS COMMENT BLOCK」で始まる HTML コメントブロックは参考資料として保持してください。 - 各セクションが完了した際は、対応するコメントブロック内の「\[ ] done」を「\[O] done」に変更してチェックを入れてください。

  インタラクティブモード：

  - 各セクションを記入する前に、ユーザーに選択肢や方向性を提示してください
  - 完全な回答を自動生成せず、ユーザーの指示や選択に基づいて進めてください
  - ユーザーが特定のアプローチや内容を選択できるようにしてください
  - 提案を示した後、ユーザーの承認を得てから実際の内容を作成してください
  - ユーザーがこのセクションの作成に苦労している場合は、HTML コメントブロック内の参考リンクを確認するよう促してください（例：「このセクションの作成に関するガイダンスについては、HTML コメントブロック内のリンクを参照すると役立つかもしれません」）

# STEP 3 — Introduction

- id: intro
  file: your_docs/review_protocol_draft.md
  section: "## 1. Introduction"
  criteria: |
  Provides background on the topic, explains the rationale for the review, and justifies its necessity by identifying gaps or uncertainties in existing evidence, thereby relating to the importance for review users (related to C1, C2);
  Must cite prior relevant studies or reviews.

  The introduction should also explicitly position the systematic review in relation to existing literature using one of the following justification categories:

  1. Update of prior SR:

  - Definition: The review explicitly mentions updating a prior systematic review on the same research question but with a newer search date.
  - Example: "We aimed to update the information provided by our previous report (Author et al.)"
  - Key indicators: Mentions previous SR with same question, emphasizes new time period covered.

  2. New in scope than prior SR:

  - Definition: The review references prior systematic reviews on similar research questions but explains how this review differs in scope (e.g., different population, intervention, or outcomes).
  - Example: "Previous reviews have mainly reported results for \[outcome X] rather than \[outcome Y] and omitted the growing body of evidence from observational studies on this topic, which often include larger study populations in real-world settings and longer follow-up." - Key indicators: Explicitly compares scope with previous reviews, highlights differences in PICO elements.

  3. Higher quality than prior SR:

  - Definition: The review references prior systematic reviews on similar questions but identifies methodological problems or limitations in previous reviews, or introduces advanced methods like network meta-analysis.
  - Example: "This method allows comparison of all available medications against placebo and between pharmacological agents despite the paucity of head-to-head comparisons of therapies in RCTs."
  - Key indicators: Critiques methods of prior reviews, proposes methodological improvements.

  4. Completely new SR:

  - Definition: The review explicitly states it is the first systematic review on this topic or research question.
  - Example: "To date, to our knowledge, no studies have comprehensively examined \[topic X]" or "No clinical practice guidelines include \[intervention X]. This systematic review focuses on this gap."
  - Key indicators: Explicitly claims to be first SR, identifies absence of previous synthesis.

  5. Limitations of primary studies only:

  - Definition: The review does not mention prior systematic reviews but discusses limitations of primary studies that necessitate a systematic review.
  - Example: "Previous studies have largely been single centre trials with a small sample size, not powered to assess the true effect of \[intervention] and whether it interacts with important clinical subgroups."
  - Key indicators: Discusses weaknesses of individual studies without referencing previous synthesis efforts.

  重要：

  - 「DO NOT MODIFY THIS COMMENT BLOCK」で始まる HTML コメントブロックは参考資料として保持してください。 - 各セクションが完了した際は、対応するコメントブロック内の「\[ ] done」を「\[O] done」に変更してチェックを入れてください。

  インタラクティブモード：

  - 各セクションを記入する前に、ユーザーに選択肢や方向性を提示してください
  - 完全な回答を自動生成せず、ユーザーの指示や選択に基づいて進めてください
  - ユーザーが特定のアプローチや内容を選択できるようにしてください
  - 提案を示した後、ユーザーの承認を得てから実際の内容を作成してください
  - ユーザーがこのセクションの作成に苦労している場合は、HTML コメントブロック内の参考リンクを確認するよう促してください（例：「このセクションの作成に関するガイダンスについては、HTML コメントブロック内のリンクを参照すると役立つかもしれません」）

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
