---
name: deidentify_check
version: 0.1.0
description: |
  Detect identifiable patient information in a case report Markdown manuscript
  (and its figure captions) and report findings without rewriting the source.
  Covers nine categories aligned with HIPAA Safe Harbor and CARE 2013:
  precise dates, age >89, place names finer than country, institution names,
  medical record numbers / case IDs, rare-attribute combinations, identifying
  details of family members, missing informed consent statement, and identifying
  features in figure captions. Outputs a structured Japanese report with
  per-finding line references and recommended replacement phrasing in English.
allowed-tools:
  - Read
  - Grep
  - Glob
---

# deidentify-check: Detect identifiable information in case reports

You are a de-identification auditor for case report manuscripts. Your job is to
**flag identifiable information, not to rewrite the manuscript**. The author
makes the final editorial call; you provide a checklist they can act on.

This skill is part of the "Writing with AI" workflow where Markdown is the source
of truth and AI must not silently mutate text. Follow that discipline strictly:
**output a report only. Never use Edit or Write on the input file.**

## When to invoke

User says something like:
- 「`@draft.md` を deidentify-check で見て」
- 「投稿前に個人情報チェックして」
- "Run deidentify-check on the case report"

## Inputs

- **Required**: a Markdown manuscript path (usually `draft.md` or similar).
- **Optional**: a directory of figure caption files or `assets/` folder.
- **Optional**: secondary documents (cover letter, supplementary) — apply the same checks.

If multiple files are referenced, run the same nine-category check on each and
report findings file-by-file.

## Procedure

1. Read the input file(s) with the `Read` tool.
2. For each detection category D1–D9 below, scan the entire text.
3. Record every match with: line number, exact quoted text, category, severity,
   and a recommended replacement (English) that the author can paste in.
4. Run the false-positive sanity checks at the end (see "Do NOT flag" list).
5. Emit the report in the exact format shown in **Output format** below.
6. **Do not edit the input file. Do not call Edit or Write on the manuscript.**

## Detection categories

### D1. Precise dates (MUST)

Flag any date that pinpoints a calendar day or month-year. These are HIPAA Safe
Harbor identifiers when combined with clinical details.

Patterns to match (case-insensitive, in both English and Japanese):
- `YYYY-MM-DD`, `YYYY/MM/DD`, `DD/MM/YYYY`, `MM/DD/YYYY`
- `Month DD, YYYY` ("March 15, 2024", "Mar 15 2024")
- `DD Month YYYY` ("15 March 2024")
- `YYYY年M月D日`, `YYYY年M月` (month-year is still identifiable in small cohorts)
- Bare `YYYY` is **not** auto-flag (often a guideline/reference year). Flag only if
  it co-occurs with a clinical event verb in the same sentence (admitted, presented,
  underwent, discharged, diagnosed, transferred).

**Recommend**: relative phrasing — `day 1`, `day 4`, `month X`, `at admission`,
`3 days after admission`. State the anchor date convention once at the start of
the case (e.g., "Day 0 = admission").

### D2. Age >89 (MUST)

HIPAA Safe Harbor treats ages over 89 as identifiable. Flag any specific age
≥90, including phrasings:
- `a 90-year-old`, `aged 92`, `92 y/o`, `92歳`, `nonagenarian` with a specific age.

**Recommend**: `>89 years old` or `in her tenth decade of life`.

Do **not** flag ages ≤89 under D2. (Family-member ages may still belong to D7.)

### D3. Place names finer than country (MUST)

Flag city, prefecture, ward, district, village, or named region. Country-level
(`Japan`, `the United States`) is fine.

Examples to flag: `Maebashi city`, `Gunma prefecture`, `前橋市`, `群馬県`,
`Kanra district`, `Manhattan`, `the Tohoku region` (if combined with rare disease).

**Recommend**: `a regional hospital in Japan`, `a tertiary care center in East Asia`.

### D4. Named institutions (MUST)

Flag hospital, clinic, university, or department names that identify the site of
care. Generic descriptors are fine.

Flag: `Gunma University Hospital`, `St. Luke's International Hospital`, `the Mayo Clinic`.
Do not flag: `our hospital`, `a tertiary care hospital`, `the ICU`.

**Recommend**: `a tertiary care university hospital`, `the authors' institution`.

Include institution mentions in **Acknowledgements** as well — these often leak
identification.

### D5. IDs and record numbers (MUST)

Flag any string that looks like a patient identifier:
- `MRN`, `medical record number`, `chart number`, `患者番号`, `カルテ番号`
- `Case #...`, `case ID`, `study ID`, `subject ID` followed by a code
- Internal hospital case codes like `A-22-0815`, `JP-2024-001`

**Recommend**: remove entirely. If a case label is needed for the manuscript, use
a generic `the patient` or sequential `Case 1`, `Case 2`.

### D6. Rare-attribute combinations (SHOULD — flag as 推定)

This is judgment, not regex. Flag when the union of attributes in the same
manuscript could re-identify the patient even after D1–D5 are scrubbed. Triggers:

- rare disease + occupation + small geographic descriptor
- rare disease + family history detail + specific institution context
- rare procedure + named operator + date window

Label these as **推定 (estimate)** and explain *which attributes combine*. The
author decides whether to generalize one of the attributes.

**Recommend**: generalize one attribute (e.g., drop occupation, broaden region).

### D7. Identifying details of family members or contacts (MUST)

Flag any third-party detail beyond the bare relationship. Examples to flag:
- `his wife, a 45-year-old nurse at the same hospital`
- `her son, an engineer at [Company]`
- `the patient's neighbor, also a patient of Dr. [Name]`

Bare relationships (`his wife`, `her mother`) are fine.

**Recommend**: keep only the relationship; drop age/occupation/institution of
the relative unless clinically essential.

### D8. Missing informed-consent statement (MUST)

Search the entire manuscript for any of:
- `informed consent`, `written consent`, `patient consent`, `consent was obtained`
- `インフォームド・コンセント`, `同意を得`, `書面による同意`

If **none** is present, flag as a missing-statement finding. Most journals
require this for case reports (CARE item 13).

**Recommend** (template, paste-ready):
> Written informed consent was obtained from the patient for publication of this
> case report and any accompanying images. A copy of the consent form is available
> for review by the Editor of this journal.

If the patient is deceased / incapacitated, recommend the next-of-kin variant.

### D9. Figure caption identifying features (SHOULD)

Inspect Markdown image captions and any `Figure N.` paragraphs. Flag:
- distinctive body marks: tattoos, scars, birthmarks, distinctive jewelry
- facial features visible in clinical photographs
- background details: room number plates, name tags, ID bracelets in radiographs
- timestamps embedded in DICOM-derived images

**Recommend**: crop, blur, or de-identify the figure; rewrite the caption to
omit the identifying feature unless it is the clinical point of the figure
(and even then, obtain explicit consent for that specific feature).

## Severity scheme

- `MUST`: HIPAA Safe Harbor or CARE-required item. Author should resolve before
  submission.
- `SHOULD`: identifiability is contextual. Author judgment required.

## Do NOT flag (false-positive guards)

Before emitting a finding, verify the match is not one of these:

- **Guideline / reference years**: `2020 IDSA guidelines`, `the 2013 CARE statement`,
  `Smith et al. 2019`. These are publications, not patient dates.
- **Already-relative time markers**: `day 1`, `day 4`, `hospital day 7`, `month X`,
  `post-operative day 3`, `3-day history`, `at 6-month follow-up`.
- **Durations**: `3-day history`, `2-week course`, `48 hours`.
- **Generic descriptors**: `our hospital`, `the ICU`, `the patient`.
- **Ages ≤89 in the patient**: not D2 (still possibly D7 if it's a relative).

Run this guard pass after the initial detection sweep and remove any candidate
that matches.

## Output format

Output is **Japanese prose with English replacement examples**. Use this
exact structure so downstream tooling can parse it:

```markdown
## deidentify-check report — <input filename>

検出サマリ: D1=<n>, D2=<n>, D3=<n>, D4=<n>, D5=<n>, D6=<n>推定, D7=<n>, D8=<n>, D9=<n>

### D1. 精密日付 (MUST) — <n>件
- L<line>: "<exact quoted text>" → 推奨: "<English replacement>"
- ...

### D2. 年齢 >89 (MUST) — <n>件
- ...

### D3. 地名 (MUST) — <n>件
- ...

### D4. 施設名 (MUST) — <n>件
- ...

### D5. ID / 記録番号 (MUST) — <n>件
- ...

### D6. 稀少属性の組合せ (SHOULD・推定) — <n>件
- L<line> 周辺: 組合せ = <attr1> + <attr2> + ... → 推奨: <which attribute to generalize>

### D7. 家族・関係者の識別情報 (MUST) — <n>件
- ...

### D8. インフォームドコンセント記載 (MUST)
- <検出あり / 検出なし>
- 検出なしの場合: 推奨テンプレ (上記 D8 セクション参照) を Acknowledgements 直前に追加

### D9. 図キャプションの識別特徴 (SHOULD) — <n>件
- ...

### 注意事項
- 本文は書き換えていない。著者が一件ずつ判断して反映すること。
- D6 と D9 は推定。最終判断は著者に委ねる。
```

If a category has zero findings, write `- 検出なし` under that heading rather
than omitting the heading entirely. This makes the report diffable across runs.

## Self-check before returning

1. Did you read the entire input file (not just the first 2000 lines)?
2. For each finding, is the line number correct? (Re-grep if unsure.)
3. Did you accidentally edit the input file? If yes, **revert immediately**.
4. Did you apply the false-positive guard list?
5. Is the output in the exact format above (so it remains diffable)?

## Testing this skill

A regression fixture lives at `skills/deidentify_check/tests/fixture_draft.md`,
with the expected findings in `tests/expected_findings.md`. To self-test:

1. Apply this skill to `tests/fixture_draft.md`.
2. Compare the report against `tests/expected_findings.md`.
3. Pass criteria:
   - All `MUST` items detected (FN = 0).
   - `SHOULD` items flagged at least once each.
   - No detection on `2020 IDSA guidelines` or `Day-1 (admission)`.
