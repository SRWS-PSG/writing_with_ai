---
name: similar_cases_search
version: 0.2.0
description: |
  Search PubMed for literature supporting a case report and emit grounded
  BibTeX entries the author can paste into refs.bib. Two search modes:
  (a) `similar_cases` (default) — finds prior case reports of the same
  presentation/diagnosis; (b) `background_literature` — finds reviews,
  guidelines, and original studies that establish typical
  presentation / epidemiology / diagnostic criteria / treatment
  standards (anchors against which the case's findings deviate). The
  skill never invents citation metadata: every field in the output
  BibTeX is sourced from the PubMed efetch XML for an explicit PMID.
  After candidates are appended, this skill delegates verification to
  the `citation_verify` skill (which runs citeguard) instead of running
  the citation checker itself. Use this for both the "find me 5 similar
  case reports for my draft" task and the "find background/guideline
  references for my discussion" task in case-report drafting.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - AskUserQuestion
---

# similar-cases-search: PubMed-grounded reference candidates for case reports

You are a literature-search assistant for case reports. Your job is to take
the clinical features of the user's case and **return BibTeX entries the
author can paste into `refs.bib`**, where every field is grounded in a
PubMed record the author can re-fetch by PMID.

The skill runs in one of two modes (`search_mode`):

- **`similar_cases`** (default) — finds prior case reports of the same
  presentation/diagnosis. Used for the "have others reported this?"
  question and as direct comparators in the Discussion.
- **`background_literature`** — finds reviews, guidelines, and original
  studies establishing the *typical* presentation, epidemiology,
  diagnostic criteria, or standard-of-care treatment. Used as
  "anchors" against which the case's deviation is shown (e.g.,
  `bottom_line_message` expects an anchor per finding), and to support
  background paragraphs of the Introduction / Discussion.

This skill is part of the "Writing with AI" workflow, in which the AI
**must never invent citations**. The discipline is strict:

- Do not write `@article{...}` blocks from memory.
- Every emitted BibTeX entry must come from a PubMed efetch response for a
  specific PMID returned in the same session.
- If a field is missing from the PubMed record (e.g., no DOI), omit it. Do not
  guess it.

## When to invoke

User says something like:

- 「この症例に似た症例報告を PubMed で探して」(→ `similar_cases`)
- 「主訴と診断から refs.bib の候補を5件出して」(→ `similar_cases`)
- "Find similar case reports for this presentation and add them to refs.bib"
  (→ `similar_cases`)
- 「典型的な daptomycin の副作用プロファイルをまとめた review を探して」(→
  `background_literature`)
- 「IgG4関連疾患の診断基準のガイドラインを refs.bib に追加して」(→
  `background_literature`)
- "Find background literature / guidelines for the discussion anchor"
  (→ `background_literature`)

## Inputs

- **Required**: `search_mode` — one of `similar_cases` |
  `background_literature`. Default `similar_cases`.
- **Required**: case keywords. Either:
  - free-text from the user ("80-year-old male, eosinophilic pneumonia after
    daptomycin"), OR
  - a path to `@draft.md` from which the skill extracts diagnosis / exposure /
    presentation keywords.
- **Optional**: path to `refs.bib`. Default: the `refs.bib` in the same
  project folder as the manuscript being worked on
  (`projects/<name>/refs.bib`). If neither a path nor an active project
  folder is known, ask the author — do **not** fall back to `demo/refs.bib`
  silently; `demo/refs.bib` is workshop-practice material only, and
  appending real-case citations to it pollutes the teaching files.
  Candidates are appended here after the author approves them. **Both modes
  append to the same `refs.bib`** — citation keys are `pmid<PMID>`
  regardless of mode, so downstream skills (`citation_verify`,
  `bottom_line_message`) treat the two pools uniformly.
- **Optional**: desired number of candidates (default: 5, max: 20).
- **Optional**: NCBI API contact email. Required by NCBI E-utilities terms of
  use. If not supplied, ask the user once via `AskUserQuestion` and remember
  the answer for the rest of the session.

## Procedure

### 0. Reusable script vs. inline calls

This skill ships a committed, stdlib-only engine at
[`scripts/pubmed_search.py`](scripts/pubmed_search.py) (see
[`scripts/README.md`](scripts/README.md)). **The script is the primary path** —
it is stdlib-only Python and runs the same on Windows, macOS, and Linux, and it
lets any assistant produce grounded BibTeX by running one command, including
assistants with no web-search tool (e.g. when a letter is delegated to a model
that cannot browse). The inline `curl` + Python recipe in steps 2–3 below is
POSIX-only (bash + curl) and is kept as a **manual fallback** for when the
script cannot run (e.g. a mac/Linux session without the repo checked out). Do
not start from the curl recipe when the script is available.

The script splits the work to keep search output from ever being confused with
the manuscript's render bibliography:

- `search` reads a **search formula saved in the project folder** and writes a
  `<topic>.candidates.md` **staging** file (a candidates table + verbatim
  quotes + BibTeX blocks). It is **not** a `.bib`.
- `add` appends **author-approved** PMIDs to the single render `refs.bib`. It
  is the only command that writes a `.bib`.

Keep the case-specific search formula and its output in the git-ignored project
folder, so the repo stays clean (per the repo `CLAUDE.md`, `projects/*` is
Git-ignored):

```
projects/<name>/
  searches/<topic>.query.txt        # the search formula (input)
  searches/<topic>.candidates.md    # the search output (staging; NOT a .bib)
  refs.bib                          # the single render bibliography (add appends here)
```

When using the script, step 1 below (build + surface the query) and step 4
(show candidates, get author approval) still apply — write the agreed query to
`searches/<topic>.query.txt`, run `search`, surface the candidates.md, then run
`add` only for the PMIDs the author approves. The NCBI email comes from
`--email` or `$NCBI_EMAIL` (never hardcoded). Step 6 (`citation_verify`) is
unchanged.

```bash
export NCBI_EMAIL=you@example.com
python skills/similar_cases_search/scripts/pubmed_search.py search \
  --query-file projects/<name>/searches/<topic>.query.txt \
  --mode background_literature --max 5 --highlight confounding,indication
# ...author reviews <topic>.candidates.md and approves PMIDs...
python skills/similar_cases_search/scripts/pubmed_search.py add \
  --pmids 12345678,23456789 --bib projects/<name>/refs.bib
```

### 1. Build the PubMed query

Convert the case features into a PubMed query string. The filter clauses
depend on `search_mode`:

Common rules (both modes):

- Combine 2–4 clinical concepts with `AND`.
- Use MeSH terms when the concept is a recognized MeSH heading (drug, disease,
  organism). Append the `[mh]` tag.
- Use `[tiab]` for free-text concepts not in MeSH.
- Restrict to humans with `AND humans[mh]` unless the user objects.

Mode-specific clauses:

- `similar_cases`: append `AND "case reports"[pt]` so PubMed returns only
  case reports.
- `background_literature`: **do not** append `"case reports"[pt]`. Instead
  append a publication-type filter focused on synthesis / standards:
  `AND (review[pt] OR "systematic review"[pt] OR meta-analysis[pt] OR
  guideline[pt] OR "practice guideline"[pt] OR randomized-controlled-trial[pt])`.
  This biases results toward background-anchor literature rather than
  prior single cases.

Example construction:

| Mode | User input | Query string |
|---|---|---|
| `similar_cases` | "daptomycin-induced eosinophilic pneumonia" | `(daptomycin[mh] OR daptomycin[tiab]) AND (eosinophilic pneumonia[mh] OR eosinophilic pneumonia[tiab]) AND "case reports"[pt] AND humans[mh]` |
| `similar_cases` | "IgG4-related disease presenting as orbital pseudotumor" | `(IgG4-related disease[mh] OR IgG4-related disease[tiab]) AND (orbital pseudotumor[tiab]) AND "case reports"[pt] AND humans[mh]` |
| `background_literature` | "daptomycin adverse effect profile review" | `(daptomycin[mh] OR daptomycin[tiab]) AND (adverse effects[mh] OR safety[tiab]) AND (review[pt] OR "systematic review"[pt] OR meta-analysis[pt] OR guideline[pt]) AND humans[mh]` |
| `background_literature` | "IgG4-related disease diagnostic criteria guideline" | `(IgG4-related disease[mh] OR IgG4-related disease[tiab]) AND (diagnostic criteria[tiab] OR diagnosis[mh]) AND (guideline[pt] OR "practice guideline"[pt] OR review[pt]) AND humans[mh]` |

**Show the user the constructed query** before executing it. If the user
revises it, use the revised version.

### 2. esearch.fcgi → PMID list (manual fallback — prefer `scripts/pubmed_search.py`)

Call NCBI E-utilities `esearch.fcgi` to get PMIDs. Use `Bash` with `curl`:

```bash
EMAIL="user@example.com"   # supplied by the user
TOOL="writing_with_AI"
QUERY="$(printf '%s' '<the query from step 1>' | python -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read()))')"
N=5                         # number of candidates
curl -sS \
  "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=${QUERY}&retmax=${N}&sort=relevance&tool=${TOOL}&email=${EMAIL}" \
  > /tmp/esearch.xml
```

Parse the `<Id>...</Id>` elements to a PMID list. If the result count is zero,
report that to the user and offer to broaden the query (drop one term, switch
`[mh]` → `[tiab]`, remove the `case reports`[pt] filter, etc.).

**Rate limits**: NCBI permits 3 requests/sec without an API key. Sleep 0.4s
between requests in a loop. With an API key, the limit is 10/sec.

### 3. efetch.fcgi → MEDLINE / PubMed XML (manual fallback — prefer `scripts/pubmed_search.py`)

For each PMID, fetch the full record:

```bash
PMIDS="12345678,23456789,34567890"
curl -sS \
  "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=${PMIDS}&retmode=xml&tool=${TOOL}&email=${EMAIL}" \
  > /tmp/efetch.xml
```

Parse the XML (Python `xml.etree.ElementTree` is enough). Map each
`<PubmedArticle>` to a BibTeX `@article` entry using only these fields:

| BibTeX field | Source in PubMed XML |
|---|---|
| `title` | `MedlineCitation/Article/ArticleTitle` |
| `author` | concat of `Author/LastName, FirstName` (or `Initials`), joined by ` and ` |
| `journal` | `Journal/Title` (fall back to `Journal/ISOAbbreviation` if Title is absent) |
| `year` | `Journal/JournalIssue/PubDate/Year` (fall back to `MedlineDate` first 4 digits) |
| `volume` | `Journal/JournalIssue/Volume` |
| `number` | `Journal/JournalIssue/Issue` |
| `pages` | `Article/Pagination/MedlinePgn` |
| `doi` | `PubmedData/ArticleIdList/ArticleId[@IdType='doi']` |
| `pmid` | `MedlineCitation/PMID` |

**Citation key**: `pmid<PMID>` (e.g., `pmid12345678`). This collides-free and
makes the PMID auditable from the key alone.

**Omit, don't invent**: if `doi` or `volume` is missing from the XML, leave the
field out. Never fill in a placeholder.

**Also extract a display quote (not a BibTeX field).** From each record's
`MedlineCitation/Article/Abstract/AbstractText`, pull one **verbatim** sentence
or fragment (≤ 40 words) that shows *why* this reference supports the intended
point. This quote is surfaced to the author in step 4 so they can judge
relevance from the source text, not from the title alone. It is **not** written
into `refs.bib`. If a record has no abstract, mark the quote
`[no abstract available]`. Copy the quote verbatim from the efetch XML; never
paraphrase it, so it stays auditable.

### 4. Show candidates to the user

Emit a compact summary table **before** writing to `refs.bib`. Include the
mode in the header so the author can distinguish similar-case hits from
background-literature hits when both modes have been run. **Every candidate
must be shown with a verbatim supporting quote** (from step 3) so the author
can verify relevance from the abstract text, not the title alone; listing a
reference without a grounding quote is not acceptable:

```markdown
## similar-cases-search candidates

Mode: `similar_cases` (or `background_literature`)
Query: `(daptomycin[mh] OR daptomycin[tiab]) AND ... AND "case reports"[pt]`
Total hits: 47 (showing top 5 by relevance)

| # | PMID | Year | Journal | Type | Title (truncated) |
|---|---|---|---|---|---|
| 1 | 12345678 | 2021 | BMJ Case Rep | case-report | Daptomycin-induced eosinophilic pneumonia in ... |
| 2 | 23456789 | 2019 | Chest | case-report | A case of eosinophilic pneumonia after ... |

Supporting quotes (verbatim from each abstract):
- **#1 (PMID 12345678)**: "<verbatim sentence showing why this supports the point>"
- **#2 (PMID 23456789)**: "<verbatim sentence showing why this supports the point>"
```

In `background_literature` mode, the `Type` column reflects PubMed's
publication-type tag (`review`, `systematic-review`, `meta-analysis`,
`guideline`, `practice-guideline`, `RCT`) so the author can prefer
higher-tier syntheses when picking anchors.

Ask the user (`AskUserQuestion`) which PMIDs to keep before appending to
`refs.bib`. Default to "all 5" if the user wants a fast workflow, but always
offer the choice — the user is the citation gatekeeper.

### 5. Append to refs.bib

Append the approved entries to `refs.bib` (Edit tool, never overwrite the
file).

- Before writing, `Grep` for the citation key (`pmid<PMID>`) in `refs.bib`. If
  it already exists, skip it (don't duplicate, don't merge).
- Add a single blank line between the existing content and the new block.
- Preserve the original file's line endings.

Example block to append:

```bibtex

@article{pmid12345678,
  title = {Daptomycin-induced eosinophilic pneumonia: a case report},
  author = {Yamada, Taro and Suzuki, Hanako and Tanaka, Ichiro},
  journal = {BMJ Case Reports},
  year = {2021},
  volume = {14},
  number = {3},
  pages = {e240123},
  doi = {10.1136/bcr-2020-240123},
  pmid = {12345678}
}
```

**Persist the supporting quotes.** The verbatim quote shown for each candidate
is display-only for `refs.bib`, but it must not vanish into chat history. After
the author approves, append each approved entry's quote to
`reference_quotes.md` in the same directory as `refs.bib` (Edit/Write, append
only, never overwrite). One block per citation key:

```markdown
## @pmid12345678 — <Journal Year>
- Claim: "<the draft sentence / point this citation is meant to back>"
- Quote (verbatim): "<the abstract sentence shown at step 4>"
- Location: <where the quote sits, e.g., abstract conclusions>
- Status: pending
```

This block shape is the **canonical `reference_quotes.md` format**, shared
with `letter_to_editor`'s reference quote gate. `Status:` always starts as
`pending`; it flips to `approved` only when the author confirms that the
quote supports that specific claim — the approval gate lives in the calling
workflow, not in this skill. Never omit or delete the `Status:` field, and
never write a block in any other shape (mixed formats break the gate check).

If a record had no abstract, record `Quote (verbatim): [no abstract available]`
and note why it was still chosen (e.g., the title states the methodological
standard). This file is where the author reviews the quotes later; keep it in
sync with the approved `refs.bib` entries.

### 6. Verify by delegating to `citation_verify`

After appending, do **not** run citeguard from this skill. Hand off to the
`citation_verify` skill instead, passing:

- the `refs.bib` path that was just modified,
- the email collected in step 2 (NCBI contact),
- the list of citation keys just appended (so `citation_verify` can scope its
  surfaced findings to the new entries — the report on disk still covers the
  whole file).

`citation_verify` is responsible for:

- installing / locating `citeguard`,
- running it with `--all --email`,
- categorizing each entry as `found` / `likely_wrong` / `not_found` /
  `retraction`,
- emitting a structured summary block.

This skill's job in step 6 is to **read `citation_verify`'s summary back into
its own final message** so the caller sees the verification result inline.
Do not re-categorize or override `citation_verify`'s verdict.

If `citation_verify` reports any `likely_wrong` / `not_found` / `retraction`
entries among the keys just appended, surface them prominently — they
represent BibTeX-assembly errors or upstream PubMed data issues that the
author needs to act on. `found`-only outcomes are silent successes.

## Rules (must follow)

1. **Never invent citation metadata.** If you cannot fetch the PubMed XML in
   this session, do not emit a BibTeX entry. Tell the user the network call
   failed and stop.
2. **Citation key = `pmid<PMID>`** in both modes. This makes every entry
   re-verifiable and uniform across modes.
3. **One PMID = one BibTeX entry.** Do not merge or de-duplicate by title.
4. **Respect `search_mode`.** `similar_cases` uses `"case reports"[pt]`;
   `background_literature` uses the review / guideline / RCT filter. Do
   not silently mix modes within one query; if the author wants both,
   run the skill twice.
5. **Surface the query to the user before executing.** The query is the
   reviewable artifact; the PMID list is just its consequence.
6. **Surface the `citation_verify` summary.** Do not declare success until
   `citation_verify` has run and you have transcribed at minimum the counts
   line (and the `likely_wrong` / `not_found` / `retraction` tables when
   non-zero) into this skill's final message.
7. **Never edit `draft.md` from this skill.** This skill only adds to
   `refs.bib` (and the companion `reference_quotes.md`). The author decides
   where in the manuscript to cite each entry.
8. **Persist supporting quotes to `reference_quotes.md`.** Quotes are
   display-only for `refs.bib` but must be saved alongside it so the author can
   review them later, not only in chat.

## Output format

The final assistant message must contain, in this order:

1. The `search_mode` used (`similar_cases` or `background_literature`).
2. The PubMed query string (the exact `term=` value used).
3. The candidates table (from step 4), **with a verbatim supporting quote for
   every candidate** (title-only listings are not acceptable).
4. The list of PMIDs the user approved.
5. The BibTeX block appended to `refs.bib` (for copy-paste audit), and the
   path to `reference_quotes.md` where the approved entries' verbatim quotes
   were saved.
6. The `citation_verify` summary block (counts of `found` / `likely_wrong` /
   `not_found` / `retraction` plus per-category tables), copied through from
   `citation_verify`'s output, plus the path to the full report it produced.
7. A one-line next step. For `similar_cases`, suggest a Discussion
   placement; for `background_literature`, suggest using the entries as
   anchors in `bottom_line_message` or in the Introduction's background
   paragraph.

## Failure modes and how to handle them

| Failure | Handling |
|---|---|
| `esearch` returns 0 hits | Suggest 3 query relaxations (drop term / switch `[mh]`→`[tiab]` / drop `"case reports"[pt]`). Ask the user which to apply. |
| `efetch` returns partial XML (network truncation) | Retry once with 2s backoff. If still partial, drop the affected PMIDs and report the failure. Do not emit partial BibTeX. |
| NCBI rate-limit (HTTP 429) | Wait 1s, retry. If repeated, suggest the user supply an NCBI API key. |
| `citation_verify` reports a `likely_wrong` for a candidate the user already approved | Surface the diff from its report; ask whether to keep, remove, or replace with the candidate it suggested. Do not silently re-edit `refs.bib`. |
| `citation_verify` is unavailable (citeguard not installed, etc.) | Surface its error and stop before declaring step 6 done. Do not skip verification silently. |
| `refs.bib` already contains `pmid<PMID>` | Skip that entry silently in step 5; mention the skip in the final summary. |
| User has no NCBI email configured | Ask once via `AskUserQuestion` and reuse for the rest of the session. Do not call NCBI without an email. |

## Self-check before returning

1. Did every emitted BibTeX entry come from a PubMed XML record fetched in
   this session? (If "from memory" — start over.)
2. Did you show a **verbatim supporting quote** for every candidate before the
   author approved it (title-only listing = redo), and **save the approved
   quotes to `reference_quotes.md`** so they outlive the chat?
3. Is the citation key `pmid<PMID>` for every entry?
4. Did you append (not overwrite) `refs.bib`?
5. Did you hand off to `citation_verify` (not run citeguard yourself) and
   read its summary?
6. Did you transcribe the `citation_verify` counts (and the non-zero
   per-category tables) into this skill's final message?
7. Did you avoid editing `draft.md`?

## Testing this skill

A regression fixture lives at `skills/similar_cases_search/tests/`. Because
the skill depends on the live PubMed API, the fixture provides a frozen efetch
XML response so the BibTeX assembly logic can be tested offline:

- `tests/fixture_efetch.xml` — a saved PubMed efetch XML for two PMIDs.
- `tests/expected_refs.bib` — the BibTeX block the skill should produce from
  that XML.

Self-test procedure:

1. Treat `tests/fixture_efetch.xml` as if it came from step 3 (skip steps 1–2).
2. Run the BibTeX-assembly logic on it.
3. Diff the output against `tests/expected_refs.bib`.

Pass criteria:

- Exactly two `@article` entries are produced.
- Both citation keys match `pmid<PMID>`.
- All fields present in the fixture XML are present in the BibTeX, in the
  field order specified above.
- No invented fields. (Specifically: PMID 99999002 in the fixture lacks a DOI;
  the corresponding entry must omit `doi =`, not insert a placeholder.)

The citeguard / citation-verification logic is covered by
`skills/citation_verify/tests/` (frozen citeguard report → expected summary).
This file's fixture intentionally stops at BibTeX assembly.

## Reference

- NCBI E-utilities documentation: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- PubMed publication-type filters:
  https://pubmed.ncbi.nlm.nih.gov/help/#publication-types
- Citation verification is delegated to
  [citation_verify](../citation_verify/SKILL.md), which wraps the
  citation-checker (citeguard) tool: https://github.com/SRWS-PSG/citation-checker
- Upstream callers: [case_report_workflow](../case_report_workflow/SKILL.md)
  invokes this skill in `similar_cases` mode at Step 4 and in
  `background_literature` mode at Step 5.
  [bottom_line_message](../bottom_line_message/SKILL.md) expects
  background-literature entries to be present as "anchors" for each
  takeaway.
- This skill follows the same "indicate, don't rewrite" discipline as
  [deidentify_check](../deidentify_check/SKILL.md), with the narrow exception
  that approved BibTeX entries are appended to `refs.bib` after explicit
  author confirmation.
