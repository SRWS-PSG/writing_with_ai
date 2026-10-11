# Expected findings for fixture_draft.md

Total seeded items: **17 must-detect** + **2 should-flag (推定)** + **1 must-flag (missing)**.

Pass criteria:
- All `MUST` items detected (false negative = 0).
- `SHOULD` items flagged at least once each.
- No detection on `2020 IDSA guidelines` (guideline year, not patient date) — false positive check.
- No detection on `Day-1 (admission)` — already relative, not an absolute date.

## D1. Precise dates (MUST: 5)
1. `2024-03-15` (admission) — L9
2. `2023年4月12日` (diagnosis date) — L15
3. `March 18, 2024` (CT) — L17
4. `2024-03-25` (weaning) — L19
5. `2024年3月20日` (conference) — L25
6. `2024-04-02` (discharge) — L28

(6 dates total; all must be flagged.)

## D2. Age >89 (MUST: 1)
1. `A 92-year-old male` — L8

## D3. Place names city/prefecture/district (MUST: 3)
1. `Maebashi city` — L8
2. `Gunma prefecture` — L8
3. `Kanra district` — L15

## D4. Institution names (MUST: 2)
1. `Gunma University Hospital` — L9 (and Acknowledgements L40)
2. (Same institution; flagging the recurrence is bonus)

## D5. IDs / record numbers (MUST: 2)
1. `MRN 1234567` — L10
2. `case ID: A-22-0815` — L10

## D6. Combined rare-attribute identifier (SHOULD flag as 推定: 1)
1. Combo: rare hereditary myopathy + sericulture farmer + Kanra district + age 92 → re-identifiable. Should appear in D6 as 推定.

## D7. Family member with identifying info (MUST: 1)
1. `His wife, a 45-year-old nurse at the same hospital` — L13

## D8. Missing informed consent (MUST flag missing: 1)
1. No "informed consent" / "written consent" phrase anywhere in the draft. Must be flagged.

## D9. Figure caption identifying features (SHOULD flag: 1)
1. `star-shaped tattoo on the right shoulder` + `patient face partially included` — L33–34

## False-positive checks (MUST NOT flag)
- `2020 IDSA guidelines` (guideline reference, not patient date)
- `Day-1 (admission)` (already relative)
- `3-day history` (duration, not date)
- `45-year-old nurse` is also D7's identifier — flagging under D7 only is fine; flagging it as D2 (age) is wrong because she is <89.
