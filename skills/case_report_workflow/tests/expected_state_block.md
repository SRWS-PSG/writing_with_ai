### case-report-workflow state

| step | name | status | artifact |
|---|---|---|---|
| 1 | input collected | done | case summary (80yo daptomycin → eosinophilic pneumonia); article type = single_case |
| 2 | clinical fact ledger | done | projects/workflow_test/clinical_facts.md (9 confirmed fields; 6 unprovided fields acknowledged) |
| 3 | deidentify_check | done | no findings above surface threshold |
| 4 | similar_cases_search | done | demo/refs.bib + 2 entries (@pmid99999001, @pmid99999002) |
| 5 | background_literature_search | done | demo/refs.bib + 1 entry (@pmid99999003, review anchor) |
| 6 | citation_verify (initial) | done | found 3 / likely_wrong 0 / not_found 0 / retraction 0 |
| 7 | bottom_line_message | done | BLM finalized; 2 findings + 総合的な臨床的意義 attached; anchors and supports both present |
| 8 | submission_guidelines_check (extract) | done | rules 7 extracted; Step 9 constraint block transcribed |
| 9 | draft generated | done | projects/workflow_test/draft.md (Abstract 224 words); TODO count = 1 (consent placeholder) |
| 10 | peer_review_simulator + care_check | done | M1 / M2 / M3 / m1 accepted; C1 dismissed (next-of-kin perspective) |
| 11 | revision applied | done | Discussion: +4 sentences across 3 edits; causality softened; limitations added; Patient Consent placeholder replaced with author-confirmed wording; TODO count = 0 |
| 12 | submission_guidelines_check (compare) | done | rules 7 / pass 7 / fail 0 / unclear 0 |
| 13 | citation_verify (final) | done | found 3 / likely_wrong 0 / not_found 0 / retraction 0 |
| 14 | hand-off | done | projects/workflow_test/handoff.md |
