---
name: letter_to_editor
version: 0.1.0
description: |
  Lightweight orchestrator that turns a Japanese memo into an English
  "Letter to the Editor" responding to a single already-published target
  article. The letter has a fixed three-paragraph shape: (P1) genuine
  praise of the target article's contribution, then (P2) and (P3) two
  paragraphs that each point out one bias that distorts the conclusion
  **or** one spin in the interpretation of the results. The orchestrator
  reads the target article that the author has placed by hand in the
  project folder (it never fetches it from the web), runs a
  human-in-the-loop quote-verification gate before drafting, grounds every
  critique in the article's actual text and in PubMed-verified literature,
  and writes `draft.md` only in the drafting and revision steps. It never
  invents citations, never misrepresents the target article, and never
  fetches journal guidelines — word and reference limits come from the memo
  or from the author. This skill is scoped to commentary-only letters
  (no original patient data); for case reports use `case_report_workflow`.
  Triggers: 「レターを書く」「letter to the editor」「エディターへの手紙」
  「この論文に反論レター」「spinを指摘するレター」「論文への批評レター」.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
---

# letter-to-editor: Japanese memo → three-paragraph spin/bias critique letter

You are the conductor for drafting a **Letter to the Editor** that responds
to one already-published article. Your job is to **call sub-skills in order,
surface their outputs back to the author, and gate progress on explicit
author confirmation** — especially at the quote-verification gate, where the
author must confirm you have the right article and the right passages before
any critique is drafted.

This skill is the only place where the full letter-drafting sequence lives.
Sub-skills (`similar_cases_search`, `citation_verify`, `proofread-manuscript`,
`letter_review_simulator`) can be called independently for one-off tasks; this
orchestrator is for the case where the author wants to turn a Japanese memo
into a finished letter start to finish.

## Scope (what this skill is and is not)

- **Is**: a commentary-only letter responding to a single target article,
  pointing out conclusion-distorting bias or interpretation spin.
- **Is not**: a vehicle for the author's own original patient data or case.
  There is no clinical-fact ledger, no `deidentify_check`, no consent
  statement, and no CARE audit here. If the author wants to report their own
  case, redirect to `case_report_workflow`.
- **Is not**: a journal-guideline fetcher. This skill does not run
  `submission_guidelines_check` and does not WebFetch author instructions.
  Word and reference limits come from the memo, or the author supplies them.

## The fixed three-paragraph structure

Every letter this skill produces has exactly three body paragraphs:

| Paragraph | Role | Discipline |
|---|---|---|
| **P1 — Praise** | Acknowledge the target article's genuine contribution and why it matters | Concrete, grounded in the article's real strengths. Not a hollow courtesy line. |
| **P2 — Critique 1** | Point out **one** conclusion-distorting bias **or** one interpretation spin | Classified against the taxonomy below; grounded in an author-confirmed quote; supported by a verified citation. |
| **P3 — Critique 2** | A **second**, distinct bias or spin | Same discipline as P2; must not repeat P2's point. |

Plus a one-sentence constructive close and a signature placeholder
(`[TODO: author name, affiliation, corresponding-author contact]`). The
salutation is `Dear Editor,`.

The author may request a deviation (e.g., a single critique paragraph).
Surface the three-paragraph rationale once; if they still want a deviation,
comply and record it in the workflow state header.

## Spin / bias taxonomy (the analytical backbone)

P2 and P3 are not free-form complaints. Each critique must be classified as
one of the following, so the letter reads as principled appraisal:

**A. Bias that distorts the conclusion**

| Code | Pattern |
|---|---|
| B1 | Confounding not addressed (incl. confounding by indication), yet a causal conclusion is drawn |
| B2 | Selection / information / immortal-time bias that undercuts the headline claim |
| B3 | Underpowered null read as "no effect" (absence of evidence ≠ evidence of absence) |
| B4 | Primary outcome not met, but the abstract/conclusion still claims benefit |

**B. Spin in the interpretation of results**

| Code | Pattern |
|---|---|
| S1 | Non-significant result reworded as positive ("trend toward", "numerically higher") |
| S2 | Causal language for an observational/non-randomized design (`caused`, `led to`, `reduced`, `improved` as causation) |
| S3 | Overgeneralization beyond the studied population / setting |
| S4 | Secondary / subgroup / within-group / post-hoc result promoted to headline |
| S5 | Mismatch between the conclusion and what the results actually show |

Each critique paragraph names its code internally (for your own reasoning and
for `letter_review_simulator`), grounds it in an author-confirmed quote from
the target article, and pairs it with a verified citation (a methodological
reference or contradicting evidence) where one strengthens the point.

## When to invoke

User says something like:

- 「この論文へのレターを書きたい。メモを渡すので最初から案内して」
- 「letter to the editor を書く」
- "Draft a letter to the editor pointing out the spin in this paper"
- The CLAUDE.md project hint points here for letter drafting.

If the author only wants one sub-skill task (e.g., "just verify these
refs"), invoke that sub-skill directly. Do not run the full orchestrator
for a single-step request.

## Inputs

- **Required at start**: the Japanese memo (free text) listing the points
  the author wants to make about the target article.
- **Required at start**: the target article, placed **by the author by hand**
  in the project folder (`projects/<name>/`) as a text / Markdown / PDF /
  pasted-abstract file. This skill **reads** that file; it never fetches the
  article from the web. If no target-article file is present, stop and ask
  the author to add one.
- **Required eventually** (collected via `AskUserQuestion` as needed):
  - NCBI E-utilities contact email — required because Step 4
    (`similar_cases_search`) and Step 5 (`citation_verify`) always run.
  - Word limit and reference limit — taken from the memo if stated there;
    otherwise asked of the author. This skill does not derive them from
    journal guidelines.
  - Author block (name, affiliation, corresponding-author contact) — taken
    from the memo if stated; otherwise asked at Step 6 so the signature is
    filled, not left as a placeholder.
- **Optional**: target journal name (context only), existing `refs.bib`
  path (default: `projects/<name>/refs.bib`), output language (default:
  English; the style discipline applies to English only).

Collect inputs lazily — ask only when the step that needs them is reached,
except the two required-at-start inputs (memo + target-article file), which
gate Step 1.

## Project folder

Implied default: `projects/<name>/` where `<name>` is derived from the memo
or the target article's topic, confirmed with the author at Step 1. Per the
repository CLAUDE.md, `projects/*` is Git-ignored working space; do not add
these files to Git unless the author explicitly asks. Artifacts written:
`draft.md`, `refs.bib`, `reference_quotes.md` (the **reference quote gate** —
one block per supporting citation, in the canonical format written by
`similar_cases_search`: citekey heading, `Claim`, `Quote (verbatim)`,
`Location`, and `Status: pending | approved`; "row" elsewhere in this file
means one such block; drafting may only cite `approved` rows — see Steps 4
and 6),
`target_article_ledger.md`, `handoff.md`, and a
`searches/` subfolder holding the literature-search formulas and their staging
output (`searches/<topic>.query.txt` + `searches/<topic>.candidates.md`; see
Step 4). The author-placed target-article file stays as-is (read-only). All of
this lives under the Git-ignored project folder, so the search formulas never
pollute the repo.

## State tracking

Maintain a workflow state block and emit it as the **first block** of every
reply during the workflow:

```markdown
### letter-to-editor state

| step | name | status | artifact |
|---|---|---|---|
| 1 | input + folder + limits | pending / done | <folder path; word/ref limits; target-article file> |
| 2 | target-article ledger + quote gate | pending / done | <quotes confirmed? yes/no> |
| 3 | spin/bias analysis | pending / done | <P2 code + P3 code> |
| 4 | similar_cases_search + reference quote gate | pending / done | <refs.bib path + N added; quote gate: A approved / P pending> |
| 5 | citation_verify (initial) | pending / done | <counts: found/likely_wrong/not_found/retraction> |
| 6 | draft generated | pending / done | <draft.md path; word count; ref count; TODO count> |
| 7 | review (letter_review_simulator + proofread + limits) | pending / done | <Major count; style hits; over-limit? yes/no> |
| 8 | revision applied | pending / done | <revision diff summary> |
| 9 | citation_verify (final) + limits recheck | pending / done | <counts; within limits? yes/no> |
| 10 | hand-off | pending / done | <handoff.md path> |
```

Update the state block after every step transition. Mark a step `skipped`
(not `done`) only when the author explicitly chose to skip, and record why.
Steps 4 and 5 are **not** skippable. The reference quote gate inside Step 4 is
also **not** skippable: Step 4 is not `done` while any `reference_quotes.md` row
is `pending`, and Step 6 must not start until every supporting row is
`approved`.

## Procedure

### Step 1 — Input, folder, and limits

1. Confirm the project folder name and create `projects/<name>/` if needed.
2. Confirm the Japanese memo is in hand. File it as a workflow note.
3. **Check for the target-article file** in `projects/<name>/` (Glob the
   folder). If none is present, stop and tell the author: "対象論文ファイルを
   `projects/<name>/` に置いてください（txt / md / pdf / 抄録の貼り付け可）。
   置いたら再開します。" Do not proceed without it.
4. Determine the **word limit** and **reference limit**: read them from the
   memo if stated; otherwise ask the author via `AskUserQuestion`. If the
   author does not know them, record "limits: unconfirmed" in the state and
   warn that the hand-off will flag this; draft without a hard cap but keep
   the letter short (letters are typically 400–1000 words, ≤ 5–10 refs).

Transition to Step 2 only after the folder, memo, and target-article file
are all confirmed present.

### Step 2 — Target-article ledger and quote-verification gate

This is the human-in-the-loop gate. **No critique is drafted until the author
confirms the article identity and the passages.**

1. **Read** the target-article file (`Read`; for PDF use the page range).
2. Build a **target-article ledger** — the article's identifying metadata
   and its actual claims, each tied to a verbatim quote:
   - identity: first author, year, journal, title (as printed in the file).
   - the article's stated objective.
   - the headline result(s), quoted verbatim.
   - the conclusion sentence(s), quoted verbatim.
   - the study design (RCT / cohort / case-control / cross-sectional /
     other), as stated.
3. From the memo + ledger, pull the **specific passages** the letter will
   engage in P2 and P3, as verbatim quotes with their location.
4. **Emit the gate** to the author:

   ```markdown
   #### 対象論文の確認 (quote gate)

   - 同定: <Author> <Year>. <Journal>. "<Title>"
   - デザイン: <design>
   - 結論 (原文引用): "<verbatim conclusion quote>"

   この論文で合っていますか? また、下記の該当箇所を批評対象にする予定です:

   - P2候補 (該当箇所引用): "<verbatim quote>"  — 想定: <taxonomy code + 一言>
   - P3候補 (該当箇所引用): "<verbatim quote>"  — 想定: <taxonomy code + 一言>

   この論文・この箇所で進めてよいですか? 修正があれば指摘してください。
   ```

5. Wait for the author to confirm or correct. Only confirmed quotes may be
   used downstream. If the author says the article or a passage is wrong,
   revise the ledger and re-emit the gate. Do not advance to Step 3 until the
   author confirms.

Write the ledger to `projects/<name>/target_article_ledger.md` after
confirmation. Every "the article states X" claim in the final letter must
trace to a verbatim quote in this ledger.

### Step 3 — Spin / bias analysis

Using the confirmed ledger and the memo, finalize the two critiques:

1. Classify each of the author's points against the taxonomy (B1–B4 /
   S1–S5). If a memo point does not map to any code, surface it and ask the
   author whether it is in scope (the letter is specifically about bias/spin;
   a point that is neither may belong in a different venue).
2. Select the **two strongest, distinct** points for P2 and P3. If the memo
   has more than two, ask the author to drop the weakest. If it has only one,
   surface that the three-paragraph structure wants two; offer to mine the
   ledger for a second, or proceed with a single-critique deviation
   (recorded in state).
3. For each selected critique, note what kind of citation would strengthen
   it (a methodological reference for the bias/spin pattern, or evidence
   that contradicts the overstated conclusion). These become the Step 4
   search targets.

Surface the P2/P3 plan (code + one-line claim + grounding quote + citation
need) and confirm with the author before Step 4.

### Step 4 — Background / supporting literature search (mandatory)

Confirm or collect the NCBI email. Invoke `similar_cases_search` with
`search_mode: background_literature`, querying for the references identified
in Step 3 (methodological references on the relevant bias/spin pattern, and
any study that contradicts the target article's overstated claim).

**Save the search formula in the project folder, not in chat.** Write each
agreed query to `projects/<name>/searches/<topic>.query.txt`, then run the
committed engine
[`similar_cases_search/scripts/pubmed_search.py`](../similar_cases_search/scripts/pubmed_search.py)
(`search` subcommand) so the search works even when the drafting is delegated
to a model that cannot browse the web. The script writes a
`searches/<topic>.candidates.md` **staging** file (not a `.bib`); only the
`add` subcommand appends author-approved PMIDs to the single render `refs.bib`,
so search output never gets confused with the render bibliography. The NCBI
email comes from `--email` or `$NCBI_EMAIL`.

Surface the candidates table **with a verbatim supporting quote for every
candidate** (per `similar_cases_search` step 4 — title-only listings are not
acceptable), so the author can verify relevance from the abstract text before
choosing which PMIDs to keep. Approved entries are appended to `refs.bib` via
the script's `add` subcommand (or by `similar_cases_search` itself).

**Then run the reference quote gate** (this is the part most easily skipped —
do not skip it). For every key appended to `refs.bib`, ensure a block exists in
`reference_quotes.md` in the canonical format (`similar_cases_search` writes it
with `Status: pending` when it appends); fill in the `Claim` field with the
exact draft sentence the citation is meant to back if it is still generic. Then
emit the gate to the author, in the same shape as the Step 2 quote gate:

```markdown
#### 参照文献の quote ゲート

- [@pmid<PMID>] — 主張: "<the sentence this will support in the draft>"
  - 該当 quote (verbatim): "<abstract quote>"
  - この quote は上の主張を支持していますか? (yes / 直す / 別文献)
```

A row flips to `status: approved` **only** when the author confirms that the
quote supports that specific claim. Passing `citation_verify` does **not**
approve a row — verify confirms the reference exists and is not retracted; it
says nothing about whether the source supports the claim. The two checks are
orthogonal, and a green `citation_verify` must never be read as quote approval.
If the author says the quote does not fit, either re-search for a source that
does (re-run `search`, re-surface quotes) or drop the claim; do not advance a
mismatched row to `approved`.

This step is **mandatory** — do not skip it. If the email is unavailable,
ask for it; do not bypass the search. If a genuinely strong critique needs
no external citation (the bias is self-evident from the article's own
numbers), record that explicitly, but still run the search for the other
critique.

### Step 5 — Citation verify (initial pass)

Invoke `citation_verify` against `refs.bib`. Transcribe its summary into the
state block. If `likely_wrong` / `not_found` / `retraction` counts are
non-zero, **pause** and ask the author to resolve before Step 6. Do not draft
with unverified citations except by explicit author override (recorded in
state). This step is **not** skippable.

### Step 6 — Draft generated

This is the **first** step where the orchestrator writes to `draft.md`.

**Precondition — the reference quote gate must be clear (手戻りゲート).** Before
writing a single line of `draft.md`, read `reference_quotes.md`. Every
supporting citekey in `refs.bib` (the target-article key is exempt — its
fidelity is gated by `target_article_ledger.md` at Step 2) must have a row with
`status: approved`. If any row is `pending`, or a supporting key has no row at
all, **do not write `draft.md`.** Stop and send the author back to the Step 4
quote gate, naming exactly which keys are unapproved and showing each one's
claim and verbatim quote for confirmation. Drafting consumes `approved` rows as
its source of truth: a citation may appear in `draft.md` only if its row is
`approved`, and the sentence it backs must match that row's recorded claim.
Resume drafting only after the author clears the outstanding rows. Do not work
around a `pending` row by silently dropping the citation — surface it.

Before writing, read the shared style file
[`../case_report_workflow/style_discipline.md`](../case_report_workflow/style_discipline.md).
The English-prose rules there apply in full (no em-dash, ≤ 25 words per
sentence with a 40-word ceiling, active voice for actor sentences, banned
terms, `Author. Year. Journal.` reference format). Note that banned-term S2
patterns (`caused`, `led to`, `contributed to`, `resulted in`, `affected`)
are doubly relevant here: the letter must not commit the same causal
overreach it accuses the target article of.

Generate the letter with this structure:

```markdown
Dear Editor,

<P1 — praise: one paragraph acknowledging the target article's
contribution, grounded in its real strengths.>

<P2 — critique 1: topic sentence states the bias/spin; then the
author-confirmed quote (paraphrased fairly or quoted with quotation marks);
then why it distorts the conclusion; then the constructive implication.
Cite the supporting reference with a pandoc citation key, e.g. [@pmid<PMID>].
Cite the target article itself as [@<target-key>].>

<P3 — critique 2: same shape, a distinct point.>

<one-sentence constructive close.>

Sincerely,
<author block — name, affiliation, corresponding-author contact, from the
memo or asked at this step>
```

**References are not hand-written in `draft.md`.** The letter is rendered
later with pandoc, which builds the reference list from `refs.bib` and a CSL
style at render time. Therefore:

- Cite with **pandoc citation keys in square brackets**: `[@pmid<PMID>]` for a
  single source, `[@pmid<A>; @pmid<B>]` for several. Do **not** write numbered
  `[1]`/`[2]` markers and do **not** append a `## References` section to
  `draft.md`. The R8 "References list format" rule in `style_discipline.md` is
  satisfied by pandoc's rendered output, not by text in `draft.md`.
- The **target article must also be a `refs.bib` entry** so pandoc can cite it.
  Add it to `refs.bib` as a manual `@article` block whose fields come from the
  Step 2 ledger (first author, year, journal, title, volume/issue/pages, DOI),
  with a stable citekey (e.g. `<firstauthor><year>`), and cite it `[@<key>]`.
  Because the target article is often very recent, `citation_verify` may return
  `not_found` for this one key; that is expected for a just-published article.
  Record it in the state and do not treat it as a blocking failure (the author
  confirmed the article's identity at the Step 2 quote gate).
- Optionally leave a one-line comment at the bottom of `draft.md` recording the
  intended render command, e.g.
  `<!-- render: pandoc draft.md --citeproc --bibliography refs.bib --csl <style>.csl -o letter.docx -->`,
  so the author knows how the bibliography is produced.

Drafting rules:

- **Target-article fidelity**: every "the authors state / conclude / report
  X" sentence must trace to a verbatim quote in the Step 2 ledger. Do not
  paraphrase the article into something it did not say. If the letter needs a
  characterization the ledger does not support, insert
  `[TODO: confirm target-article wording for <point>]` instead of inventing
  it.
- **Citation discipline**: cite only pandoc keys `[@<key>]` that both exist in
  `refs.bib` **and** carry an `approved` row in `reference_quotes.md`. Existence
  in `refs.bib` is necessary but not sufficient — an unapproved key must not be
  cited (see the Step 6 precondition). If a needed key is absent, do not invent
  it — insert `[TODO: similar_cases_search for <topic>]`; if it is present but
  `pending`, stop and return to the Step 4 quote gate rather than citing it. The
  target article is the one exception: cite it `[@<target-key>]` after its
  manual `@article` block (built from the Step 2 ledger) has been added to
  `refs.bib`; its fidelity is gated by `target_article_ledger.md`, not by
  `reference_quotes.md`.
- **Constructive tone**: open each critique by acknowledging the point's
  context, state the issue with evidence, and phrase it as something the
  field (or a future study) can address. No ad hominem, no "the authors
  failed to", no rhetorical questions implying incompetence.
- **Respect the limits**: keep within the Step 1 word and reference limits.
  If a critique cannot fit, tighten prose before dropping a citation.
- **Author block**: fill the signature from the memo, or ask the author at
  this step. Do not leave it as a `[TODO: ...]`. If the author genuinely
  defers it, mark it `<author block — to be completed at submission>` (not a
  `[TODO:]`) and surface it at hand-off as the one author-owned deferral.
- Use English (default). The style discipline applies to English only; ask
  the author if a Japanese letter is wanted instead.

Write the file via `Write` (new file) only. If `draft.md` already exists,
do not overwrite — surface it and ask the author how to proceed.

At the end of Step 6, run the **style self-check** from
[`style_discipline.md`](../case_report_workflow/style_discipline.md):

1. `grep -c '—' draft.md` must return `0`.
2. Long-sentence ratio (> 25-word sentences / total) ≤ 15 %.
3. No prose sentence > 40 words (quotations excluded).
4. Banned-term grep returns `0` for each of `significant`, `demonstrated`,
   `caused`, `led to`, `contributed to`, `clearly`, `obviously`,
   `^[Hh]owever,`.
5. `draft.md` contains **no** `## References` section and **no** numbered
   `[1]`/`[2]` citation markers; every citation is a pandoc key `[@<key>]`.
6. Every `[@<key>]` cited in `draft.md` exists in `refs.bib` (Grep the keys),
   including the target-article key.

Also count words, the number of distinct cited keys (`[@<key>]`), and
`[TODO: ...]` placeholders, and surface all counts in the state block. Word
count is body text only (the rendered reference list is produced by pandoc and
is not in `draft.md`); when checking the journal's "including references"
limit, add the expected rendered reference lines. Fix any style-self-check
failure before emitting. Over-limit word/reference counts are a flag for
Step 8.

### Step 7 — Review

Invoke three reviews on the drafted letter (read-only on `draft.md`):

- `letter_review_simulator` — fairness, constructiveness, accuracy of the
  target-article representation, overclaim, scope, and taxonomy soundness of
  P2/P3.
- `proofread-manuscript` — English prose style (the `style_discipline.md`
  rules). Skip this invocation if the letter is in Japanese.
  **Fallback**: this is a user-level skill not shipped with the repository.
  If it is not available in the session, do not stop — run the
  `style_discipline.md` self-check (grep-based) yourself and use its
  findings as the Style items; record the fallback in the state.
- A **limits check** — compare the Step 6 word and reference counts against
  the Step 1 limits. Over-limit is a punch-list item.

Aggregate into a single punch-list:

- Fairness / accuracy / overclaim / scope items → from
  `letter_review_simulator` (Major / Minor).
- Style items (em-dash, > 25-word sentences, banned terms, passive voice) →
  from `proofread-manuscript` (default disposition: `auto-apply` in Step 8;
  they do not touch the substance of the critique).
- Over-limit items → from the limits check.

De-duplicate overlaps. Surface the merged punch-list and ask the author which
items to accept. The author may dismiss items (recorded with a one-line
reason). Style items default to accept.

### Step 8 — Revision applied

This is the **second** step where the orchestrator writes to `draft.md`.

For each accepted item, apply the smallest targeted `Edit`:

- One edit per item (preserves traceability).
- Re-read the affected paragraph after each edit.
- **Honor the target-article ledger.** Any new characterization of the
  article must trace to a confirmed quote, else insert a `[TODO: confirm
  target-article wording]` placeholder.
- Cite only keys already in `refs.bib`. If a Major comment requests a new
  citation, re-invoke `similar_cases_search` (which loops to Step 5 to
  verify) before adding it.
- If `letter_review_simulator` flagged the letter's own overclaim or a
  mischaracterization of the target article, the rewrite must remove the
  overstatement without inventing new claims about the article.
- Style items from `proofread-manuscript` are auto-applied. Re-run the
  `style_discipline.md` self-check afterward.

If a revision pushed the letter back over the word/reference limit, tighten
before moving on. Surface a diff summary (touched paragraphs, word-count
change, em-dash count, long-sentence ratio before/after) in the state block.

### Step 9 — Citation verify (final) and limits recheck

1. Re-invoke `citation_verify` on the updated `refs.bib`. Confirm every
   pandoc key `[@<key>]` cited in `draft.md` exists in `refs.bib`, and that
   `citation_verify` returns zero `likely_wrong` / `not_found` /
   `retraction` for the cited keys. Loop back to Step 8 for any failure. The
   single exception is the just-published target-article key, which may legit-
   imately return `not_found` because it is not yet indexed; record that and
   do not loop on it (its identity was confirmed at the Step 2 quote gate).
2. Recheck word and reference counts against the Step 1 limits. If over,
   loop back to Step 8. If the limits were "unconfirmed", record that the
   recheck could not be performed and carry the warning to the hand-off.

### Step 10 — Hand-off

Produce a hand-off package as a single Markdown summary the author can paste
into a project log or share with co-authors. Contents:

- Final `draft.md` path + word count + reference count (and the limits they
  were checked against, or the "unconfirmed limits" warning).
- Final `refs.bib` path + entry count + `citation_verify` counts.
- The P2/P3 taxonomy codes and the one-line claim of each critique.
- The target-article identity (the article being responded to).
- Review punch-list with each item marked `addressed` / `dismissed` (with
  reason).
- A short "next actions" list (e.g., "[Co-author review](#co-author-review-round-after-hand-off)", "Add author block",
  "Submit via journal correspondence portal").

Before writing the hand-off, run these blockers:

- `[TODO: ...]` count in `draft.md` must be **zero** (author block,
  target-article wording placeholders, citation placeholders all resolved).
  If any remain, list them and refuse to write `handoff.md`.
- If limits were "unconfirmed", repeat that warning verbatim in the hand-off.

Write the hand-off to `projects/<name>/handoff.md`. Tell the author the
workflow is complete.

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
3. Re-enter **Step 8**, using the table's `修正` / `一部修正` rows, every
   accepted co-author suggestion (tracked change in `review/vN/report.md`,
   confirmed with the author item by item), and every adopted direct edit
   from `check_direct_edits.py` findings as revision items. This replaces `tracked_revision` Step 3; the branch writes
   `draft.md` only through Step 8, with all its rules still in force.
   Record rejected suggestions as ID-less table rows with reasons per
   `tracked_revision` Step 2; the target-article quote gate below also
   applies to suggestions that characterize the article.
   Any new characterization of the target article must trace to a quote
   confirmed at the Step 2 quote gate; a co-author's new claim about the
   article goes through that gate first. New supporting references must
   pass Step 4 (search + reference quote gate) and Step 5 before citation.
   Cite only keys in `refs.bib`, run the style self-check, and surface
   the revision diff summary.
4. Before any upload, re-run Step 9 (citation verify, final, plus word and
   reference limits recheck). Preserve its target-article exception and
   carry any "unconfirmed limits" warning to the hand-off. Require zero
   `[TODO: ...]`, as at Step 10. On verification failure, loop back to
   Step 8 and repeat verification; do not upload.
5. Run `tracked_revision` Steps 4–6: `make_tracked_md.py` + pandoc for
   tracked docx with original comments and replies, verification, then
   upload v{N+1} as a **new Doc** using its Step 0 hash-name and ledger
   procedure. Update `handoff.md` with the round number, new Doc URL,
   and response table path.

Keep the main 10-row state block unchanged. Emit and update this separate
round block alongside it (record any agreed baseline here):

```markdown
### co-author round N
| stage | status | artifact |
|---|---|---|
| fetch + direct-edit check (tracked_revision 1) | pending / done | <review/vN path; direct edits found?> |
| response table (tracked_revision 2) | pending / done | <path; rows by 対応> |
| revision (Step 8) | pending / done | <diff summary> |
| verification (Step 9) | pending / done | <citation counts; word/reference counts and limits or warning> |
| tracked v{N+1} upload (tracked_revision 4–6) | pending / done | <Doc URL; ledger row> |
```

## Rules (must follow)

1. **Sub-skills do the work.** This orchestrator does not re-implement
   literature search, citation verification, or letter review.
2. **`draft.md` writes only at Step 6 and Step 8.** Every other step is
   read-only on the letter.
3. **No invented citations.** Supporting references come through
   `similar_cases_search` and are verified by `citation_verify`. Every
   candidate is surfaced with a verbatim supporting quote before approval. The
   only `@article` block written by hand is the target article itself, built
   from the Step 2 ledger and added to `refs.bib` so pandoc can cite it; any
   other hand-written `@article` block is a workflow failure.
3a. **Pandoc-style citations, no hand-written reference list.** Prose cites
   `[@<key>]` keys; `draft.md` has no `## References` section and no numbered
   markers. Pandoc renders the bibliography from `refs.bib` at the end.
4. **No misrepresentation of the target article.** Every claim about what the
   article said must trace to a verbatim quote in the Step 2 ledger, and the
   passages must have passed the Step 2 quote-verification gate. Unsupported
   characterizations become `[TODO: confirm target-article wording]`.
5. **The quote-verification gate is mandatory.** Step 3 onward may use only
   the article identity and passages the author confirmed at Step 2.
6. **Fixed three-paragraph structure.** P1 praise, P2 + P3 critique. A
   deviation is allowed only after the structure rationale is surfaced once,
   and is recorded in the state header.
7. **Constructive tone only.** No ad hominem, no rhetorical jabs. The letter
   acknowledges the contribution before critiquing.
8. **No journal-guideline fetching.** Word/reference limits come from the
   memo or the author. This skill does not run `submission_guidelines_check`
   or WebFetch.
9. **Steps 4 and 5 are not skippable.** Background search and the initial
   citation verify always run.
10. **Style discipline lives in
    [`style_discipline.md`](../case_report_workflow/style_discipline.md).**
    Step 6 reads it, Step 7 verifies via `proofread-manuscript`, Step 8
    auto-applies. Do not duplicate the rules in procedure text.
11. **The letter must not commit the same overreach it critiques.** If P2/P3
    flag causal language (S2), the letter's own prose must avoid it too.
12. **Skips are explicit and recorded.** `skipped` ≠ `done`.
13. **Hand-off requires zero `[TODO: ...]` in `draft.md`.**
14. **Shared Google Doc co-author comments use only the co-author review
    round branch.** Revise only by re-entering Step 8. Never overwrite
    the existing Doc; follow the `tracked_revision` ledger procedure.

## Output format

The final assistant message (at completion) must contain, in this order:

1. The final state block (all rows `done` or `skipped`).
2. The hand-off package contents (Step 10).
3. The hand-off package path (`handoff.md`).
4. A one-line confirmation: "Letter-to-editor workflow complete. Review
   `handoff.md` and the final `draft.md` before submission."

For intermediate messages, surface: the updated state block, the current
step's output (transcribed or referenced), and an `AskUserQuestion` for the
next gate (proceed / revise / skip).

## Failure modes and how to handle them

| Failure | Handling |
|---|---|
| Co-author comments returned but `versions/draft.v1.md` is missing (v1 uploaded without the ledger) | Stop and tell the author. `tracked_revision` has no automated fallback. `pandoc <reviewed>.docx --track-changes=reject -t markdown` yields only a baseline candidate: citation keys return as rendered numbers, so every citation shows as a change. Use it only with explicit author agreement and record that in the round state. |
| `check_direct_edits.py` exits 2 | Show the detected paragraphs to the author. Record adopt / not adopt decisions as ID-less response-table rows before Step 8. |
| A verification step fails after co-author revision | Loop back to Step 8 with the findings, then repeat verification. Do not upload. |
| No target-article file in `projects/<name>/` | Stop at Step 1. Ask the author to place the file by hand. Do not WebFetch it. |
| Author confirms the article but says a chosen passage is wrong | Revise the Step 2 ledger and re-emit the quote gate. Do not advance until passages are confirmed. |
| Memo point maps to no taxonomy code | Surface it at Step 3; ask whether it is in scope. A non-bias/non-spin point may belong elsewhere. |
| Memo has only one usable critique | Surface the three-paragraph rationale; offer to mine the ledger for a second, or proceed as a single-critique deviation recorded in state. |
| NCBI email unavailable at Step 4 | Ask for it. Do not skip the mandatory background search. |
| `citation_verify` returns failures and the author overrides | Record the override in state with the author's one-line justification; require it again at Step 9. |
| Word/reference limits unknown and the author cannot supply them | Record "limits: unconfirmed", draft short, and carry the warning to the hand-off. Do not invent a journal's limit. |
| `draft.md` already exists at Step 6 | Do not overwrite. Surface it; ask whether to revise the existing file (skip to Step 7) or start a new folder. |
| `letter_review_simulator` flags the letter mischaracterizing the article | Treat as a Major item. Step 8 rewrite must re-ground the claim in a confirmed quote or drop it. |
| Author wants to skip the praise paragraph (P1) | Allowed as a recorded deviation, but surface once that editors weight constructive framing; default is to keep P1. |
| `proofread-manuscript` unavailable (user-level skill, not shipped with this repo) | Do not stop. Run the `style_discipline.md` self-check instead and use its findings as the Style items. Record the fallback in the state. |

## Self-check before returning at hand-off

1. Are all 10 state rows `done` or `skipped` (no `pending`)?
2. Did the Step 2 quote-verification gate occur and get author confirmation?
3. Does every "the article states X" sentence in `draft.md` trace to a
   verbatim quote in `target_article_ledger.md`?
4. Did `draft.md` get written only at Step 6 and Step 8?
5. Are all pandoc `[@<key>]` citations in `draft.md` (including the target-
   article key) present in `refs.bib` (Grep confirms), with no `## References`
   section and no numbered markers in `draft.md`?
6. Did `citation_verify` run at Step 9 and return clean for cited keys (target-
   article `not_found` excepted, if just-published and recorded)?
7. Is the letter within the confirmed word/reference limits (or is the
   "unconfirmed limits" warning carried to the hand-off)?
8. Does the letter have P1 + P2 + P3 (or a recorded deviation), with P2 and
   P3 each carrying a distinct taxonomy code?
9. (English letters) Does `draft.md` pass the `style_discipline.md`
   self-check (em-dash `0`, long-sentence ratio ≤ 15 %, no banned terms)?
10. Are there **zero** `[TODO: ...]` placeholders remaining in `draft.md`?
11. Is the hand-off written to `projects/<name>/handoff.md`?

## Testing this skill

A regression fixture lives at `skills/letter_to_editor/tests/`:

- `tests/fixture_memo.md` — a Japanese memo asking for a letter about a
  retrospective cohort study, with two critique points (confounding by
  indication → causal conclusion; a non-significant subgroup spun positive).
- `tests/fixture_target_article.md` — a short structured-abstract stand-in
  for the target article, with the conclusion and the two target passages
  quotable verbatim. (Synthetic fixture; PMIDs are illustrative.)
- `tests/fixture_refs.bib` — two PMID BibTeX entries: one methodological
  reference on confounding by indication, one on spin in non-randomized
  studies, **plus a manual entry for the target article** (so the pandoc
  target-article key resolves). (Synthetic fixture.)
- `tests/expected_draft.md` — the three-paragraph letter the skill should
  emit (P1 praise; P2 = B1 confounding; P3 = S4/S1 subgroup spin), within a
  300-word / 5-reference limit. Citations are pandoc keys `[@<key>]`; the
  letter has **no** `## References` section (pandoc renders it from
  `fixture_refs.bib`).
- `tests/expected_handoff.md` — the expected hand-off package contents.

Self-test procedure:

1. Treat `fixture_memo.md` as the memo and `fixture_target_article.md` as the
   author-placed target-article file. Treat the Step 2 quote gate as
   confirmed (the fixture marks the confirmed passages).
2. Run Steps 3–10 against the fixtures (substitute the fixture `refs.bib` for
   the live `similar_cases_search` + `citation_verify` results).
3. Diff the generated `draft.md` against `expected_draft.md` and the hand-off
   against `expected_handoff.md`.

Pass criteria:

- The letter has exactly P1 + P2 + P3, with P2 coded B1 and P3 coded S4/S1.
- Every "the authors conclude/report X" sentence maps to a verbatim quote in
  `fixture_target_article.md`.
- Every pandoc key `[@<key>]` in the letter appears in `fixture_refs.bib`
  (FP = 0 on invented citations); the letter has no `## References` section and
  no numbered citation markers.
- The letter is ≤ 300 words and cites ≤ 5 references (the fixture limits).
- `grep -c '—'` on the letter returns `0`; no banned terms; long-sentence
  ratio ≤ 15 %.
- No `[TODO: ...]` placeholders remain.

## Reference

- Spin taxonomy background: Boutron et al. 2010 (JAMA) on reporting and
  interpretation of trials with non-significant primary outcomes; Lazarus et
  al. 2015 (J Clin Epidemiol) on spin in non-randomized studies. (Verify
  exact citations via `citation_verify` before relying on them in a letter.)
- Sub-skills called, in order:
  1. [similar_cases_search](../similar_cases_search/SKILL.md),
     `background_literature` mode — Step 4 (mandatory).
  2. [citation_verify](../citation_verify/SKILL.md) — Steps 5 and 9.
  3. [letter_review_simulator](../letter_review_simulator/SKILL.md) — Step 7.
  4. `proofread-manuscript` — Step 7 (user-level skill in
     `~/.claude/skills/proofread-manuscript/`; invoke via the `Skill` tool;
     skip for Japanese letters; if not installed, fall back to the
     `style_discipline.md` self-check — see Step 7).
  5. [render_and_upload](../render_and_upload/SKILL.md): first upload after
     hand-off, recording v1 in the ledger with its Markdown snapshot.
  6. [tracked_revision](../tracked_revision/SKILL.md): co-author review round only.
- This orchestrator follows the same "Markdown is the source of truth, AI
  does partial revisions" discipline as
  [case_report_workflow](../case_report_workflow/SKILL.md), and the same
  "indicate, don't rewrite" discipline as
  [citation_verify](../citation_verify/SKILL.md). It shares
  [style_discipline.md](../case_report_workflow/style_discipline.md) rather
  than duplicating the style rules.
- Not used by this skill (case-report-specific): `deidentify_check`,
  `care_check`, `peer_review_simulator`, `bottom_line_message`,
  `submission_guidelines_check`.
