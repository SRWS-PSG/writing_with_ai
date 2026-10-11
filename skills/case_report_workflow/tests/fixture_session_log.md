# case-report-workflow session transcript (FIXTURE)

> Frozen "transcript" used by `skills/case_report_workflow/tests/`. It stands
> in for the live sub-skill invocations so the orchestrator's
> state-tracking / aggregation / hand-off logic can be tested offline.
>
> Each section is labeled with the step number and the sub-skill that
> produced it. Edit this file only in tandem with `expected_state_block.md`
> and `expected_handoff.md`.

---

## Step 1 — Input collected

- mode: case summary (no pre-existing draft)
- author-supplied summary: 80-year-old man on intravenous daptomycin for a
  deep-seated soft tissue infection developed dyspnea, bilateral peripheral
  consolidation, and 42% BAL eosinophils on Day 12; recovered after
  daptomycin discontinuation and prednisolone 0.5 mg/kg/day.
- author confirmed synopsis accurate: yes
- article type (declared): `single_case`

## Step 2 — Clinical fact ledger

Ledger written to `projects/workflow_test/clinical_facts.md`.

| field | value | source |
|---|---|---|
| patient sex | male | Step 1 summary |
| patient age band | 80 years (80s) | Step 1 summary |
| primary indication for daptomycin | deep-seated soft tissue infection | Step 1 summary |
| daptomycin route | intravenous | Step 1 summary |
| Day 0 anchor | start of daptomycin therapy | Step 1 summary |
| Day 12 events | dyspnea, bilateral peripheral consolidation on imaging, BAL with 42% eosinophils | Step 1 summary |
| BAL eosinophil percentage | 42% | Step 1 summary |
| intervention | daptomycin discontinuation + prednisolone 0.5 mg/kg/day | Step 1 summary |
| outcome | recovered | Step 1 summary |

Unprovided fields the author chose to leave empty (will become
`[TODO: author to confirm <field>]` if needed in Step 9):

- relevant comorbidities and current medications
- vital signs at presentation
- microbiology / pathology results for the soft tissue infection
- Day 23 follow-up clinical status detail
- patient perspective / quality of life
- duration of follow-up beyond Day 23

Author confirmed the ledger is faithful: yes.

## Step 3 — Deidentify check (from deidentify_check)

Findings: none above the surface threshold. The summary uses relative day
numbering (Day 0 / Day 12 / Day 13 / Day 23), no place names, no MRN, no
named institution. Age (80) is below the >89 threshold.

Author choice: proceed without additional de-identification edits.

## Step 4 — Similar cases search (from similar_cases_search, mode=similar_cases)

NCBI email collected: workflow-test@example.com

Query executed:
`(daptomycin[mh] OR daptomycin[tiab]) AND (eosinophilic pneumonia[mh] OR eosinophilic pneumonia[tiab]) AND "case reports"[pt] AND humans[mh]`

Candidates approved (2 of 5 shown):
- @pmid99999001 — Daptomycin-induced eosinophilic pneumonia: a case report (BMJ Case Reports, 2021)
- @pmid99999002 — A case of eosinophilic pneumonia after antibiotic therapy (Chest, 2019)

Both entries appended to `demo/refs.bib`.

## Step 5 — Background literature search (from similar_cases_search, mode=background_literature)

Query executed:
`(daptomycin[mh] OR daptomycin[tiab]) AND (adverse effects[mh] OR safety[tiab] OR pulmonary toxicity[tiab]) AND (review[pt] OR "systematic review"[pt] OR meta-analysis[pt] OR guideline[pt]) AND humans[mh]`

Candidates approved (1 of 3 shown):
- @pmid99999003 — Daptomycin safety profile: a systematic review (Clin Infect Dis, 2020, review)

Entry appended to `demo/refs.bib`. Now serves as the typical-presentation
anchor for `bottom_line_message` Phase 2.

## Step 6 — Citation verify (initial pass, from citation_verify)

```
## citation-verify summary
- refs.bib: demo/refs.bib
- report: /tmp/citation_report.md
- entries checked: 3
- found: 3
- likely_wrong: 0
- not_found: 0
- retraction: 0
```

No `likely_wrong` / `not_found` / `retraction`. Proceed.

## Step 7 — Bottom-line message (from bottom_line_message)

Two findings + BLM finalized:

- 発見 1: Drug-induced eosinophilic pneumonia from daptomycin can mimic
  progressive infection during antibiotic therapy. 出典: [pmid99999001,
  pmid99999002], anchor: [pmid99999003]
- 発見 2: BAL eosinophilia >25% with bilateral peripheral consolidation
  during daptomycin treatment supports the diagnosis and warrants drug
  withdrawal before considering steroids. 出典: [pmid99999001], anchor:
  [pmid99999003]
- 総合的な臨床的意義: New pulmonary symptoms during antibiotic therapy
  should not be reflexively attributed to infection progression;
  bronchoalveolar lavage with cell-count differential is a quick way to
  surface the alternative diagnosis.
- BLM (chosen candidate): "In an elderly patient on intravenous daptomycin
  whose pulmonary symptoms do not improve with infection-directed
  escalation, consider drug-induced eosinophilic pneumonia and obtain BAL
  cell-count differential before further antibiotic broadening."

## Step 8 — Submission guidelines check, extract_only (from submission_guidelines_check)

Target: Journal of Imaginary Case Medicine (fixture).
Mode: `extract_only` — no manuscript comparison performed.

Rules extracted (7 total): SG1.1 (abstract ≤ 250 words), SG2.1 (required
sections: Title page / Abstract / Introduction / Case Presentation /
Discussion / Conclusion), SG3.1 (figures ≤ 5), SG4.1 (Vancouver style),
SG5.1 (Patient Consent statement required), SG10.1 (title must contain
"case report"), SG11.1 (AI Disclosure required).

Step 9 generation constraints transcribed:
- Body section ordering: Introduction → Case Presentation → Discussion →
  Conclusion.
- Abstract ≤ 250 words.
- Title must contain "case report".
- CSL = `vancouver.csl`.
- Patient Consent section after References (TODO placeholder if not yet
  confirmed).
- AI Disclosure subsection at end.

## Step 9 — Draft generated

draft.md written to `projects/workflow_test/draft.md`.

Per-section word counts (body only, headings excluded):
- Abstract: 224
- Introduction: 78
- Case Presentation: 142
- Discussion: 263
- Conclusion: 41

Citations placed: @pmid99999001, @pmid99999002, @pmid99999003.
Placeholders inserted:
- `[TODO: confirm written informed consent for publication and any accompanying images — replace with the author-confirmed wording]` (Patient Consent section)

TODO count at end of Step 9: 1 (consent placeholder).

## Step 10 — Peer review + CARE (from peer_review_simulator + care_check)

Article type confirmed: `single_case` (matches Step 1).

Aggregated punch-list (de-duplicated):

| id | source | severity | item |
|---|---|---|---|
| M1 | peer_review_simulator | major | Discussion should explicitly enumerate alternative diagnoses considered (infection progression, idiopathic acute EP, parasitic eosinophilia, other concomitant drugs) and how each was excluded. |
| M2 | peer_review_simulator | major | Soften causality wording from "proves" / "mandatory" to "consistent with" / "should prompt consideration of". |
| M3 | peer_review_simulator + care_check | major | Resolve consent placeholder — confirm with author whether written informed consent has been obtained, then replace the TODO with the confirmed wording (or escalate if not yet obtained). |
| m1 | peer_review_simulator | minor | Add a limitations paragraph (no rechallenge; follow-up only 10 days post-steroid; infection workup on BAL not reported). |
| C1 | care_check | care_8 | Patient perspective sentence not present. |

Author triage:
- M1: accept.
- M2: accept.
- M3: accept (author confirms written informed consent was obtained at the
  time of discharge counseling; placeholder will be replaced with the
  canonical wording).
- m1: accept.
- C1: dismiss (reason: patient was unable to provide perspective due to
  language barrier; consent obtained via next-of-kin, which is noted in the
  Patient Consent section).

## Step 11 — Revision applied

Edits to `projects/workflow_test/draft.md`:

- Discussion paragraph 1: added a sentence enumerating the alternative
  diagnoses considered and how each was excluded (M1).
- Discussion paragraph 2: changed "proves the causal role" → "is
  consistent with a causal role"; changed Conclusion "mandatory" →
  "should prompt consideration of daptomycin withdrawal" (M2).
- Patient Consent section: replaced `[TODO: confirm written informed
  consent ...]` placeholder with the author-confirmed wording "Written
  informed consent was obtained from the patient's next of kin for
  publication of this case report and any accompanying images." (M3).
- New limitations paragraph appended to Discussion end: single
  observation, no rechallenge, 10-day post-steroid follow-up, BAL
  infection workup not reported (m1).

No new citations introduced; `similar_cases_search` was not re-invoked.
Touched sections: Discussion (3 edits), Patient Consent (1 edit).
Sentence-count change: Discussion +4 sentences; Patient Consent +0
(placeholder replaced 1:1).

TODO count after Step 11: 0.

## Step 12 — Submission guidelines check, compare (from submission_guidelines_check)

Mode: `compare`. Re-used the Step 8 rule table; applied against revised
`projects/workflow_test/draft.md`.

Findings: rules checked 7 / pass 7 / fail 0 / unclear 0.

All rules pass:
- SG1.1 — Abstract 224 ≤ 250 words: pass.
- SG2.1 — required sections present (Introduction, Case Presentation,
  Discussion, Conclusion, plus Patient Consent + AI Disclosure): pass.
- SG3.1 — 0 figures ≤ 5 cap: pass.
- SG4.1 — Vancouver CSL declared: pass.
- SG5.1 — Patient Consent statement present (confirmed wording after
  Step 11 M3 resolution): pass.
- SG10.1 — title contains "case report": pass.
- SG11.1 — AI Disclosure subsection present: pass.

## Step 13 — Citation verify (final pass, from citation_verify)

```
## citation-verify summary
- refs.bib: demo/refs.bib
- report: /tmp/citation_report_final.md
- entries checked: 3
- found: 3
- likely_wrong: 0
- not_found: 0
- retraction: 0
```

All three cited PMIDs still resolve clean. Proceed to Step 14.

## Step 14 — Hand-off

Workflow complete. Hand-off package written to
`projects/workflow_test/handoff.md` (contents in `expected_handoff.md`).
TODO count in final draft: 0 (verified before write).
