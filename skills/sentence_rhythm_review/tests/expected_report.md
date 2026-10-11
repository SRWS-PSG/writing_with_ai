<!-- Regression target for sentence_rhythm_review on fixture.md.
     Produced by:
       python skills/sentence_rhythm_review/scripts/sentence_stats.py \
         skills/sentence_rhythm_review/tests/fixture.md --top 3
     PASS CRITERIA are the numbers below (n / mean / max / flags / line
     numbers), not the surrounding prose. If the script's exact formatting
     changes, update this file; if the NUMBERS change, the script regressed. -->

- source: skills/sentence_rhythm_review/tests/fixture.md
- cap: 25 (default, = style_discipline.md R2)

## Auto-detection (must hold)

- Exactly THREE body paragraphs detected.
- The title block, the author/affiliation block, the `Email:`/`ORCID:` lines,
  the `## Title` / `## Acknowledgments` headings, the Funding line, and the
  Conflicts line are all SKIPPED.
- The leading HTML comment is SKIPPED and does not shift reported line numbers
  (P1 starts at line 16, the true line of the first prose paragraph).

## Distribution table (regression values)

| Para | Line | n | mean | sd   | min | max | >cap |
|------|------|---|------|------|-----|-----|------|
| P1   | 16   | 4 | 13.2 | 3.1  | 8   | 16  | 0    |
| P2   | 21   | 8 | 5.1  | 1.2  | 4   | 7   | 0    |
| P3   | 26   | 3 | 16.7 | 17.2 | 3   | 41  | 1    |

- OVERALL: n=15 sentences, mean=9.6, sd=9.3

## Longest sentences (split candidates)

- Top candidate: 41 words, P3 L26 (over cap) — the "most important caveat"
  sentence. This is the sentence a reviewer must offer to split first.

## Rhythm outliers (the core value of this skill)

- P2 flagged "uniformly short" (mean 5.1 vs 11.7 sibling avg) — the fragment
  run. Every sentence in P2 is under the 25-word cap, so a per-sentence rule
  would report nothing; only the cross-paragraph distribution surfaces it.
- P3 flagged "uniformly long" (mean 16.7 vs 11.7 sibling avg).

## Notes

- `--lines 16,21,26` reproduces the same three paragraphs explicitly and, in
  that mode, would additionally keep any single-sentence block (auto mode drops
  blocks with fewer than 2 sentences).
