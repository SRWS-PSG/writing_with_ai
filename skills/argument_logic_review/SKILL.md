---
name: argument_logic_review
version: 0.1.0
description: |
  Evaluate and improve the ARGUMENT STRUCTURE of a piece of prose after it is
  written — not its science, not its sentence-level style. Identifies the
  document's single core thesis, maps each paragraph's internal logic
  (topic sentence, claim→evidence→significance arc, intra-paragraph order,
  one-idea-per-paragraph), and checks cross-paragraph progression (does each
  paragraph advance the argument or merely restate it?), paragraph ordering,
  and genre-template fit (letter P1/P2/P3, IMRaD, abstract). Classifies defects
  with a reusable logic taxonomy (L1–L10) and severity, then emits (A) a
  Japanese diagnosis report and (B) a NEW restructured file
  `<source>.logic.md` that reorders / merges / splits paragraphs and fixes
  topic sentences WITHOUT touching prose style or inventing content. Read-only
  on the source; never overwrites it. General-purpose: works on letters,
  manuscripts, abstracts, discussion sections, grant text, any argued prose.
  Triggers: 「ロジックを評価して」「段落構成をチェック」「論理展開を見て」
  「文章の論理を改善」「パラグラフライティングの評価」「argument structure review」.
  NOT for prose style (em-dash, word count, banned terms → proofread-manuscript),
  NOT for AI-style removal (→ humanizer_academic), NOT for scientific validity
  / fairness / spin (→ peer_review_simulator / letter_review_simulator).
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - AskUserQuestion
---

# argument-logic-review: paragraph-level logic audit and structural rewrite

You audit the **argument structure** of a written piece and then repair that
structure. You judge how the argument is *organized*, not whether it is
*true*, *fair*, or *stylish*. Three sibling concerns are explicitly out of
scope and belong to other skills:

- **Prose style** (em-dash, sentence length, banned terms, active voice) →
  `proofread-manuscript`.
- **AI-style fingerprints** (AI vocabulary, hedging tics, synonym cycling) →
  `humanizer_academic`.
- **Scientific validity / fairness / spin** → `peer_review_simulator`
  (case reports) or `letter_review_simulator` (letters to the editor).

This skill is **general-purpose**. It runs on any argued prose: a letter to
the editor, a Discussion section, an abstract, a grant aims page, a cover
letter. It does not assume a medical topic.

## When to invoke

User says something like:

- 「このレター/原稿のロジックを評価して、各段落の論理展開を見て」
- 「パラグラフライティングがちゃんとできているかチェックして」
- 「主張が反復していないか、段落の順番が論理的か見て直して」
- "Review the argument structure / paragraph logic of this draft and fix it."
- Optionally called by `letter_to_editor` or `case_report_workflow` right
  after a draft is generated, before the style and content reviews.

Do **not** invoke to fix wording style (→ `proofread-manuscript`), to strip
AI tics (→ `humanizer_academic`), or to judge whether a claim is scientifically
or ethically sound (→ the review simulators).

## Inputs

- **Required**: path to the source file (`.md` or `.txt`), or pasted prose. If
  pasted without a path, produce only report (A); say you cannot write
  `<source>.logic.md` without a file path and offer to write to a path the
  user names.
- **Optional**: the intended genre / template (letter, IMRaD section, abstract,
  free prose). If absent, infer it in Step 4 and label the inference.
- **Optional**: the intended *single* take-home point, if the author can state
  it. Having it sharpens Step 1; if absent, you infer it and ask the author to
  confirm.

## The logic-defect taxonomy (L1–L10)

Classify every finding with one code. This is the analogue of the spin
taxonomy in `letter_review_simulator`; use it for a repeatable, teachable
vocabulary.

**Whole-document / thesis**
- **L1 buried or inverted thesis** — the core claim is hidden mid-document, or
  the piece is point-last where point-first would serve the reader (or vice
  versa).
- **L2 diluted single point** — one idea is stretched across multiple
  paragraphs and restated rather than developed; the document says the same
  thing N times. (The most common defect; weight it heavily.)

**Within a paragraph**
- **L3 weak or missing topic sentence** — the first sentence does not announce
  what the paragraph will establish.
- **L4 intra-paragraph order inversion** — conclusion stated before its setup,
  or a setup clause (e.g., how an instrument was constructed) interrupts the
  argument it should precede.
- **L5 multi-idea paragraph** — two or more distinct points share one
  paragraph; it should split.

**Across paragraphs**
- **L6 missing connective / non-sequitur** — adjacent claims lack the logical
  bridge; the reader must assemble the causal thread unaided.
- **L7 paragraph-ordering error** — a paragraph precedes the one that
  justifies it (e.g., a recommendation before its rationale).
- **L8 redundant paragraph** — a paragraph adds no new information or so-what;
  it is a smaller copy of an earlier one (common in closings).
- **L9 unsupported leap** — a claim appears without the bridging evidence or
  reasoning the argument needs.

**Genre**
- **L10 template mismatch** — the piece violates its genre's expected shape
  (a letter not built as P1 praise → P2/P3 critique; an abstract missing a
  conclusion; IMRaD with results in the discussion).

Severity: **Major** = the reader cannot follow or believe the argument as
ordered (typically L1, L2, L7, L9, L10). **Minor** = local friction the reader
overcomes (typically L3, L4, L6, L8); L5 is Major if it hides a buried second
thesis, else Minor.

## Procedure

### Step 1 — Identify the single core thesis

State, in one sentence, the document's central claim. Then count how many
paragraphs are needed to make it versus how many exist. If one idea spans many
paragraphs, that is an **L2** finding and frames the whole review. If you
cannot find a single thesis, the document may have an L1 (buried) or a genuine
multi-thesis structure — say which.

### Step 2 — Per-paragraph logic map

For each paragraph, record a compact line:

- **Topic sentence**: present & accurate / weak / missing (L3).
- **Internal arc**: name the arc it uses or should use — e.g.
  `claim → evidence → significance`, `observation → interpretation →
  implication`, `problem → proposal → payoff` — and whether the sentences
  actually follow it. Flag inversions (L4) and interrupting clauses.
- **Idea count**: one (good) / multiple (L5).
- **Role**: what job this paragraph does in the whole (praise / limitation /
  proposal / evidence / closing). Name it so Step 3 can check ordering.

### Step 3 — Cross-paragraph progression

- Does each paragraph **advance** the argument, or restate a prior one? Mark
  restatements (L2 / L8).
- Is the **paragraph order** logical — does every claim arrive after its
  support, every proposal after its rationale? Flag L7 with the suggested move.
- Are the **connectives** between paragraphs explicit, or must the reader infer
  the thread? Flag L6 / L9.

### Step 4 — Genre-template fit

If a template applies, check it:

- **Letter to the editor**: P1 concrete praise → P2/P3 two *distinct*
  critiques → constructive close. (Matches `letter_to_editor`.)
- **Abstract**: background → objective → methods → results → single conclusion.
- **IMRaD section**: each section holds only its own move.
- **Free prose**: no template; judge by Steps 1–3 only.

Flag deviations as L10. A deviation that the source's own state header
documents is acceptable; note it and move on.

### Step 5 — Classify and prioritize

Build a findings table: each row = location + taxonomy code + severity +
one-line description + the fix. Order Major before Minor.

### Step 6 — Improve: produce the restructured draft

Write a **new file** `<source>.logic.md` (never overwrite the source) that
repairs *structure only*:

- Reorder sentences within a paragraph to fix L4.
- Reorder, merge, or split paragraphs to fix L2 / L5 / L7 / L8.
- Add or rewrite topic sentences to fix L3 (minimal new words, author's voice).
- Add the missing connective to fix L6 / L9 (a bridging clause, not new
  evidence).

Every change you make must be marked with a trailing `[bracketed note]` stating
which taxonomy code it addresses, e.g. `[L7: moved the proposal to P3]`. You
may **reuse and relocate the author's existing sentences** and add minimal
connective words; you may **not** invent new content, data, or citations, and
you must **not** restyle surviving sentences (that is `proofread-manuscript`).
If a paragraph should be cut as redundant (L8), do not delete it silently —
move it to a `> [L8: candidate for cut — restated P2]` block so the author
decides.

## Output format

The final assistant message must contain, in this order:

1. A header block: `source: <path>` / `genre: <given or inferred>` /
   `core thesis: <one sentence>` / `thesis spread: stated in N paras, occupies
   M paras`.
2. **Step 2 paragraph map** (one line per paragraph).
3. **Findings table** (Step 5): `| Loc | Code | Severity | Issue | Fix |`.
4. A 2–4 sentence **diagnosis in Japanese** naming the dominant defect and the
   recommended restructure at a high level.
5. The path to the written `<source>.logic.md` (or, if no path was given, the
   restructured draft inline with a note that no file was written).
6. A one-line "Recommended next" pointer (e.g., "Run `proofread-manuscript` on
   the restructured draft for prose style; then `letter_review_simulator` for
   fairness.").

Explanatory prose in the report is in **Japanese** (per repo convention); the
restructured draft stays in the source language.

## Rules (must follow)

1. **Read-only on the source; write only `<source>.logic.md`.** Never call Edit
   on the source and never overwrite it.
2. **Structure only — never style.** Do not change em-dash usage, sentence
   length, word choice, or voice of surviving sentences. That is
   `proofread-manuscript`. Mention style only when it changes the logic (e.g.,
   a dropped hedge that flips a claim).
3. **Never invent content or citations.** You reorder, merge, split, and add
   connective words from the author's own material. New evidence or references
   are out of scope; if the argument needs them, *say so* and point to
   `similar_cases_search`.
4. **Do not judge truth, fairness, or spin.** A logically clean paragraph can
   still be scientifically wrong; that is the review simulators' job. Stay on
   organization.
5. **Every edit is annotated.** Each structural change in `<source>.logic.md`
   carries a `[L#: ...]` note. No silent rewrites; no silent deletions (use the
   `> [L8: candidate for cut]` block).
6. **One taxonomy code per finding**; pick the dominant one if several apply,
   and note the secondary in the Issue text.
7. **Genre deviations documented in the source are acceptable** — note, do not
   penalize.

## Failure modes and how to handle them

| Failure | Handling |
|---|---|
| Pasted prose with no file path | Produce report (A) only; offer to write `<source>.logic.md` to a path the user names. Do not write to an arbitrary path. |
| User wants wording/style fixed | Redirect to `proofread-manuscript`; do the structure pass here, then hand off. |
| User wants the science/fairness judged | Redirect to `peer_review_simulator` / `letter_review_simulator`. |
| The draft genuinely has multiple legitimate theses (e.g., a review article) | Do not force L2; map each thesis's paragraphs separately and check ordering within each. |
| The argument needs evidence the author has not supplied (L9) | Flag the leap; do NOT fabricate the bridge. Suggest `similar_cases_search` if a citation would fill it. |
| Single-paragraph input | Run Steps 1–2 and 6 only (no cross-paragraph step); still produce `.logic.md` if order within the paragraph is fixable. |

## Self-check before returning

1. Did you leave the source file untouched and write only `<source>.logic.md`?
2. Did you state the single core thesis and its paragraph spread (Step 1)?
3. Does every finding carry exactly one L-code and a severity?
4. Does every change in the restructured draft carry a `[L#: ...]` note, and
   is every cut surfaced as a `> [L8: candidate for cut]` block rather than
   deleted?
5. Did you avoid all sentence-level style edits to surviving sentences?
6. Did you avoid judging truth / fairness / spin, and avoid inventing content?
7. Is the diagnosis in Japanese and the restructured draft in the source
   language?

## Testing this skill

A regression fixture lives at `skills/argument_logic_review/tests/`:

- `tests/fixture.md` — a synthetic four-paragraph letter (different theme from
  any real case) that intentionally carries the canonical defects: **L2** (one
  point — "test transfer on a new task" — diluted across P2/P3/P4), **L4** (P2
  states its recommendation before the rationale and lets a construction-detail
  clause interrupt the core argument), **L7** (the proposal sits in P2 ahead of
  its justification), and **L8** (P4 restates P1–P3 with no new so-what).
- `tests/expected_report.md` — the report this skill must emit: the core thesis
  in one sentence, a four-line paragraph map, a findings table containing at
  least L2/L4/L7/L8, and a note that `fixture.logic.md` would be written.

Self-test procedure:

1. Run Steps 1–6 against `fixture.md`.
2. Compare the generated report against `expected_report.md`.

Pass criteria:

- Step 1 names a single core thesis and flags the spread as L2.
- The findings table contains L2 (Major), L7 (Major), L4 (Minor), L8 (Minor),
  each citing a paragraph.
- The proposed restructure collapses P2–P4's one idea and moves the proposal
  after its rationale, annotated with `[L7: ...]` and `[L2: ...]` notes.
- No finding judges the science or restyles a sentence.

## Reference

- Adjacent skills (boundaries):
  - [proofread-manuscript](../proofread-manuscript/SKILL.md) — sentence-level
    prose style; run it **after** this structural pass.
  - [humanizer_academic](../humanizer_academic/SKILL.md) — removes AI-style
    fingerprints; orthogonal to logic.
  - [letter_review_simulator](../letter_review_simulator/SKILL.md) /
    [peer_review_simulator](../peer_review_simulator/SKILL.md) — fairness,
    spin, and scientific soundness; this skill stays on organization.
  - [letter_to_editor](../letter_to_editor/SKILL.md) /
    [case_report_workflow](../case_report_workflow/SKILL.md) — orchestrators
    that may call this skill right after drafting.
- This skill follows the same "indicate every change, never invent content"
  discipline as `letter_review_simulator` and `citation_verify`, and the same
  "Japanese feedback + a new `*.<tag>.md` file" output shape as
  `proofread-manuscript`.
