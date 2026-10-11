---
name: citation_verify
version: 0.2.0
description: |
  Verify every BibTeX entry in `refs.bib` against Crossref / PubMed using
  citeguard (citation-checker) and surface a structured report. Never modifies
  `refs.bib` or `draft.md`: it only emits the report and a human-readable
  summary. Designed to be called by `similar_cases_search` immediately after
  appending new candidates, and again by `case_report_workflow` after the
  author finishes manuscript revisions. Categories surfaced: `found`,
  `likely_wrong`, `not_found`, `retraction`. Scope limit: this is
  bibliographic verification only — it does NOT check whether each cited
  source actually supports the claim made in the manuscript. Pair it with a
  claim-support pass before submission (see "Scope limit" section).
allowed-tools:
  - Read
  - Grep
  - Bash
  - AskUserQuestion
---

# citation-verify: Cross-check refs.bib against Crossref / PubMed

You are a citation-verification gatekeeper. Your only job is to **run citeguard
on `refs.bib` and report what it found**. You do not edit `refs.bib`, you do
not edit `draft.md`, and you do not fabricate replacement metadata.

This skill is the formerly-embedded step 6 of `similar_cases_search`, extracted
so it can be called independently by other skills (the orchestrator
`case_report_workflow` calls it twice: once after similar_cases_search adds
candidates, and once after manuscript revisions).

## When to invoke

User says something like:

- 「`refs.bib` を citation-verify で見て」
- 「投稿前に引用が間違ってないかチェックして」
- "Verify refs.bib against Crossref / PubMed"
- Called programmatically at the end of `similar_cases_search` or by
  `case_report_workflow`.

## Inputs

- **Required**: path to `refs.bib`. Default: the `refs.bib` adjacent to the
  manuscript being worked on (`projects/<name>/refs.bib`); `demo/refs.bib`
  is for workshop practice only. If the path is ambiguous, ask the caller.
  If the file does not exist, stop and tell the user.
- **Required**: NCBI E-utilities contact email. If unknown, ask once via
  `AskUserQuestion` and reuse for the session.
- **Optional**: list of specific citation keys to verify (default: all
  entries). Use when the caller only wants to re-check the entries it just
  appended.
- **Optional**: output report path (default: `citation_report.md` in the same
  directory as the input `refs.bib` — platform-neutral; do not default to
  `/tmp`, which does not exist on Windows).

## Dependency

`citeguard` (citation-checker) must be installed on the user's machine:

```bash
pip install citeguard
```

If `citeguard --version` fails, ask the user once whether to install it. Do
not run the install command without confirmation.

Upstream: https://github.com/SRWS-PSG/citation-checker

## Procedure

### 1. Pre-flight checks

- Confirm `refs.bib` exists at the given path. If not, stop.
- Confirm `citeguard` is on PATH. If not, surface the install command and stop
  until the user confirms.
- Confirm the email argument is present. NCBI E-utilities terms of use require
  it; refuse to run without one.

### 2. Run citeguard

```bash
citeguard --input-file <refs.bib path> --out <report path> --all --email "<email>"
```

- `--all` runs all checks (metadata match, retraction lookup, DOI resolve).
- `--out` writes the structured report to the path above.

If the caller passed specific citation keys, filter the report after the run
(citeguard verifies the whole file; we narrow the *surfaced* findings to the
requested keys, but the report on disk stays complete for auditability).

If citeguard exits non-zero, capture stderr and surface it. Do not silently
treat a tool failure as "no issues".

### 3. Parse and categorize

Read the report. For each entry, assign one of four categories:

| Category | Meaning | Source field in citeguard report |
|---|---|---|
| `found` | Title / author / year match Crossref or PubMed within tolerance | `status: found` |
| `likely_wrong` | A candidate exists but title/author/year diverge enough that the author should review the diff | `status: likely_wrong` (or `verdict: mismatch`) |
| `not_found` | No candidate located. Probable causes: typo'd DOI, withdrawn record, hand-typed entry | `status: not_found` |
| `retraction` | The publication is retracted (PubMed PublicationType `Retracted Publication` or `Retraction of Publication`) | `retraction: true` |

A single entry can be both `found` and `retraction`; surface it under
`retraction` (the retraction status is the more urgent signal).

### 4. Surface the summary to the caller

Emit a summary block in this exact shape so downstream skills can parse it:

```markdown
## citation-verify summary

- refs.bib: <path>
- report: <report path>
- entries checked: <N>
- found: <count>
- likely_wrong: <count>
- not_found: <count>
- retraction: <count>

### likely_wrong (if any)

| citation key | refs.bib title | candidate title | candidate DOI |
|---|---|---|---|
| `@pmid12345678` | ... | ... | 10.xxxx/yyyy |

### not_found (if any)

| citation key | refs.bib DOI / PMID | likely cause |
|---|---|---|

### retraction (if any)

| citation key | refs.bib title | retraction notice |
|---|---|---|
```

Rules for the summary:

- Always emit the counts line, even when all counts are zero.
- Omit the per-category tables when their count is zero (do not print an empty
  table).
- Quote citation keys with backticks (`@pmidXXXX`) so downstream skills can
  grep them.
- Cap each table at 20 rows; if more, list the first 20 and tell the user the
  total count plus the report path for the full list.

### 5. Recommend next steps (do not act)

After the summary, append a short "Recommended action" block:

- For `likely_wrong`: "Open `<report path>` to compare diffs. If the
  candidate is correct, re-run `similar_cases_search` for that PMID, or hand-
  edit `refs.bib`."
- For `not_found`: "Verify the DOI / PMID by hand. If the entry was hand-
  typed, consider re-fetching via `similar_cases_search`."
- For `retraction`: "Decide whether to drop the citation or cite-as-retracted
  per the target journal's policy."
- Always, before submission: "Run the claim-support pass (see 'Scope limit'
  below) — a clean bibliographic report does not mean each source supports
  the sentence citing it."

**Never propose edits to `refs.bib` from this skill.** The author or another
skill makes that change.

## Scope limit: bibliographic existence ≠ claim support

A citation can pass every citeguard check (correct authors, title, journal,
year, DOI, not retracted) and still fail the reader: the cited source may not
support the specific claim the manuscript attaches to it. Real near-miss:
a correctly-cited news feature was used to support a country-level claim,
but the supporting data appeared only in a figure inside the article, and
the article's own country ranking pointed the other way. citeguard cannot
catch this — it never reads the source's content against the manuscript.

Therefore, before submission, run one **claim-support pass** separately:

1. List every in-text citation together with the exact sentence it supports.
2. For each pair, open the source (abstract at minimum; full text when the
   claim is specific) and locate the passage, table, or figure that supports
   the sentence.
3. Mark each pair `supported` / `partially supported (rephrase)` /
   `not supported (replace or delete)`. A claim resting on a figure or a
   subgroup rather than the source's main finding should be rephrased to
   match what the source actually shows.
4. Surface the list to the author; the author decides rephrasings.

Do not treat a clean citeguard report as "citations are fine" — it only
means "citations exist and are not retracted".

## Rules (must follow)

1. **Read-only on `refs.bib` and `draft.md`.** This skill does not call Edit
   or Write on either file.
2. **Surface citeguard's verdict, do not override it.** If citeguard says
   `likely_wrong`, report `likely_wrong` even if you would personally judge
   the diff as cosmetic.
3. **Refuse to run without an email.** NCBI E-utilities require it.
4. **Counts are always reported**, even when all zeros — downstream skills
   rely on the counts line existing.
5. **Path discipline**: the report file path is part of the output. Callers
   may read it to surface details inline.

## Output format

The final assistant message must contain, in this order:

1. The citeguard command actually executed (so the run is reproducible).
2. The summary block from step 4 (counts + per-category tables).
3. The "Recommended action" block from step 5.
4. The absolute path to the full report.

## Failure modes and how to handle them

| Failure | Handling |
|---|---|
| `citeguard` not installed | Surface install command. Do not run `pip install` without user confirmation. |
| `refs.bib` not found at given path | Stop. Ask the caller to confirm the path. |
| `citeguard` exits non-zero | Surface stderr. Do not pretend the run succeeded. |
| Email missing | Ask via `AskUserQuestion`. Do not call citeguard without it. |
| Network failure mid-run | Retry once. If still failing, report the partial result and the network error verbatim. |
| Report contains unknown `status:` value | Treat as `likely_wrong` (conservative) and note "unrecognized status: <value>" in the summary. |

## Self-check before returning

1. Did you run citeguard with `--all` and `--email`?
2. Did you read the report file before summarizing?
3. Are the counts line present even when all zeros?
4. Did you leave `refs.bib` and `draft.md` untouched? (`git status` should
   show no modification to those files attributable to this skill.)
5. Did you include the full report path in the final message?

## Testing this skill

A regression fixture lives at `skills/citation_verify/tests/`:

- `fixture_refs.bib` — three-entry refs.bib (one `found`, one `likely_wrong`,
  one `not_found`).
- `fixture_citeguard_report.md` — a frozen citeguard report representing what
  the tool would emit for `fixture_refs.bib`. Used so the parsing /
  summarization logic can be tested offline (citeguard itself hits the
  network).
- `expected_summary.md` — the exact summary block this skill must emit from
  the frozen report.

Self-test procedure:

1. Treat `fixture_citeguard_report.md` as if citeguard had just written it
   (skip the actual `citeguard` invocation).
2. Run the parsing / categorization / formatting logic on it.
3. Diff the output against `expected_summary.md`.

Pass criteria:

- Exactly three entries categorized: 1 `found`, 1 `likely_wrong`, 1
  `not_found`, 0 `retraction`.
- Counts line is present and matches.
- Both per-category tables (`likely_wrong`, `not_found`) are present.
- `found`-only and `retraction` tables are **absent** (count was zero).
- Citation keys appear with backtick quoting (`@pmidXXXX`).

## Reference

- citation-checker (citeguard) repo: https://github.com/SRWS-PSG/citation-checker
- Upstream callers:
  - `skills/similar_cases_search/SKILL.md` — step 6 delegates to this skill.
  - `skills/case_report_workflow/SKILL.md` (planned) — calls this skill
    twice: after similar_cases_search appends candidates, and again after
    manuscript revisions.
- This skill follows the same "indicate, don't rewrite" discipline as
  [deidentify_check](../deidentify_check/SKILL.md).
