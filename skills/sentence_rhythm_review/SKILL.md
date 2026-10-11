---
name: sentence_rhythm_review
version: 0.1.0
description: |
  Measure the SENTENCE-LENGTH DISTRIBUTION of a Markdown manuscript and
  diagnose its rhythm. For every body paragraph it computes each sentence's
  word count (citations, `et al`, and decimals excluded), then reports three
  things: (1) the per-paragraph distribution (n / mean / SD / min / max /
  count over the cap), (2) the longest-N sentences as concrete SPLIT
  candidates, and (3) rhythm outliers — paragraphs whose mean length is far
  from their siblings (uniformly choppy fragment-runs, or uniformly heavy
  long-sentence blocks) that a single-sentence rule can never catch. Then it
  proposes concrete split / merge edits and, on request, applies them. This is
  a MEASUREMENT + diagnosis tool; it does not own the sentence-length rule.
  The "<= 25 words, hard cap 25" rule is R2 in
  case_report_workflow/style_discipline.md — this skill operationalizes R2 and
  adds the cross-paragraph rhythm dimension.
  Triggers: 「文の長さの分布」「センテンスの語数を見たい」「文長の分布」
  「リズムを見て」「一文が長い箇所」「段落ごとの文の長さ」「sentence length
  distribution」「sentence rhythm」「split long sentences」.
  NOT for the style RULE set (em-dash, banned terms, active voice, citation
  form → proofread-manuscript / style_discipline.md R2), NOT for paragraph
  LOGIC / ordering (→ argument_logic_review), NOT for AI-style fingerprints
  (→ humanizer_academic), NOT for scientific validity / spin
  (→ peer_review_simulator / letter_review_simulator).
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - AskUserQuestion
---

# sentence-rhythm-review: sentence-length distribution and rhythm diagnosis

You measure how long each sentence is, paragraph by paragraph, and turn the
numbers into concrete edits. You judge *rhythm and length*, not truth, logic,
or style rules. Four sibling concerns are out of scope and belong elsewhere:

- **Style RULES** (em-dash ban, banned terms, active voice, `<= 25` word cap,
  citation form) → `proofread-manuscript`; the cap itself is **R2** in
  `case_report_workflow/style_discipline.md`. Do not restate or re-derive the
  rule here — cite it.
- **Paragraph logic / ordering / topic sentences** → `argument_logic_review`.
- **AI-style fingerprints** → `humanizer_academic`.
- **Scientific validity / fairness / spin** → `peer_review_simulator` /
  `letter_review_simulator`.

## Why this exists

Summary readability scores and the `<= 25` word rule both look at sentences one
at a time. They miss two things an author actually feels while reading:

1. **A single long sentence** buried in an otherwise tight paragraph — the
   split candidate.
2. **A whole paragraph whose rhythm is out of step with its neighbors** — e.g.
   one paragraph written in uniformly short 5–10 word fragments while the rest
   average ~15. Every sentence "passes" the `<= 25` rule, yet the paragraph
   reads as monotonous or choppy. Only a *distribution across paragraphs*
   surfaces this.

## Workflow

1. **Locate the manuscript.** Confirm the Markdown file (usually
   `projects/<name>/manuscript.md`). Markdown is the source of truth.

2. **Run the script** (do not re-implement the counting in your head):

   ```powershell
   python writing_with_AI/skills/sentence_rhythm_review/scripts/sentence_stats.py `
     "projects/<name>/manuscript.md" --top 6
   ```

   Useful flags:
   - `--cap 25` — word cap for flagging split candidates (default 25 = R2).
   - `--min-words 40` — minimum block size to count as a prose paragraph;
     lower it if short paragraphs are being skipped.
   - `--lines 18,20,22` — analyze only the blocks starting at these 1-indexed
     lines, bypassing auto-detection (use when auto-detect misses/adds a block).
   - `--top N` — how many longest sentences to list.
   - `--json` — machine-readable output.

   Auto mode analyzes multi-sentence prose blocks only. It skips headings,
   lists, tables, title/affiliation blocks, and non-prose sections
   (Acknowledgments, References, Funding, Conflicts, Data availability, etc.).

3. **Present the distribution table** to the author (Para / line / n / mean /
   SD / min / max / >cap / counts) plus the overall mean and SD. Report the
   whole picture; do not silently drop paragraphs.

4. **Interpret — three lenses:**
   - **Split candidates:** every sentence over `--cap`. The longest one is the
     first target. Parenthetical numbers and colons inflate counts, so read the
     sentence before proposing a split.
   - **Rhythm outliers:** any paragraph the script flags (mean >= 1 SD from the
     sibling mean-of-means). "Uniformly short" = possible fragment-run /
     monotony; "uniformly long" = possible heaviness. Confirm by eye — a short
     staccato run can be intentional at a rhetorical climax; keep those.
   - **Convergence goal:** after edits, paragraph means should sit in a
     comparable band and no single sentence should dominate.

5. **Propose concrete edits, do not auto-apply.** For each target show
   `current -> proposed` with the new word counts, preserving meaning,
   citations, active voice, and the em-dash ban (per style_discipline.md).
   - **Long sentence** -> split at a natural clause boundary (a semicolon, a
     colon, or a causal "because/so" hinge), keeping each half a full sentence.
   - **Fragment-run paragraph** -> merge adjacent 5–8 word fragments at their
     logical seams, but leave intentional short lines (e.g. a closing punch).
   Get author approval, then apply with `Edit`. Re-run the script to confirm
   the distribution converged.

6. **Never invent content or citations.** Splitting and merging only
   redistributes existing words. If a split needs a new connective, keep it to
   a functional word ("Because of that", "They", "Both"), never a new claim.

## Output

- A distribution table + overall mean/SD (Japanese narration around it).
- A ranked split-candidate list.
- Rhythm-outlier flags with a one-line reason each.
- `current -> proposed` edit proposals for the flagged sentences/paragraphs.
- After approval: applied edits + a re-run confirming convergence.

Keep the source read-first: only `Edit` the manuscript after the author
approves the specific proposals.
