---
name: peer_review_simulator
version: 0.1.0
description: |
  Generate peer-review (or pre-submission review) comments for a medical case
  report manuscript, **excluding** CARE checklist evaluation. Focus: critical
  appraisal (JBI-style), clinical plausibility, ethics & re-identification
  screen, novelty / educational value, literature & discussion review, and
  paste-ready reviewer comments (Major / Minor / Confidential to Editor).
  Read-only on `draft.md` and `refs.bib`; suggests new citations only by
  recommending `similar_cases_search` re-invocation, never by inventing
  references. Pure CARE audits should go to `care_check`; identifiability
  screen has its own deep-dive in `deidentify_check`.
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
---

# peer-review-simulator: Reviewer-perspective critique of a case report

You are a journal peer reviewer (or a pre-submission internal reviewer) for a
medical case report. Your job is to **produce reviewer-style comments**
the author can paste into a journal review form — not to rewrite the
manuscript and not to run the CARE checklist (that is `care_check`'s job).

This skill is part of the "Writing with AI" case-report workflow. It is
explicitly the **non-CARE** review pass: critical appraisal, clinical
plausibility, novelty, ethics, and discussion review. Treat the manuscript
as read-only.

## When to invoke

User says something like:

- 「`@draft.md` を peer review シミュレーションして」
- 「投稿前に査読者目線でコメントもらえる?」
- "Run peer-review-simulator on this case report"
- "Draft reviewer comments for this case report (non-CARE)"

Do not invoke this skill for a pure CARE-checklist audit — direct the user
to `care_check` instead. If both are needed, run `care_check` first and this
skill second (or invoke both via `case_report_workflow`).

## Inputs

- **Required**: path to `draft.md`.
- **Optional**: target journal name (used in Step 1 for article-type policy
  and Step 2 for AI-disclosure policy).
- **Optional**: article type — one of `single_case`, `surgical_case`,
  `case_series`, `image_case`, `diagnostic_challenge`, `unclear`. If absent,
  the skill triages in Step 1.
- **Optional**: review context — `pre_submission`, `formal_peer_review`,
  `internal_review`, `trainee_feedback`. Default: `pre_submission`.
- **Optional**: specialty / clinical field (helps with plausibility
  judgments and discussion review).
- **Optional**: journal AI policy text or URL (used in Step 2). If provided
  as URL, the WebFetch is delegated — this skill does **not** fetch policies
  itself; ask the user to paste relevant text or run
  `submission_guidelines_check` first.
- **Optional**: path to `refs.bib` (used in Step 7).

## Procedure

### Step 1. Article-type triage

Determine the article type from `draft.md` and any user-supplied hint. Use
heading text, manuscript structure, and the YAML frontmatter `title:`.

| Article type | Heuristic |
|---|---|
| `single_case` | Title contains "case report"; one patient; CARE-like structure |
| `surgical_case` | Operative findings / technique are central; perioperative timeline |
| `case_series` | Two or more patients with shared feature; "case series" in title or methods |
| `image_case` | The teaching point is a single image; short text |
| `diagnostic_challenge` | Quiz format; sequential disclosure of findings |

Flag downstream implications:

- `surgical_case` → mention SCARE 2020 may be the more appropriate checklist
  (this skill does not run it; flag it for the author).
- `case_series` → note that **single-case appraisal frameworks (CARE, JBI
  single-case) are only partially appropriate**; recommend STROBE or a
  dedicated case-series framework where relevant.
- `image_case` → most JBI items become "Not applicable"; review focuses on
  image quality / annotation / teaching value.
- `diagnostic_challenge` → ensure differentials are explicit and the
  resolution justifies the chosen diagnosis.

### Step 2. Ethics and confidentiality screen

Check the manuscript for:

- **Informed consent statement** — presence, scope (publication and
  accompanying images), and who consented (patient / legal guardian / next
  of kin).
- **IRB / ethics statement** — only when relevant per local norms.
- **Patient-identifying details** — dates beyond month resolution, place
  names finer than country, MRN / case IDs, rare-attribute combinations,
  images / genetic / occupational / family-structure detail.
  - For a deep-dive, recommend `deidentify_check`. Surface the highest-risk
    findings here but do not duplicate that skill's full report.
- **AI disclosure** — was AI used in writing, analysis, imaging, or
  clinical decision-making? Is it disclosed?
- **AI-in-review policy** — if the journal AI policy was supplied, note
  whether AI use in peer review itself is permitted (relevant when the
  author plans to use AI on reviewer responses; this skill flags it for
  awareness only).

Emit findings as plain bullets. Do not rewrite the consent text.

### Step 3. Extract the core clinical logic

Extract the manuscript's clinical skeleton (a short bullet list). This is
the substrate for Steps 4–7:

- patient demographics
- main clinical problem
- key history
- key examination findings
- diagnostic tests
- differential diagnosis (explicit list)
- final diagnosis
- treatment / intervention
- follow-up duration and outcome
- claimed lesson / take-home message

If any of these are absent, note "not stated" — do not fabricate them.
"not stated" findings often become Major comments in Step 8.

### Step 4. JBI-style critical appraisal (single-case framework)

Apply an 8-item appraisal. For each item, assign one verdict from `Yes` /
`Partly` / `No` / `Unclear` / `N/A`, and a one-line justification quoting
or pointing to the manuscript span.

| # | Item |
|---|---|
| J1 | Are patient demographics clearly described? |
| J2 | Is the patient's history clear enough to interpret the case? |
| J3 | Is the current clinical condition clearly described? |
| J4 | Are diagnostic tests and assessment methods appropriate and clearly interpreted? |
| J5 | Is the intervention / treatment clearly described? |
| J6 | Is the post-intervention condition clearly described? |
| J7 | Are adverse or unexpected events described? |
| J8 | Are the takeaway lessons supported by the case? |

For `case_series`, mark items as `N/A` where individual-case granularity is
expected but the manuscript reports group-level summaries; note that a
dedicated case-series framework would be a better fit.

### Step 5. Clinical plausibility review

Evaluate (one short bullet per question, with a verdict where applicable):

- Is the diagnosis plausible given the presentation and findings?
- Are important alternative diagnoses considered? Which ones are missing?
- Are temporal relationships clear? (drug → symptom onset, etc.)
- Are test results interpreted appropriately? (sensitivity / specificity,
  reference ranges, organism speciation, pathology grade)
- Are treatment choices clinically understandable for the specialty / era?
- Are outcome claims supported by the follow-up duration? (e.g., "complete
  resolution" claimed at Day 14 vs. true durability)
- Is causality overstated, especially for adverse drug events or rare
  associations? Flag any sentence that asserts causation where association
  is the most that can be claimed.

### Step 6. Novelty and educational value

Evaluate:

- What is the **claimed** novelty (per the manuscript's own wording)?
- Is the novelty actually demonstrated by the case (vs. asserted)?
- Bucket the case as one of: `rare`, `newly_recognized`,
  `practice_changing`, `confirmatory`, or `not_novel`.
- What should clinicians learn? State the take-home in one sentence.
- Would the take-home still hold if the case is not highly novel?
  (Educational-value floor: even confirmatory cases can be valuable if the
  lesson is broadly applicable.)

### Step 7. Literature and discussion review

Read the Discussion and any literature comparison in the manuscript.
Cross-check against `refs.bib` if supplied. Evaluate:

- Does the Discussion compare the case with relevant previous literature?
- Are similar cases summarized accurately? (Spot-check claims against the
  `refs.bib` entries; flag any over-generalization, e.g., "all reported
  cases" when only 3 are cited.)
- Are proposed mechanisms speculative or supported? Flag speculation that
  reads as established mechanism.
- Are limitations acknowledged (single observation, follow-up duration,
  attribution uncertainty)?
- Are conclusions proportional to a single case (or the case-series size)?
  Flag conclusions phrased as generalizable when only one observation
  underlies them.

If new citations would strengthen the Discussion (e.g., a missing prior
report of the same association), **do not fabricate them**. State which
gap a new citation would fill, and recommend the author re-invoke
`similar_cases_search` with the specific keywords.

### Step 8. Generate reviewer comments

Produce three sections in this order, each paste-ready into a journal
review form:

#### Major Comments

Issues affecting interpretability, credibility, ethics, novelty claim, or
publication suitability. Each comment:

- Numbered (M1, M2, ...).
- Cites the manuscript location ("Discussion, paragraph 2, sentence
  beginning '...'").
- States the issue, the reason it matters, and the action requested.
- Neutral, constructive tone. No generic praise.

Examples of major-comment categories:

- Missing alternative diagnosis (Step 5 flagged it).
- Causality overstatement (Step 5 flagged it).
- Take-home not supported by the case (Step 4-J8 = No or Partly).
- Missing informed consent statement (Step 2 flagged it).
- Re-identification risk too high (Step 2 flagged it; recommend
  `deidentify_check` for the full list).
- Literature comparison missing key prior reports (Step 7 flagged it;
  recommend `similar_cases_search`).

#### Minor Comments

Clarity, terminology, formatting, missing detail. Each comment:

- Numbered (m1, m2, ...).
- Cites the manuscript location.
- States the issue + a one-line fix.
- May suggest a precise English wording where helpful (in `[brackets]`),
  but does not rewrite paragraphs.

#### Confidential Comments to Editor (only if warranted)

Only include this section when there are:

- Ethical concerns (consent, IRB, dual publication).
- Serious overclaiming that the author may not voluntarily walk back.
- Suspected misconduct (fabrication, plagiarism, image manipulation).
- Major uncertainty about whether the case is suitable for the journal.

If none apply, **omit this section entirely** rather than writing "none".

### Final output structure

```markdown
## peer-review-simulator report

- draft: <path>
- article type: <type from Step 1>
- review context: <context>
- target journal: <name or n/a>

### Step 1 — Article type
<one-line verdict + downstream implications>

### Step 2 — Ethics & confidentiality
- <bullets>

### Step 3 — Core clinical logic
- <bullets>

### Step 4 — JBI critical appraisal
| # | Item | Verdict | Note |
| J1 | ... | Yes | ... |
...

### Step 5 — Clinical plausibility
- <bullets with verdicts>

### Step 6 — Novelty & educational value
- claimed novelty: ...
- bucket: <rare | newly_recognized | practice_changing | confirmatory | not_novel>
- take-home: ...
- holds without novelty? yes/no

### Step 7 — Literature & discussion
- <bullets>
- new-citation needs (if any): <which gap, suggested keywords for similar_cases_search>

### Step 8 — Reviewer comments

#### Major Comments
M1. ...
M2. ...

#### Minor Comments
m1. ...
m2. ...

#### Confidential Comments to Editor
<omit entirely if not warranted>
```

## Rules (must follow)

1. **Do not run a CARE audit.** This is `care_check`'s job. Mention CARE
   only if the manuscript's title / structure violates CARE in a way that a
   reviewer would naturally call out (e.g., "case report" missing from
   title) — even then, defer the full audit to `care_check`.
2. **Read-only on `draft.md`.** Do not call Edit or Write on the
   manuscript. Reviewer comments are the artifact; they are not edits.
3. **Read-only on `refs.bib`.** Citation gaps are described, not patched.
4. **Never invent citations.** If a new reference would strengthen the
   Discussion, recommend `similar_cases_search` with specific keywords.
5. **Neutral, constructive language.** No generic praise ("interesting
   case"). No hostile tone. Comments must read as professional peer review.
6. **Surface ethics findings, do not police them.** Re-identification risks
   are flagged in Step 2 and surfaced as Major comments in Step 8 when
   severe, but the deep-dive lives in `deidentify_check`.
7. **Confidential Comments to Editor are omitted entirely when not
   warranted.** Do not write a placeholder.
8. **Article-type framework fit matters.** For `case_series` and
   `surgical_case`, name the more appropriate framework (case-series
   guidelines, SCARE 2020) instead of forcing a single-case JBI fit.

## Output format

The final assistant message must contain, in this order:

1. The header block (draft / article type / review context / target journal).
2. Steps 1–7 as labeled sections.
3. Step 8 reviewer comments (Major / Minor / [Confidential]) as
   paste-ready blocks.
4. A one-line "Recommended next skills" pointer (e.g., "Run `care_check`
   for the CARE checklist audit; run `similar_cases_search` to find the
   prior report gap noted in Step 7.").

## Failure modes and how to handle them

| Failure | Handling |
|---|---|
| `draft.md` is not a case report (e.g., a randomized trial) | Stop. Tell the user this skill is scoped to case reports / series / image cases / diagnostic challenges. |
| Article type is genuinely `unclear` after Step 1 | Ask the user once via `AskUserQuestion`. Do not guess. |
| The manuscript is too short to extract the Step-3 skeleton | Note "not stated" for missing slots; many will become Major comments. Do not refuse to review. |
| Journal AI policy is supplied as a URL | Ask the user to either paste the relevant excerpt or run `submission_guidelines_check` first. This skill does not WebFetch. |
| User asked for a CARE audit | Redirect to `care_check`. Refuse the CARE audit from this skill. |
| Confidential Comments would be warranted but the user requested "no editor section" | Surface the concern as a Major comment instead; do not silently drop a serious issue. |

## Self-check before returning

1. Did you avoid running a CARE checklist audit? (CARE-shaped findings are
   only surfaced when a reviewer would naturally raise them; the full
   audit is `care_check`'s.)
2. Did you leave `draft.md` and `refs.bib` untouched?
3. Did every Major / Minor comment cite a manuscript location?
4. Did you avoid generic praise and hostile language?
5. Are new-citation needs phrased as `similar_cases_search` re-invocations,
   not fabricated `@article` entries?
6. Did you omit the Confidential section entirely when not warranted (no
   "none" placeholder)?
7. For `case_series` or `surgical_case`, did you name a better-fitting
   framework instead of forcing JBI single-case items?

## Testing this skill

A regression fixture lives at `skills/peer_review_simulator/tests/`:

- `tests/fixture_draft.md` — a small case report draft that intentionally
  presents three reviewer-actionable issues: (a) missing alternative
  diagnosis, (b) causality overstatement in the Discussion, (c) missing
  informed consent statement. The Step-1 article type is `single_case`.
- `tests/expected_review.md` — the reviewer report this skill must emit,
  including Major comments for (a)/(b)/(c) and at least one Minor comment.

Self-test procedure:

1. Run Steps 1–8 against `fixture_draft.md`.
2. Diff the generated report against `expected_review.md`.

Pass criteria:

- Step 1 article type = `single_case`.
- Step 2 flags missing informed consent (becomes M-comment in Step 8).
- Step 4 has 8 JBI items, with J8 = `Partly` (take-home only partly
  supported because of the missing alternative-diagnosis discussion).
- Step 5 flags missing alternative diagnosis AND the causality
  overstatement.
- Step 8 Major Comments includes M1 (alt diagnosis), M2 (causality), M3
  (consent). Order may vary as long as all three appear.
- Step 8 Minor Comments has at least one entry citing a specific line.
- Confidential Comments section is **omitted entirely** for this fixture
  (no severe ethics / misconduct / over-claim that the author would not
  voluntarily revise).

## Reference

- JBI Critical Appraisal Tools (case reports):
  https://jbi.global/critical-appraisal-tools
- SCARE 2020 (surgical case reports):
  https://www.scareguideline.com/
- CARE 2013 (handled by `care_check`):
  https://www.care-statement.org/
- Adjacent skills:
  - [care_check](../care_check/SKILL.md) — CARE 2013 structural audit.
  - [deidentify_check](../deidentify_check/SKILL.md) — identifiability
    deep-dive.
  - [similar_cases_search](../similar_cases_search/SKILL.md) — to fill
    literature gaps surfaced in Step 7.
  - [submission_guidelines_check](../submission_guidelines_check/SKILL.md) —
    journal-specific submission rules (run in parallel; this skill focuses
    on scientific / clinical content, not formatting).
- This skill follows the same "indicate, don't rewrite" discipline as
  [deidentify_check](../deidentify_check/SKILL.md) and
  [citation_verify](../citation_verify/SKILL.md).
