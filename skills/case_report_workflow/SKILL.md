---
name: case_report_workflow
version: 0.2.0
description: |
  End-to-end orchestrator for writing a medical case report. Calls each
  case-report sub-skill in a fixed sequence, gates progress on author
  confirmation at every step, writes `draft.md` only in the drafting and
  revision steps, and produces a single hand-off package at the end. The
  orchestrator never invents citations, never invents clinical facts
  beyond the author-confirmed clinical-fact ledger, never edits `draft.md`
  outside the two designated steps, and never silently skips verification —
  failed verifications are surfaced and require explicit author override.
  Currently optimized for `single_case`; `surgical_case` and `case_series`
  are only partially supported (see "Article-type scope").
  Triggers: 「症例報告ワークフロー」「case-report-workflow」「症例報告を最初から書く」.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
---

# case-report-workflow: End-to-end case-report drafting orchestrator

You are the conductor for the entire case-report drafting pipeline. Your job
is to **call sub-skills in order, surface their outputs back to the author,
and gate progress on explicit author confirmation** at every step. You do not
duplicate the sub-skills' logic — when a sub-skill exists for a task, you
invoke it; you do not re-implement it.

This skill is the only place where the full sequence lives. Sub-skills can be
called independently for one-off tasks (e.g., the author just wants a CARE
audit on an existing draft → invoke `care_check` directly); the orchestrator
is for the case where the author wants to write a case report start to
finish with AI assistance.

## Article-type scope

This workflow is **optimized for `single_case`**. For other article types,
behavior degrades — surface the scope warning in the workflow state and do
not let the author submit without manual gap-filling:

- `surgical_case` — SCARE 2020 would be the appropriate checklist, but this
  workflow only runs `care_check`. `peer_review_simulator` flags
  SCARE-framework gaps; treat those flags as **required** punch-list items
  (no auto-dismiss).
- `case_series` — single-case frameworks (CARE 2013, JBI single-case) only
  partially fit; STROBE or a dedicated case-series framework would be more
  appropriate. `peer_review_simulator` flags this; same handling.
- `image_case`, `diagnostic_challenge` — most sub-skills work, but
  `care_check` items become largely "N/A". The workflow still completes;
  the author verifies framework-fit manually.

When article type ≠ `single_case`, prepend a one-line scope warning to
every reply during the workflow ("⚠ scope: <type> — single_case-only
features may underfit; see Article-type scope") so the author cannot miss it.

## When to invoke

User says something like:

- 「これから症例報告を書きたい。最初から最後まで案内して」
- 「case-report-workflow を起動して」
- "Start a case-report workflow for this case"
- The CLAUDE.md project hint points to this skill as the entry point for
  case-report work.

If the author only wants a single sub-skill task (e.g., "just check CARE"),
invoke that sub-skill directly. **Do not run the full orchestrator for a
single-step request.**

## Inputs

- **Required at start**: either a case summary (free text) or an existing
  `@draft.md` path.
- **Required eventually** (collected via `AskUserQuestion` as needed):
  - NCBI E-utilities contact email (for `similar_cases_search`,
    `background_literature_search` mode, and `citation_verify`).
  - Target journal name + author-instructions URL (for
    `submission_guidelines_check`).
  - Article type (for `peer_review_simulator`): one of `single_case`,
    `surgical_case`, `case_series`, `image_case`, `diagnostic_challenge`.
- **Optional**: existing `refs.bib` path (default:
  `projects/<name>/refs.bib`, alongside the manuscript; `demo/refs.bib`
  only for workshop practice sessions — never append real-case citations
  to it).

Collect inputs lazily — ask only when the step that needs them is reached.
Do not block the workflow at step 1 collecting every input upfront.

## State tracking

Maintain a workflow state block in your responses so the author can see
where they are. Emit it as the **first block** of every reply during the
workflow:

```markdown
### case-report-workflow state

| step | name | status | artifact |
|---|---|---|---|
| 1 | input collected | pending / done | <case summary or draft path> |
| 2 | clinical fact ledger | pending / done | <ledger path or "skipped (existing draft)"> |
| 3 | deidentify_check | pending / done / skipped | <findings inline> |
| 4 | similar_cases_search | pending / done / skipped | <refs.bib path + N entries added> |
| 5 | background_literature_search | pending / done / skipped | <refs.bib path + N entries added> |
| 6 | citation_verify (initial) | pending / done / skipped | <counts: found/likely_wrong/not_found/retraction> |
| 7 | bottom_line_message | pending / done / skipped | <BLM finalized? yes/no> |
| 8 | submission_guidelines_check (extract) | pending / done / skipped | <rule count + constraint block written> |
| 9 | draft generated | pending / done / skipped | <draft.md path; TODO count> |
| 10 | peer_review_simulator + care_check + proofread-manuscript | pending / done / skipped | <Major comment count, CARE missing items, em-dash + long-sentence counts> |
| 11 | revision applied | pending / done / skipped | <revision diff summary> |
| 12 | submission_guidelines_check (compare) | pending / done / skipped | <fail/unclear count after revision> |
| 13 | citation_verify (final) | pending / done / skipped | <counts> |
| 14 | hand-off | pending / done | <hand-off package path> |
```

Update the state block after every step transition. Mark steps `skipped`
(not `done`) when the author explicitly chose to skip — this preserves the
audit trail.

## Procedure

### Step 1 — Input collected

- Confirm whether the author has a case summary, a draft, or both.
- If only a case summary: tell the author Step 9 will create `draft.md`
  later; for now, file the summary as a workflow note.
- If only a draft: read it and surface a 5-line synopsis (presentation /
  course / outcome / claimed lesson / open questions) so both parties are
  on the same page about what's being reported.
- If neither: stop and ask which input the author wants to provide.

Transition to Step 2 only after the author confirms the synopsis is
accurate (or the case summary captures the case as intended).

### Step 2 — Clinical fact ledger

Build a ledger of **author-confirmed clinical facts**. This is the single
source of truth for clinical content during draft generation (Step 9). The
ledger prevents AI from filling unprovided facts (lab values, doses,
timelines, outcomes, comorbidities, etc.).

Workflow:

1. Extract every concrete clinical fact mentioned by the author in Step 1
   into a table with these columns:
   - `field` — what kind of fact (e.g., "age", "BAL eosinophil %", "day of
     symptom onset relative to drug start", "prednisolone dose").
   - `value` — exactly as the author stated it (do not paraphrase
     numerically).
   - `source` — where it came from ("Step 1 summary", "Step 1 Q&A turn
     N", "existing draft, Case Presentation paragraph 2").
2. List the fields the author did **not** provide as a separate
   "unprovided fields" block. Typical empty-but-expected fields for a
   case report:
   - patient sex, age band
   - relevant comorbidities and current medications
   - vital signs at presentation
   - key labs with units and reference ranges
   - imaging findings
   - microbiology / pathology results
   - intervention name + dose + duration
   - timeline anchors (Day 0, Day N events)
   - follow-up duration and final outcome
   - patient perspective / quality of life
3. Ask the author whether to fill in any unprovided fields now. Anything
   left empty after this confirmation becomes a `[TODO: author to confirm
   <field>]` placeholder in Step 9.

If a pre-existing `draft.md` was provided in Step 1, mark Step 2 as
`done (ledger extracted from existing draft)` — extract the ledger by
reading the draft instead of asking the author, and ask the author to
confirm the extraction is faithful before proceeding. Any fact in the
draft that the author cannot confirm becomes a Step 11 punch-list item
("verify or remove").

Write the ledger to `<draft_dir>/clinical_facts.md` (alongside the
eventual `draft.md`). The ledger is consulted by Step 9 (drafting) and
Step 11 (revision); it is never used as a source of fact for the final
manuscript by itself — the author still owns every claim.

### Step 3 — Deidentify check

Invoke `deidentify_check`. Surface its findings table inline. **Do not
auto-edit the draft.** The author decides which findings to act on; this
orchestrator only ensures the audit happens.

If the deidentify_check report contains D-prefixed findings (D1–D9), pause
and ask whether the author wants to address them before Step 4 (recommended
when running on existing draft) or defer (acceptable for a case summary
that hasn't been turned into a draft yet — Step 9 will incorporate
de-identification guidance into the generated draft).

If the author skips Step 3, surface the skip explicitly in the workflow
state and tell them they should re-run before submission. Do not let the
workflow finish without at least one deidentify_check pass.

### Step 4 — Similar cases search

Confirm or collect the NCBI email. Invoke `similar_cases_search` in its
default mode (`search_mode: similar_cases`) with the case features
extracted from Step 1 / Step 2 ledger. Surface its candidates table and
let the author choose which PMIDs to keep. Approved entries are appended
to `refs.bib` by `similar_cases_search` itself (not by this orchestrator).

If the author skips Step 4 (e.g., they already have `refs.bib` finalized
from prior literature work), still proceed to Step 6 — the verification
step is non-negotiable.

### Step 5 — Background literature search (optional but recommended)

Re-invoke `similar_cases_search` with `search_mode: background_literature`
to find review articles, guidelines, and original studies that support
the case's background context (typical presentation, epidemiology,
diagnostic criteria, treatment standards). These are the citations
`bottom_line_message` will use as "anchors" against which the case's
findings deviate.

Use this step when:

- The case's claimed novelty rests on a deviation from a typical
  presentation (anchor needed in `refs.bib`).
- The discussion will compare the case against guideline-recommended
  management.
- Step 4 yielded < 3 directly-similar cases (broaden into background).

Skip when the author has already curated background references manually
(record skip with reason).

Approved entries are appended to the **same** `refs.bib` as Step 4. Citation
keys remain `pmid<PMID>` so `citation_verify` and `bottom_line_message`
treat them uniformly.

### Step 6 — Citation verify (initial pass)

Invoke `citation_verify` against `refs.bib` (covering both Step 4 and
Step 5 additions). Transcribe its summary into the workflow state. If
`likely_wrong` / `not_found` / `retraction` counts are non-zero, **pause**
and ask the author to resolve before Step 7. Do not let the workflow
advance with unverified citations except by explicit author override
(which is recorded in the state).

### Step 7 — Bottom-line message

Invoke `bottom_line_message`. This skill runs a four-phase dialogue with
the author; the orchestrator's job is to hand control to it and resume
when the dialogue concludes. The deliverable is the "2 findings + bottom
line message candidates + PMID-to-finding map".

Do not auto-paste the BLM into `draft.md` yet — the author confirms the
final BLM wording, and it lands in the draft during Step 9 (or Step 11
if a draft already existed).

### Step 8 — Submission guidelines check (extract-only)

Confirm or collect the target journal name + author-instructions URL.
Invoke `submission_guidelines_check` with `mode: extract_only` — this
extracts the rule table from the author instructions but does **not**
compare against `draft.md` (which usually does not exist yet at this
point).

Transcribe the extracted rules into a "Step 9 generation constraints"
block so the draft generator (Step 9) honors them from the start:
abstract word limit, required sections, consent statement placement,
title format, AI disclosure, citation style, etc.

If a draft already exists (workflow entered with `@draft.md`), still run
`extract_only` here — the compare pass happens in Step 12 after Step 11
revisions, where the comparison is meaningful.

If the target journal is undecided, skip Step 8 with explicit author
confirmation. Use CARE 2013 ordering as the default in Step 9. The
workflow can still complete, but the state row records the skip; warn
the author that Step 12 will be skipped too.

### Step 9 — Draft generated

This is the **first** step where the orchestrator writes to `draft.md`.

- If a draft already exists, **skip generation** and proceed to Step 10.
  This orchestrator does not rewrite an existing draft from scratch.
- If no draft exists, generate one in Markdown using:
  - the clinical fact ledger from Step 2,
  - the BLM and findings from Step 7,
  - the journal constraints from Step 8,
  - the `refs.bib` entries from Steps 4–5 (cite by `@pmid<PMID>`).

Drafting rules:

- **Clinical-fact discipline**: every concrete clinical fact in the draft
  (lab value, dose, time interval, vital sign, outcome statement,
  comorbidity, demographic) must trace back to an entry in the Step 2
  ledger. If a fact is needed by the narrative but not in the ledger,
  insert `[TODO: author to confirm <field>]` instead of inventing a
  value. Do not paraphrase numerically (e.g., "around 40%" when the
  ledger says "42%").
- **Style discipline** (English drafts only): before writing, read
  [`style_discipline.md`](style_discipline.md). The canonical rules are
  (a) no em-dash in prose, (b) ≤ 25 words per sentence by default with a
  hard ceiling of 40 words, (c) active voice for clinical-team actions
  and family decisions (passive acceptable for measurements / lab
  values), (d) topic sentence first in every paragraph, (e) banned
  terms (`significant`, `demonstrated`, `caused / led to / contributed
  to / impacted / resulted in / affected` in observational contexts,
  `clearly`, `obviously`, `however,` at sentence start), and (f)
  References list uses `Author. Year. Journal.` format (no em-dash
  separator). The full table of replacements lives in the style file —
  consult it, do not paraphrase from memory.
- Use the structure mandated by Step 8's SG2 rule (or CARE 2013 ordering
  if no journal-specific rule was extracted).
- Cite only `@pmid<PMID>` keys that exist in `refs.bib`. Grep `refs.bib`
  before each citation; if a key is absent, do not invent it. Instead
  insert a `[TODO: similar_cases_search for <topic>]` placeholder.
- Use English for body text (workshop default; ask the author if Japanese
  is wanted). The style discipline above applies to English only.
- Keep the draft at the journal's word limits.
- If SG5 required a consent statement, add a "Patient Consent" subsection
  with the **TODO placeholder**, not a hard-coded sentence:
  `[TODO: confirm written informed consent for publication and any accompanying images, replace with the author-confirmed wording]`
  Do **not** write "Written informed consent was obtained ..." as a
  filler. That would be a false statement until the author confirms.
- Add an "AI Disclosure" subsection if SG11 required it (placeholder
  text describing the AI tools actually used in the workflow; the author
  edits before submission).

Write the file via `Write` (new file) only. If `draft.md` already exists,
refuse to overwrite (the workflow would have skipped to Step 10).

At the end of Step 9, run the **style self-check** from
[`style_discipline.md`](style_discipline.md):

1. `grep -c '—' draft.md` must return `0`.
2. Long-sentence ratio (sentences > 25 words / total sentences) ≤ 15 %.
3. No prose sentence > 40 words (quotations and lab-value lists
   excluded).
4. Banned-term grep returns `0` for each of `significant`,
   `demonstrated`, `caused`, `led to`, `contributed to`, `clearly`,
   `obviously`, `^[Hh]owever,`.

If any check fails, fix the violations before emitting the draft.

At the end of Step 9, also count `[TODO: ...]` placeholders in the draft
and surface both counts (TODO + style-self-check results) in the state
block. Anything > 0 on TODOs is a flag for Step 11 revision (and a hard
blocker at Step 14). Anything > 0 on the style self-check must be
resolved before emitting the draft.

### Step 10 — Peer review + CARE + Proofread

Invoke `peer_review_simulator`, `care_check`, and `proofread-manuscript`
in parallel (all three read the same `draft.md` and produce independent
reports). Confirm the article type for `peer_review_simulator`
(single_case / surgical_case / etc.) before invoking.

The three skills cover non-overlapping concerns by design:

- `peer_review_simulator` — clinical plausibility, novelty, ethics,
  discussion-literature review (non-CARE).
- `care_check` — CARE 2013 structural completeness (C1–C13).
- `proofread-manuscript` — English prose style: em-dash, sentence
  length, active voice, banned terms (the rules from
  [`style_discipline.md`](style_discipline.md)). Pass the file as
  English; skip this invocation if the draft is in Japanese.
  **Fallback**: this is a user-level skill not shipped with the
  repository. If it is not available in the session, do **not** stop —
  run the [`style_discipline.md`](style_discipline.md) self-check
  (grep-based) yourself and use its findings as the Style punch-list
  items. Record `proofread-manuscript: unavailable — style_discipline
  self-check used` in the workflow state.

If the confirmed article type is not `single_case`, ensure the
"Article-type scope" warning is in the workflow state and **treat every
SCARE / case-series framework flag from `peer_review_simulator` as a
Major punch-list item that cannot be auto-dismissed** (the author can
still dismiss with explicit one-line reason, but the default disposition
is "accept").

Aggregate the three reports into a single revision punch-list:

- CARE-shaped items (missing checklist elements) → from `care_check`.
- Reviewer-shaped items (Major / Minor / Confidential) → from
  `peer_review_simulator`.
- Article-type framework gaps (SCARE for surgical_case, STROBE / case-
  series framework for case_series) → from `peer_review_simulator`,
  surfaced as Major.
- Style items (em-dash, > 25-word sentences, banned terms, passive
  voice for clinical-team actions) → from `proofread-manuscript`,
  surfaced as **Style** (default disposition: `auto-apply` in Step 11
  because they do not touch clinical facts; the author may opt-out per
  item).

De-duplicate where they overlap (e.g., both `care_check` and
`peer_review_simulator` may flag a missing consent statement — keep one
entry, attribute to both skills).

Surface the merged punch-list and ask the author which items to accept
for the Step 11 revision. The author may dismiss items they disagree
with — record dismissals in the workflow state with a one-line reason.
Style items default to accept and need no per-item confirmation unless
the author explicitly opts out of a specific edit.

### Step 11 — Revision applied

This is the **second** step where the orchestrator writes to `draft.md`.

For each accepted punch-list item, apply the smallest targeted edit that
resolves the item, typically `Edit` calls scoped to a single paragraph
or section. Rules:

- One edit per item (preserves traceability).
- Re-read the affected section after each edit before moving to the
  next.
- Do not re-write paragraphs the author did not request changes to.
- **Honor the clinical-fact ledger.** Any new clinical content that the
  revision requires must come from the ledger; if not present, insert a
  `[TODO: author to confirm <field>]` placeholder instead of inventing
  it. The same rule that gated Step 9 still applies here.
- Cite only keys already in `refs.bib`. If a Major comment requested a
  new citation, re-invoke `similar_cases_search` (which loops to Step 6
  to verify) before adding the citation.
- If `peer_review_simulator` flagged causality overstatement, the
  rewording must remove the overstated claim **without** asking AI to
  generate new clinical content beyond the literature already in
  `refs.bib`.
- **Style items from `proofread-manuscript` are auto-applied** (em-dash
  replacement, sentence splitting, active-voice conversion, banned-term
  replacement). These edits do not touch numerical clinical facts,
  drug names, dates, or day numbering, so the ledger-discipline
  invariant is preserved. Verify by running the
  [`style_discipline.md`](style_discipline.md) self-check after the
  edits: em-dash count `0`, long-sentence ratio ≤ 15 %, no banned-term
  hits.

When revision is complete, surface a diff summary (touched sections,
sentence-count change per section, em-dash count, long-sentence ratio
before / after) in the workflow state.

### Step 12 — Submission guidelines check (compare against revised draft)

Re-invoke `submission_guidelines_check` with `mode: compare`, using the
rule table extracted in Step 8 and the revised `draft.md` from Step 11.
Transcribe its findings into the workflow state.

If `fail` count is non-zero, the workflow **must not** proceed to
Step 14. Loop back to Step 11 with the new findings as additional
punch-list items, then re-run Step 12.

If the target journal was undecided in Step 8, mark Step 12 as `skipped
(no journal target)`. Warn the author that journal-specific compliance
is unverified.

### Step 13 — Citation verify (final pass)

Re-invoke `citation_verify` on the updated `refs.bib`. Confirm:

- All `@pmid<PMID>` keys cited in `draft.md` exist in `refs.bib`.
- `citation_verify` returns zero `likely_wrong` / `not_found` /
  `retraction` for the currently-cited keys (the report may still cover
  unused entries — focus the surface on cited keys).

If any failures, loop back to Step 11 for that specific entry. Do not
proceed to Step 14 with broken citations.

### Step 14 — Hand-off

Produce a hand-off package as a single Markdown summary the author can
paste into a project log or share with co-authors. Contents:

- Final `draft.md` path + word counts per section.
- Final `refs.bib` path + entry count + citation_verify counts.
- BLM (the chosen candidate from Step 7).
- Journal target + the SG findings that were resolved (Step 12 pass) and
  any that remain `unclear`.
- Reviewer punch-list with each item marked `addressed` / `dismissed`
  (with reason).
- AI disclosure draft text (mirroring SG11 if required).
- A short "next actions" list for the author (e.g., "[Co-author review](#co-author-review-round-after-hand-off)",
  "Consent form attached separately", "Submit via journal portal").

Before writing the hand-off, run these blockers:

- `[TODO: ...]` count in `draft.md` must be **zero** (consent
  placeholder, fact placeholders, similar_cases_search placeholders all
  resolved). If any remain, list them and refuse to write `handoff.md`.
- The article-type scope warning, if present, is repeated verbatim in
  the hand-off so the author cannot lose it.

Write the hand-off package to `<draft_dir>/handoff.md`. Tell the author
the workflow is complete.

## Co-author review round (after hand-off)

Enter this branch **only when the author reports that co-authors commented
on the shared Google Doc after hand-off**. It is not a normal numbered step.

The first upload of the hand-off draft uses
[`render_and_upload`](../render_and_upload/SKILL.md), which records v1 in
`projects/<name>/versions/versions.md` and saves `versions/draft.v1.md`.
Without that snapshot, this branch cannot run; stop and tell the author
(see Failure modes for the author-agreed baseline candidate).

1. Run [`tracked_revision`](../tracked_revision/SKILL.md) Step 1: fetch the
   reviewed Doc into `projects/<name>/review/vN/`, run
   `parse_docx_changes.py`, and run `check_direct_edits.py` against the v1
   snapshot for round 1. For later rounds, follow its "Round 2 以降"
   procedure, including the manual direct-edit check and fresh comment IDs.
2. Run `tracked_revision` Step 2 to build `review/vN/response_table.md`.
   Surface the response table and obtain author confirmation before revision.
3. Re-enter **Step 11**, using the table's `修正` / `一部修正` rows, every
   accepted co-author suggestion (tracked change in `review/vN/report.md`,
   confirmed with the author item by item), and every adopted direct edit
   from `check_direct_edits.py` findings as the punch-list. This replaces `tracked_revision` Step 3; the branch writes
   `draft.md` only through Step 11, with all its rules still in force.
   Record rejected suggestions as ID-less table rows with reasons per
   `tracked_revision` Step 2; the clinical-fact ledger rules below also
   apply to accepted suggestions.
   Add new clinical facts from co-authors to the Step 2 ledger only with
   author confirmation; otherwise use `[TODO: author to confirm ...]`.
   Cite only keys in `refs.bib`; new literature goes through
   `similar_cases_search` and its loop to Step 6 before citation.
   Run the style self-check and surface the revision diff summary.
4. Before any upload, re-run Step 12 (SG compare; keep it skipped if it
   was skipped), Step 13 (citation verify, final), and `deidentify_check`
   on the revised draft because co-author edits can add identifiers.
   Require zero `[TODO: ...]`, as at Step 14. On verification failure,
   loop back to Step 11 and repeat verification; do not upload.
5. Run `tracked_revision` Steps 4–6: `make_tracked_md.py` + pandoc for
   tracked docx with original comments and replies, verification, then
   upload v{N+1} as a **new Doc** using its Step 0 hash-name and ledger
   procedure. Update `handoff.md` with the round number, new Doc URL,
   and response table path; retain the article-type scope warning.

Keep the main 14-row state block unchanged. Emit and update this separate
round block alongside it (record skips and any agreed baseline here):

```markdown
### co-author round N
| stage | status | artifact |
|---|---|---|
| fetch + direct-edit check (tracked_revision 1) | pending / done | <review/vN path; direct edits found?> |
| response table (tracked_revision 2) | pending / done | <path; rows by 対応> |
| revision (Step 11) | pending / done | <diff summary> |
| verification (Step 12, 13, deidentify_check) | pending / done / skipped | <counts; Step 12 skip reason if applicable> |
| tracked v{N+1} upload (tracked_revision 4–6) | pending / done | <Doc URL; ledger row> |
```

## Rules (must follow)

1. **Sub-skills do the work.** This orchestrator does not re-implement
   citation verification, CARE audits, etc.
2. **`draft.md` writes only at Step 9 and Step 11.** Every other step is
   read-only on the manuscript.
3. **No citation invention.** All citations come through
   `similar_cases_search` (both modes) and are verified by
   `citation_verify`. Any `@article` block written outside that path is
   a workflow failure.
4. **No clinical-fact invention.** Every concrete clinical claim in the
   draft must trace to the Step 2 clinical-fact ledger. Unprovided
   facts become `[TODO: author to confirm ...]` placeholders, not
   AI-imagined values.
5. **No false-positive consent statements.** Step 9 must not output the
   sentence "Written informed consent was obtained ..." as a filler.
   Use the TODO placeholder until the author confirms.
6. **Pause on verification failure.** Step 6, Step 12, and Step 13 pause
   if their respective checks fail. Override requires explicit author
   action, recorded in state.
7. **At least one `deidentify_check` pass** must occur before Step 14.
   Step 3 may be skipped at the start, but the orchestrator must loop
   back before hand-off if it was skipped.
8. **State block is the first artifact of every reply.** The author
   uses it to navigate; do not bury it.
9. **CARE audit lives in `care_check`, not here.** Step 10 invokes it;
   do not embed CARE logic in this orchestrator.
10. **Style discipline lives in [`style_discipline.md`](style_discipline.md).**
    Step 9 reads it, Step 10 verifies via `proofread-manuscript`, Step
    11 auto-applies the punch-list. Do not duplicate the style rules in
    procedure text; update the canonical file and let the layers
    inherit.
11. **Skips are explicit and recorded.** `skipped` ≠ `done` in the state
    block.
12. **Article-type scope warning is mandatory** when article type ≠
    `single_case`, at the top of every reply, and re-stated in the
    hand-off.
13. **Hand-off requires zero `[TODO: ...]` in `draft.md`.** Step 14
    refuses otherwise.
14. **Shared Google Doc co-author comments use only the co-author review
    round branch.** Revise only by re-entering Step 11. Never overwrite
    the existing Doc; follow the `tracked_revision` ledger procedure.

## Output format

The final assistant message (at workflow completion) must contain, in
this order:

1. The final state block (all rows `done` or `skipped`).
2. The hand-off package contents (from Step 14).
3. The hand-off package path (`handoff.md`).
4. A one-line confirmation: "Case-report workflow complete. Review
   `handoff.md` and the final `draft.md` before submission."

For intermediate messages during the workflow, surface:

1. The updated state block.
2. The current step's sub-skill output (transcribed in full or by
   reference to a longer artifact file).
3. An `AskUserQuestion` for the next gate (proceed / revise / skip).

## Failure modes and how to handle them

| Failure | Handling |
|---|---|
| Co-author comments returned but `versions/draft.v1.md` is missing (v1 uploaded without the ledger) | Stop and tell the author. `tracked_revision` has no automated fallback. `pandoc <reviewed>.docx --track-changes=reject -t markdown` yields only a baseline candidate: citation keys return as rendered numbers, so every citation shows as a change. Use it only with explicit author agreement and record that in the round state. |
| `check_direct_edits.py` exits 2 | Show the detected paragraphs to the author. Record adopt / not adopt decisions as ID-less response-table rows before Step 11. |
| A verification step fails after co-author revision | Loop back to Step 11 with the findings, then repeat verification. Do not upload. |
| Sub-skill not available (file missing, etc.) | Surface which skill is missing. Stop. Do not silently bypass. (Exception: `proofread-manuscript` — see next row.) |
| `proofread-manuscript` unavailable (user-level skill, not shipped with this repo) | Do not stop. Run the `style_discipline.md` self-check instead and use its findings as the Style punch-list. Record the fallback in the workflow state. |
| `citation_verify` returns non-zero failures and the author overrides | Record the override in state with the author's one-line justification; require it again at Step 13. |
| Author wants to skip Step 3 (deidentify) at the start | Allowed at start. The orchestrator loops back to run it before Step 14. If still skipped at Step 14, the workflow does **not** complete — issue a hard stop. |
| Author already has a complete `draft.md` at workflow start | Skip Step 9. Steps 10–14 run normally. State row 9 = `skipped (draft pre-existed)`. Step 2 still runs, extracting the ledger from the draft for Step 11 traceability. |
| Step 10 reveals article type is `case_series` or `surgical_case` after the workflow started as `single_case` | Re-run `peer_review_simulator` with the corrected type. Surface the change in state. Add the article-type scope warning retroactively to all subsequent replies. |
| Conflicts between `care_check` and `peer_review_simulator` (one says present, the other says missing) | Trust the more specific one based on Grep evidence in the report. If neither has line evidence, ask the author. |
| The journal-target answer is "undecided" at Step 8 | Skip SG checks (Steps 8 and 12) with explicit author confirmation. Use CARE 2013 ordering as the default in Step 9. The workflow can still complete, but the state rows record the skips. |
| Step 12 returns non-zero `fail` count | Loop back to Step 11 with the new findings as punch-list items. Do not advance to Step 13 until Step 12 returns clean (or unresolved findings have explicit author override recorded). |
| Step 9 inserted ≥ 1 `[TODO: ...]` placeholder and the author wants to skip resolving them before hand-off | Refuse. Step 14 will hard-stop on outstanding TODOs; resolve them in Step 11 first. |
| Author wants to ship without `background_literature_search` (Step 5) | Allowed. Record skip with reason. The downstream impact (weaker anchors for `bottom_line_message`) is surfaced in the Step 7 dialogue automatically. |

## Self-check before returning at hand-off

1. Are all 14 state rows `done` or `skipped` (no `pending` remaining)?
2. Was `deidentify_check` run at least once?
3. Was `citation_verify` run at the end (Step 13), and did it return
   clean for cited keys?
4. Did `draft.md` get written only at Step 9 and Step 11?
5. Are all `@pmid<PMID>` citations in `draft.md` present in `refs.bib`
   (Grep confirms)?
6. Does the hand-off package list each reviewer punch-list item as
   `addressed` or `dismissed` (no `pending`)?
7. Is the hand-off written to `<draft_dir>/handoff.md`?
8. Are there **zero** `[TODO: ...]` placeholders remaining in `draft.md`?
9. Did Step 12 (SG compare) return clean, or was it explicitly skipped
   because no journal target was set?
10. (English drafts only) Does `draft.md` pass the
    [`style_discipline.md`](style_discipline.md) self-check, i.e.,
    `grep -c '—'` returns `0`, long-sentence ratio ≤ 15 %, no banned
    terms?
11. If article type ≠ `single_case`, is the scope warning present in
    both the state block and the hand-off package?

## Testing this skill

A regression fixture lives at `skills/case_report_workflow/tests/`:

- `tests/fixture_session_log.md` — a hand-crafted "session transcript"
  showing each step's sub-skill output as if the sub-skills had been
  invoked in sequence. Stands in for live sub-skill invocations during
  offline testing.
- `tests/expected_state_block.md` — the final state block after all
  steps complete.
- `tests/expected_handoff.md` — the expected hand-off package contents.

Self-test procedure:

1. Treat `fixture_session_log.md` as the substrate (skip live sub-skill
   invocations).
2. Run the aggregation / state-tracking / hand-off-package-generation
   logic on it.
3. Diff:
   - Generated final state block against `expected_state_block.md`.
   - Generated hand-off package against `expected_handoff.md`.

Pass criteria:

- All 14 state rows are `done` or `skipped` (none `pending`).
- Hand-off lists every reviewer punch-list item as `addressed` or
  `dismissed` (none `pending`).
- The hand-off package is written to `handoff.md` adjacent to
  `draft.md`.
- The package's `@pmid<PMID>` citations all resolve to entries in the
  fixture's `refs.bib`.
- No `[TODO: ...]` placeholders remain in the fixture's final draft
  state.

## Sub-skills called

In invocation order:

1. [deidentify_check](../deidentify_check/SKILL.md) — Step 3
2. [similar_cases_search](../similar_cases_search/SKILL.md), default mode — Step 4
3. [similar_cases_search](../similar_cases_search/SKILL.md), `background_literature` mode — Step 5
4. [citation_verify](../citation_verify/SKILL.md) — Step 6
5. [bottom_line_message](../bottom_line_message/SKILL.md) — Step 7
6. [submission_guidelines_check](../submission_guidelines_check/SKILL.md), `extract_only` mode — Step 8
7. (Step 9 = draft generation, no sub-skill)
8. [peer_review_simulator](../peer_review_simulator/SKILL.md) +
   [care_check](../care_check/SKILL.md) +
   `proofread-manuscript` (parallel) — Step 10. `proofread-manuscript`
   is a user-level skill (lives in `~/.claude/skills/proofread-manuscript/`,
   not in this repo); invoke via the `Skill` tool. Skip it for
   Japanese-language drafts. If it is not installed, fall back to the
   `style_discipline.md` self-check (see Step 10).
9. (Step 11 = revision, no sub-skill; may re-invoke
   `similar_cases_search` if Major comments require new literature.
   Auto-applies `proofread-manuscript`'s style punch-list per
   [`style_discipline.md`](style_discipline.md).)
10. [submission_guidelines_check](../submission_guidelines_check/SKILL.md), `compare` mode — Step 12
11. [citation_verify](../citation_verify/SKILL.md) (re-invoked) — Step 13
12. [case_timeline](../case_timeline/SKILL.md) — optional, on author
    request during Step 9 or Step 11 for figure generation.
13. [tracked_revision](../tracked_revision/SKILL.md): co-author review round only.

## Reference

- This orchestrator follows the "Markdown is the source of truth, AI does
  partial revisions" discipline from the workshop README. It does not
  introduce new editorial discipline beyond what the sub-skills already
  enforce; it sequences them.
- Adjacent: [humanizer_academic](../humanizer_academic/SKILL.md) for
  voice/tone adjustments, [render_and_upload](../render_and_upload/SKILL.md)
  for the first Markdown → Google Docs export after Step 14, recording v1
  in the ledger with its Markdown snapshot.
