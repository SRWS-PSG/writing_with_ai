# Expected findings for fixture_draft.md

The fixture intentionally violates CARE 2013 across most items. The skill is
expected to mark each item with the state listed below and to name the
specific missing sub-element where applicable.

Counts seeded:
- OK items: 1
- PARTIAL items: 7
- MISSING items: 5
- MISPLACED items: 0

## C1. Title — PARTIAL
- YAML `title` and H1 are present, but neither contains the literal phrase
  "case report".
- Expected finding: title missing "case report".

## C2. Key words — PARTIAL
- YAML `keywords` has 2 entries (`myocarditis`, `young adult`) but does not
  include `case report`.
- Expected finding: case report key word missing.

## C3. Abstract — PARTIAL
- Contains diagnoses / interventions / outcomes summary but lacks (a) an
  introduction statement about uniqueness/contribution and (d) a take-away
  conclusion sentence.
- Expected finding: missing [intro] and [take-away] sub-elements.

## C4. Introduction — PARTIAL
- Section exists but contains no citation marker.
- Expected finding: missing literature citation.

## C5. Patient information — PARTIAL
- Demographics ("young adult") and primary concerns are present.
- Missing: family history, psychosocial history, past interventions, and any
  explicit medical history statement (the manuscript only says "no relevant
  past medical history" without addressing family / psychosocial).
- Expected finding: missing [family hx], [psychosocial], [past interventions].

## C6. Clinical findings — PARTIAL
- PE finding (soft S3) is present but vital signs are absent.
- Expected finding: missing vital signs.

## C7. Timeline — MISSING
- No table and no figure-based timeline. Only narrative prose.
- Expected finding: no figure/table-formatted timeline.

## C8. Diagnostic assessment — PARTIAL
- Methods (troponin, MRI) and diagnosis (myocarditis) are present.
- Missing: differential diagnoses considered, diagnostic challenges, and
  prognostic characteristics.
- Expected finding: missing [challenges], [differential], [prognosis].

## C9. Therapeutic intervention — PARTIAL
- Drugs named (bisoprolol, ACE inhibitor) without dose, route, frequency,
  or duration; no mention of changes over time.
- Expected finding: missing [administration], [changes].

## C10. Follow-up and outcomes — PARTIAL
- Clinician-assessed outcome (LVEF) and adverse events (none) are present.
- Missing: patient-assessed outcomes, follow-up diagnostic tests other than
  LVEF, and adherence/tolerability.
- Expected finding: missing [patient], [follow-up tests], [adherence].

## C11. Discussion — PARTIAL
- Limitations and a take-away are present.
- The take-away paragraph contains a citation marker `[@ref1]`, which
  violates the "no references in the take-away paragraph" rule.
- Missing: explicit strengths, broader literature discussion, rationale.
- Expected finding: take-away contains references; missing [strengths],
  [literature], [rationale].

## C12. Patient perspective — MISSING
- No patient-voice section is present.
- Expected finding: MISSING with paste-ready first-person template.

## C13. Informed consent — MISSING
- No consent statement appears anywhere.
- Expected finding: MISSING with paste-ready consent statement.

## Items expected to be OK

- None of the 13 items are seeded as fully OK in this fixture.
- (Counting rule: if any sub-element is missing the item is PARTIAL, not OK.)

## False-positive guards to verify

- YAML `title:` should count as a title block for C1 even though the body
  H1 is the same string. The skill should not flag C1 as MISSING.
- YAML `keywords:` with `[myocarditis, young adult]` should count as a key
  words block for C2 (so C2 is PARTIAL, not MISSING).
- The Discussion section ends in a paragraph beginning with "The take-away
  is…". The skill should recognise this as a take-away even though no
  explicit `## Conclusion` heading exists — but it should still flag the
  embedded citation `[@ref1]` as a violation of C11(d).
