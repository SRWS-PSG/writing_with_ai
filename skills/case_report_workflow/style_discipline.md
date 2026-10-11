# Style discipline for English case-report drafts

This file is the single source of truth for English prose style in
`case_report_workflow`. Step 9 (drafting) reads this file before
generating `draft.md` and applies the rules below. Step 10 (review)
invokes `proofread-manuscript` as a verification pass against the same
rules. Step 11 (revision) auto-applies style fixes that do not touch
clinical facts.

The rules below apply to **English** drafts only. They do not apply to
Japanese drafts.

---

## R1. Em-dash (—) is forbidden in prose

Em-dash overuse is a common AI-drafting artefact. Replace every em-dash
in prose with one of:

| Original construct | Replacement |
|---|---|
| `A — explanatory phrase — B` (parenthetical) | `A, explanatory phrase, B` or `A (explanatory phrase) B` |
| `A — B` (re-statement / clarification) | `A. B.` (split into two sentences) |
| `A — B and C — D` (multi-clause aside) | Split into 2–3 sentences |
| `X — Y` (list separator) | `X, Y` or `X: Y` |

Bibliographic entries: in the References list, prefer `Author. Year. Journal.`
over `Author — Year — Journal`.

Self-check before emitting: `grep -c '—' draft.md` must be `0`.

## R2. One sentence, one idea (≤ 25 words by default)

Long subordinated sentences are the second most common AI-drafting
artefact. Apply these heuristics while drafting:

- One main clause per sentence. If you reach for "and", "but",
  "although", "while", or "because" mid-sentence, consider whether the
  second clause deserves its own sentence.
- Hard cap: 25 words. Sentences over 25 words must be defensible (e.g.,
  a quoted passage, a list of lab values with units that does not split
  cleanly, or a single complex idea that genuinely cannot be split).
- Hard ceiling: 40 words. No sentence in prose may exceed 40 words,
  with no exception for AI-generated text.

Acceptable long sentences (do not force-split):

- Direct quotations (patient or family).
- Lab-value lists with units, e.g., "Day 0 venous blood tests showed
  Hb 9.8 g/dL, WBC 9 610/μL with 93 % neutrophils, platelet
  270 × 10³/μL, and CRP 12.4 mg/dL." (One factual list.)
- Citations of consensus statements where the quoted passage itself is
  long.

Self-check: long-sentence ratio = (count of > 25-word sentences) /
(total sentences). Target ≤ 15 %.

## R3. Active voice for actions; passive OK for measurements

| Sentence type | Preferred voice | Example |
|---|---|---|
| Action taken by the clinical team | **Active** | "We administered lactated Ringer's 500 mL/day." |
| Decision made by the patient/family | **Active** | "The family declined hospitalisation." |
| Measurement / observation / lab result | Passive acceptable | "The Hb was 9.8 g/dL." |
| Diagnostic reasoning | Active preferred | "We diagnosed aspiration pneumonia clinically." |

Avoid impersonal passive constructions like "It was decided" or "It
was found" — name the actor.

## R4. Topic sentence first

The first sentence of every paragraph states the paragraph's claim.
Subsequent sentences supply evidence, qualification, or context. Do not
bury the main point in the middle of a paragraph.

Apply this to:

- Introduction paragraphs (each paragraph = one idea, topic sentence
  first).
- Discussion paragraphs (claim, then evidence + citations).
- Limitations (one limitation per paragraph if there are ≥ 3; topic
  sentence names the limitation).

## R5. Banned terms

These terms are banned in case-report prose. Replace as below.

| Banned | Why | Replacement |
|---|---|---|
| `significant`, `significantly` | Without a statistic, meaningless | Quote the effect or omit |
| `however,` at sentence start | Stilted | `In contrast,` or restructure |
| `demonstrated` | Overused | `found`, `showed`, `observed` |
| `borderline significance` | No GRADE basis | Drop or rewrite quantitatively |
| `caused`, `led to`, `contributed to`, `impacted`, `resulted in`, `affected` (observational designs, including case reports) | Implies causality | `was associated with` |
| `clearly`, `obviously` | Empty intensifier | Drop, or give the specific evidence |
| `it is important to note that` | Filler | Drop |
| Bare disease name as subject (e.g., `aspiration pneumonia presented with`) | Person-first language | `the patient with aspiration pneumonia presented with` |

## R6. Numbers and units

- Quote numerical clinical facts verbatim from `clinical_facts.md`. Do
  not paraphrase (e.g., never "around 40 %" when the ledger says
  "38.1 °C").
- Units: SI where possible. Keep the units the source used (mg/dL,
  mEq/L, U/L) rather than converting silently.
- Day numbering: `Day 0`, `Day N`, never calendar dates (`2023-10-10`).

## R7. Quotations

- Translate Japanese quotations into English. Mark with
  `[translated from Japanese]`.
- Do not paraphrase a quotation silently; if a long quotation must be
  shortened, mark the cut with `[…]`.
- Quotation length is not subject to R2 (one-sentence rule).

## R8. References / citations

- Use `@pmid<PMID>` keys in prose; do not invent any key.
- In the References list, use `Author. Year. Journal.` format (no
  em-dash separator).
- Cite the source for every claim that is not a direct case observation
  or a generic statement of fact.

---

## Self-check before returning a draft

Before emitting `draft.md` at Step 9 (or after Step 11 revision):

1. `grep -c '—' draft.md` → must be `0`.
2. Sentence-length check: `> 25-word` sentences / total ≤ 15 %.
3. No sentence > 40 words in prose (excluding quotations and lab-value
   lists).
4. Banned-term grep: each of `significant`, `demonstrated`, `caused`,
   `led to`, `contributed to`, `clearly`, `obviously`, `however,`
   (sentence start) → must be `0` (or justified in context).
5. Active voice used for every "we did X" / "the team did Y" /
   "the family chose Z" sentence.
6. Topic sentence first in every paragraph.

If any check fails, fix the violations before declaring the step
complete. If a violation is genuinely unavoidable (e.g., a long
quoted passage), note it in the workflow state block.

---

## Why this file exists

This style discipline is layer 1 of a 3-layer system:

- **Layer 1** (this file): canonical rules.
- **Layer 2** (`case_report_workflow` Step 9): the drafter reads this
  file and applies the rules while writing.
- **Layer 3** (`case_report_workflow` Step 10): the reviewer invokes
  `proofread-manuscript`, which verifies the same rules and produces a
  punch-list. Step 11 auto-applies the resulting style edits because
  they do not touch clinical facts.

When updating these rules, update this file and let the other layers
inherit. Do not duplicate the rules in Step 9 or Step 10 procedure
text.

Adjacent (not a layer of this system):
[`humanizer_academic`](../humanizer_academic/SKILL.md) removes
AI-writing tells from existing text on request. It is invoked
standalone, outside the orchestrators. Where its patterns overlap with
the rules here (e.g., the em-dash ban), this file is the source of
truth.
