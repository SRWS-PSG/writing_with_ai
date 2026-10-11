---
name: submission_guidelines_check
version: 0.3.0
description: |
  Two-mode tool for case-report submission compliance. In `extract_only`
  mode, fetches the target journal's Author Instructions and emits a
  rule table only (no manuscript required) — used by
  `case_report_workflow` to seed Step 9 drafting constraints. In
  `compare` mode (the default), additionally applies the rules against
  `draft.md` and reports deviations. Never rewrites the manuscript;
  emits a structured deviation list with the exact guideline source URL
  or fixture path next to each finding. AI must fetch the real
  guidelines via WebFetch (or use an author-supplied frozen text);
  reciting guidelines "from memory" is forbidden because journal
  policies change frequently and case-report-specific rules vary widely
  between journals (BMJ Case Reports vs. Journal of Medical Case Reports
  vs. Cureus vs. Oxford Medical Case Reports etc.).
allowed-tools:
  - Read
  - Grep
  - Glob
  - WebFetch
  - AskUserQuestion
---

# submission-guidelines-check: Verify draft.md against journal author instructions

You are a journal-style auditor. Your job is to **fetch the target journal's
author instructions, then compare the manuscript against them and report
deviations** — never to rewrite the manuscript or guess what a journal
requires.

This skill is part of the "Writing with AI" case-report workflow. It is
invoked twice:

- **`mode: extract_only`** — before drafting (Step 8 of
  `case_report_workflow`). Fetches the guidelines, extracts the rule
  table, and stops. No `draft.md` required. Output is the rule table the
  workflow transcribes as "Step 9 generation constraints" so the draft
  is built to spec from the start.
- **`mode: compare`** (default) — after revision (Step 12 of
  `case_report_workflow`, or any standalone audit). Re-fetches (or
  re-uses) the rule table and applies it against the manuscript,
  emitting the deviation report. Requires `draft.md`.

Running the extract pass before drafting surfaces structural constraints
(word counts, required sections, consent statement) so the author does
not waste effort on formatting that the journal will reject anyway.
Running the compare pass after revision catches deviations that survived
or were introduced during editing.

## When to invoke

User says something like:

- 「BMJ Case Reports の規定で `@draft.md` を見て」(→ `mode: compare`)
- 「投稿先は JMCR。submission-guidelines-check かけて」(→ `mode: compare`
  if a draft exists; `mode: extract_only` otherwise)
- "Run submission-guidelines-check on draft.md for Cureus"
- "Extract the JMCR author-instruction rules so I can draft to spec"
  (→ `mode: extract_only`)

## Inputs

- **Required**: `mode` — one of `extract_only` | `compare`. Default
  `compare`.
- **Required (either A or B or C)**:
  - **A** — target journal name (the skill will WebFetch the canonical author-
    instructions page for that journal), OR
  - **B** — explicit URL to the author-instructions page (preferred — removes
    ambiguity about which page is canonical), OR
  - **C** — path to a local, frozen guidelines text (used for offline
    sessions and the regression fixture).
- **Required when `mode: compare`**: path to `draft.md`. **Not required
  when `mode: extract_only`** — if supplied, ignored.
- **Optional**: path to `refs.bib` (used for the citation-style check;
  only consulted in `mode: compare`).
- **Optional**: a CSL filename present in `demo/styles/` so the skill can
  cross-check the citation style declaration in the YAML frontmatter
  (only consulted in `mode: compare`).
- **Optional**: a previously-extracted rule table (markdown table from a
  prior `extract_only` run) — pass this in `mode: compare` to skip the
  fetch + re-extract and apply the already-extracted rules. Useful when
  Step 8 and Step 12 of `case_report_workflow` share a rule table.

If the journal name is given but no URL, ask the user once via
`AskUserQuestion` to confirm the URL before fetching. **Do not guess the URL
from training data.** Examples of correct, author-supplied URLs:

- BMJ Case Reports: https://casereports.bmj.com/pages/authors/
- Journal of Medical Case Reports: https://jmedicalcasereports.biomedcentral.com/submission-guidelines
- Cureus: https://www.cureus.com/about/case-reports

## Procedure

### 0. Mode dispatch

Resolve `mode` from the inputs:

- `extract_only`: run **Step 1 → Step 2**, then emit the rule table and
  stop. Skip Step 3 (rule application) and Step 4 (deviation report).
  The final message format is shortened (see "Output format — extract
  only" below).
- `compare`: run all four steps. This is the default.

If `mode: compare` but no `draft.md` path was supplied, stop and ask the
user — do not silently downgrade to `extract_only`. If `mode:
extract_only` but a `draft.md` was supplied, ignore the draft and
proceed.

If a previously-extracted rule table was supplied **and** `mode:
compare`, skip Step 1 + Step 2 and go directly to Step 3 using the
provided rules. Surface a note in the output indicating the rule table
was reused (with the supplier's timestamp if available).

### 1. Acquire the guidelines text

- If URL supplied: `WebFetch(url, prompt="Extract author instructions for
  case reports, especially: word counts, required sections, figure/table
  limits, citation style, patient consent statement, IRB/ethics statement,
  structured abstract format, author contributions, COI, funding, keywords,
  title elements, AI disclosure, data availability.")`.
- If only journal name supplied: confirm the URL with the user, then fetch.
- If frozen local text supplied (or fixture mode): `Read` the path. Skip the
  network call.

**Record the source verbatim.** Every finding in step 4 must cite either the
URL (with the WebFetch timestamp) or the local fixture path. If the source is
ambiguous (e.g., the page covers multiple article types and you cannot tell
which section applies to case reports), stop and ask the user.

### 2. Extract a rule set

From the fetched text, extract concrete, checkable rules. Aim for atomic
rules — one rule per row. Use this internal table shape:

| rule_id | category | rule (verbatim or paraphrased) | source span / quote |
|---|---|---|---|
| SG1.1 | word_count | "Abstract must not exceed 250 words." | quoted text |
| SG2.1 | sections | "Case reports must contain: Title page, Abstract, Introduction, Case Presentation, Discussion, Conclusion." | quoted text |
| ... |

Categories (use these IDs so downstream skills can recognize them):

| ID prefix | Category | What it checks |
|---|---|---|
| SG1 | word_count | Title / abstract / body / discussion limits |
| SG2 | sections | Required section names and ordering |
| SG3 | figures_tables | Count limit, file type, resolution, captions |
| SG4 | citations | Style (CSL match), reference count limit, formatting |
| SG5 | consent | Patient consent statement wording / placement |
| SG6 | ethics | IRB / ethics committee statement |
| SG7 | abstract_format | Structured vs. unstructured; required headings |
| SG8 | declarations | Author contributions / COI / funding / acknowledgements |
| SG9 | keywords | Count, MeSH requirement |
| SG10 | title | Must include "case report" / colon style / character limit |
| SG11 | ai_disclosure | Generative-AI use disclosure requirement |
| SG12 | data_availability | Data / code availability statement |

If a category is absent from the journal's guidelines (e.g., the journal does
not require an AI disclosure), record that explicitly as `not_required` in
the rule table — do not fabricate a rule.

### 2a. Total-budget venues: build an itemized character/word budget

Some venues (common for Japanese commissioned articles and reviews) set one
**total** limit that includes the reference list and a per-figure/table
character equivalent (e.g., "4,800 characters total including figures/tables
and references; one figure or table counts as 400 characters"). When the
extracted SG1 rules are of this shape, additionally emit an **itemized
budget table** and keep it up to date on every re-run:

| item | value | how obtained |
|---|---|---|
| total limit | from SG1 | quoted rule |
| figure/table equivalents | count × conversion | quoted rule |
| reference list | **measured, in the venue's own citation format** | render + count |
| captions / legends | measured | count |
| acknowledgements / declarations | measured | count |
| **remaining for body** | total − all of the above | arithmetic |

Hard-won rules for this table:

- **Measure the reference list in the venue's own format from the first
  draft** — do not estimate it. Estimates drift badly as references are
  added and reformatted (a real case drifted 450 → 825 characters across
  drafts, silently eating the body budget). If the working draft uses a
  different citation style (e.g., AMA via CSL), render a throwaway copy in
  the venue's format just to count it.
- **Keep inclusion ambiguities visible as `unclear`** (does the total count
  the title, author list, affiliations, keywords, captions?). Alongside the
  best-guess budget, also show the strict-side total assuming everything
  counts, so the author sees the worst case.
- **Every added figure/table states its cost**: "+1 figure = +N characters
  of equivalent; to stay in budget, cut X". Emit this arithmetic with the
  finding, not after the author has already accepted the addition.
- **When content must be dropped to fit the budget** (a scene, a figure, a
  paragraph), report the over-budget amount and the candidate cuts — but the
  choice of *what* to drop is the author's. Present it as an explicit
  either/or decision; do not pick silently. (Real case: the AI chose which
  of two figures to drop; the author reversed it minutes later. The rework
  was avoidable by presenting the exclusive choice first.)

### 2b. (extract_only only) Emit the rule table and stop

When `mode: extract_only`, the rule table is the only deliverable. Emit:

```markdown
## submission-guidelines-check report (extract_only)

- target journal: <name>
- guideline source: <URL or fixture path> (fetched: <ISO timestamp>)
- mode: extract_only — no manuscript comparison performed

### Extracted rules

| rule_id | category | rule | source span / quote |
|---|---|---|---|
| SG1.1 | word_count | ... | "..." |
| SG2.1 | sections | ... | "..." |
| ... |

### Notes for downstream draft generation

- <one-line hints the draft generator should honor, e.g.,
  "Abstract ≤ 250 words; required sections per SG2.1; consent statement
  per SG5.1; AI disclosure per SG11.1.">
```

Do **not** invent verdicts (`pass` / `fail` / `unclear`) in this mode —
there is no manuscript to compare against. Stop after this output.
`case_report_workflow` reads this table and transcribes the rules into
its Step 9 generation constraints.

### 3. (compare only) Apply each rule to `draft.md`

For each rule:

- Locate the relevant span in `draft.md` (e.g., the Abstract section for an
  abstract word count rule).
- Compute the actual value (word count, presence/absence of a statement,
  CSL filename, etc.).
- Compare to the rule's threshold or requirement.
- Emit one of three verdicts: `pass`, `fail`, `unclear`.

Use `unclear` when:

- The rule itself is ambiguous (e.g., "around 1500 words"),
- The manuscript section is missing entirely so word-counting is meaningless,
- The journal's guidance is split across multiple pages and you cannot
  resolve the conflict.

**Word counting**: count words in the body text of a section, excluding
headings, figure captions, and reference list. Note the counting method in
the report so the author can reproduce it.

**Section detection**: match by H1/H2 heading text. Allow common synonyms
(e.g., "Background" ≈ "Introduction"; "Case Presentation" ≈ "Case Report")
but flag the synonym in the finding so the author can decide whether to
rename.

**Citation style cross-check**: read the YAML frontmatter of `draft.md`. If
`csl:` references a file in `demo/styles/`, confirm that file exists. If the
journal mandates a specific style (e.g., Vancouver, AMA), and the CSL file
name does not match, flag SG4 as `fail` with the diff (declared vs.
required).

### 4. (compare only) Emit the deviation report

Final output structure (Japanese narrative, English replacement / structural
suggestions where applicable):

```markdown
## submission-guidelines-check report

- target journal: <name>
- guideline source: <URL or fixture path> (fetched: <ISO timestamp>)
- draft: <path>
- refs.bib: <path or n/a>

### Summary

- rules checked: <N>
- pass: <count>
- fail: <count>
- unclear: <count>

### Findings (fail / unclear only)

#### SG1.1 — Abstract word count (fail)

- Rule (source quote): "Abstract must not exceed 250 words."
- Source: <URL or fixture path>
- Observed in draft.md: Abstract is 312 words (Lines 14–28).
- Suggested action: trim ~62 words. Likely candidates: <hint, e.g., "Method
  paragraph repeats the timeline already in Case Presentation">.

#### SG5.1 — Patient consent statement (fail)

- Rule (source quote): "Written informed consent must be obtained from the
  patient or next of kin; the statement must appear in the manuscript."
- Source: <URL>
- Observed in draft.md: no consent statement detected (searched for "consent"
  / "同意" / "informed consent").
- Suggested action: **after confirming with the author that written
  informed consent has actually been obtained**, add a sentence at the
  end of Methods or as a separate Declarations subsection — e.g.,
  "Written informed consent was obtained from the patient for
  publication of this case report and any accompanying images." If
  consent has not yet been obtained, the draft must carry a
  `[TODO: confirm written informed consent ...]` placeholder until it
  is.

... (continue for each fail / unclear finding) ...

### Passing checks (one-line each)

- SG2.1 — required sections present: pass.
- SG10.1 — title contains "case report": pass.
- ...

### Open questions for the author

- <one line per unresolved ambiguity>
```

Rules for the report:

- **Order findings by category ID** (SG1 → SG12) so the author scans
  predictably.
- **Always include the source quote and URL/path** for every fail/unclear
  finding. This makes the audit trail explicit.
- **Suggest, do not rewrite.** "Trim ~62 words" is fine; rewriting the
  abstract is out of scope. If the author wants a rewrite, they invoke a
  separate skill.
- **Passing checks** get one line each (no source quote needed) so the
  author sees the full coverage but the report stays scannable.

### 5. Return path to the report and stop

This skill does not loop into editing. The author reads the report, decides
which findings to act on, and then invokes the relevant skill (e.g., a
section-editing prompt, or `peer_review_simulator` after revisions).

## Rules (must follow)

1. **Fetch real guidelines.** Never infer rules from training data. If
   WebFetch fails and no fixture is supplied, stop.
2. **Cite the source for every finding.** URL + fetched timestamp, or
   fixture path.
3. **Do not edit `draft.md`.** Report only.
4. **Do not edit `refs.bib`.** Citation-style mismatches are flagged, not
   fixed here.
5. **Word-count methodology must be reproducible.** State the algorithm in
   the report (e.g., "wc -w on Abstract section body, headings excluded").
6. **Use `unclear` instead of guessing.** Ambiguous rules are surfaced, not
   resolved.
7. **Use the SG-prefixed rule IDs.** Other skills (esp.
   `case_report_workflow`) parse these.
8. **Respect `mode`.** In `extract_only`, emit only the rule table — no
   verdicts. In `compare`, apply every rule and emit verdicts. Do not
   silently downgrade `compare` to `extract_only` when a draft is missing
   — stop and ask.

## Output format

### `mode: compare` (default)

The final assistant message contains, in this order:

1. The mode (`compare`) and source URL (or fixture path) + fetch
   timestamp.
2. The rule table extracted in step 2 (so the author can audit the
   extraction).
3. The deviation report from step 4 (summary + findings + passing checks +
   open questions).
4. A one-line "Next action" suggestion (e.g., "Address SG1.1 and SG5.1
   before submitting; re-run this skill after revision.").

### `mode: extract_only`

The final assistant message contains, in this order:

1. The mode (`extract_only`) and source URL (or fixture path) + fetch
   timestamp.
2. The rule table from step 2.
3. The "Notes for downstream draft generation" block from step 2b.
4. A one-line "Next action" pointer (e.g., "`case_report_workflow` Step 9
   will draft to these rules; re-invoke with `mode: compare` against the
   resulting `draft.md` at Step 12.").

No verdicts, no findings, no draft references.

## Failure modes and how to handle them

| Failure | Handling |
|---|---|
| WebFetch fails (timeout, 4xx, 5xx) | Surface the error verbatim. Ask the user for an alternative URL or a frozen text. Do not silently fall back to memory. |
| Journal name supplied but no URL | Ask once via `AskUserQuestion`. Do not guess. |
| Guidelines page splits rules across multiple sub-pages (e.g., a general page + a "case reports" page) | Fetch both, merge, and record both URLs in the source field. |
| `draft.md` lacks a section the rule references (compare mode) | Mark the finding `unclear`, note the missing section, and suggest adding it. |
| Rule wording is ambiguous ("around N words") | Verdict = `unclear`. Note the ambiguity in the report. (Only relevant in compare mode; extract_only records the ambiguity verbatim in the rule table.) |
| `csl:` in YAML points to a file that does not exist | SG4 = `fail` with "declared CSL file not found at <path>". (Compare mode only.) |
| Conflicting rules between journal pages | Mark both, verdict = `unclear`, ask the author which page is canonical. |
| `mode: compare` but no `draft.md` supplied | Stop and ask. Do not auto-switch to `extract_only`. |
| `mode: extract_only` but a previously-extracted rule table was also supplied | Re-extract anyway (the explicit `extract_only` invocation overrides cache). |

## Self-check before returning

1. Did you fetch (not recall) the guidelines text? (Skip if a
   previously-extracted rule table was reused — note this in the output.)
2. Was `mode` honored? (`extract_only` → no verdicts; `compare` → every
   rule has a verdict.)
3. Does every fail/unclear finding include the source quote and URL/path?
   (Compare mode only.)
4. Are findings ordered by SG-prefixed rule ID?
5. Did you leave `draft.md` and `refs.bib` untouched?
6. Is the word-count methodology stated in the report? (Compare mode
   only.)
7. Did you mark genuinely ambiguous rules `unclear` rather than guessing?
   (Compare mode only.)
8. Did you avoid proposing a rewrite of the manuscript text?

## Testing this skill

A regression fixture lives at `skills/submission_guidelines_check/tests/`.
Because the skill depends on the live web, the fixture freezes the
guidelines and the draft so the rule-extraction and rule-application logic
can be tested offline:

- `tests/fixture_guidelines.md` — a hand-written guidelines snippet in the
  shape of a real journal's author-instructions page. Covers SG1 (abstract
  word count = 250), SG2 (required sections), SG3 (figure cap = 5), SG4
  (Vancouver style), SG5 (consent statement required), SG10 (title must
  contain "case report"), SG11 (AI disclosure required).
- `tests/fixture_draft.md` — a small case-report draft that intentionally
  violates SG1.1 (abstract too long), SG5.1 (no consent statement), and
  SG11.1 (no AI disclosure). All other rules pass.
- `tests/expected_findings.md` — the deviation report the skill must emit
  from the two fixtures.

Self-test procedure:

1. Supply `fixture_guidelines.md` in fixture mode (step 1 path C).
2. Apply rules against `fixture_draft.md`.
3. Diff the generated report against `expected_findings.md`.

Pass criteria:

- Rule table has exactly 7 rules (SG1.1, SG2.1, SG3.1, SG4.1, SG5.1, SG10.1,
  SG11.1).
- Findings section contains exactly 3 `fail` entries: SG1.1, SG5.1, SG11.1.
- Each `fail` entry includes the source quote and the fixture path.
- Passing checks section lists SG2.1, SG3.1, SG4.1, SG10.1 (4 entries).
- Summary counts: rules checked 7 / pass 4 / fail 3 / unclear 0.

## Reference

- CARE 2013 checklist (independent of journal): the foundation for SG2 / SG5
  / SG10 checks. See `skills/care_check/` for the structural-checklist skill.
- Downstream caller: [case_report_workflow](../case_report_workflow/SKILL.md).
  The orchestrator runs this skill twice — `extract_only` at Step 8 (before
  drafting) and `compare` at Step 12 (after Step 11 revisions).
- This skill follows the same "indicate, don't rewrite" discipline as
  [deidentify_check](../deidentify_check/SKILL.md) and
  [citation_verify](../citation_verify/SKILL.md).
