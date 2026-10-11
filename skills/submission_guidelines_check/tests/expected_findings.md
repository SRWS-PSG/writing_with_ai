## submission-guidelines-check report

- target journal: Journal of Imaginary Case Medicine (fixture)
- guideline source: skills/submission_guidelines_check/tests/fixture_guidelines.md (fixture mode)
- draft: skills/submission_guidelines_check/tests/fixture_draft.md
- refs.bib: n/a (not supplied in fixture)

### Rule table (extracted from guidelines)

| rule_id | category | rule | source span |
|---|---|---|---|
| SG1.1 | word_count | Abstract must not exceed 250 words. | "## Abstract" → "Abstract must not exceed 250 words." |
| SG2.1 | sections | Body sections required, in order: Introduction, Case Presentation, Discussion, Conclusion. | "## Body sections (required, in this order)" |
| SG3.1 | figures_tables | Maximum 5 figures + tables combined. | "## Figures and tables" |
| SG4.1 | citations | Vancouver style; CSL = `vancouver.csl`. | "## References and citation style" |
| SG5.1 | consent | A patient consent statement must appear in the manuscript, in a Patient Consent section after References. | "## Patient consent" |
| SG10.1 | title | Title must contain the phrase "case report" (any capitalization); ≤150 characters. | "## Title" |
| SG11.1 | ai_disclosure | If any generative-AI tool contributed to writing/editing/figures, disclose in a dedicated "AI Disclosure" subsection with tool name, version, and scope. | "## Generative-AI disclosure" |

### Summary

- rules checked: 7
- pass: 4
- fail: 3
- unclear: 0

### Findings (fail / unclear only)

#### SG1.1 — Abstract word count (fail)

- Rule (source quote): "Abstract must not exceed 250 words."
- Source: skills/submission_guidelines_check/tests/fixture_guidelines.md
- Observed in draft.md: Abstract body is 256 words (counted by `wc -w` on the section body, headings excluded, single paragraph at line 11 of `fixture_draft.md`).
- Suggested action: trim ~6 words. Likely candidates: the closing sentence ("This abstract intentionally extends beyond the journal limit ...") is meta-commentary that does not belong in a published abstract; removing it alone clears the limit.

#### SG5.1 — Patient consent statement (fail)

- Rule (source quote): "Written informed consent must be obtained from the patient (or the patient's legal guardian / next of kin) for publication of the case report and any accompanying images. A statement to this effect must appear in the manuscript, in the Patient Consent section after References."
- Source: skills/submission_guidelines_check/tests/fixture_guidelines.md
- Observed in draft.md: no Patient Consent section detected after References (searched for the headings "Patient Consent" / "Consent" / "Informed consent" and for the keyword "consent" in body text).
- Suggested action: add a "# Patient Consent" section between Funding and the end of the manuscript with a sentence such as: "Written informed consent was obtained from the patient for publication of this case report and any accompanying images."

#### SG11.1 — Generative-AI disclosure (fail)

- Rule (source quote): "If any generative-AI tool (e.g., ChatGPT, Claude, Gemini) contributed to manuscript writing, editing, or figure generation, this must be disclosed in a dedicated 'AI Disclosure' subsection at the end of the manuscript, with the tool name, version, and the scope of its use."
- Source: skills/submission_guidelines_check/tests/fixture_guidelines.md
- Observed in draft.md: no "AI Disclosure" subsection detected (searched headings for "AI" / "generative" / "ChatGPT" / "Claude" / "Gemini").
- Suggested action: add a "# AI Disclosure" subsection at the end of the manuscript. If AI was not used, state that explicitly; if it was, name the tool, version, and the scope (e.g., "Antigravity 1.x with Claude Opus 4.7 was used to assist in language editing of Discussion. All content was reviewed and verified by the authors.").

### Passing checks

- SG2.1 — required sections present in correct order (Introduction, Case Presentation, Discussion, Conclusion): pass.
- SG3.1 — figure + table count ≤ 5 (none embedded in fixture_draft.md): pass.
- SG4.1 — CSL declared as `styles/vancouver.csl`, matching the journal-required Vancouver style: pass.
- SG10.1 — title contains "case report" and is ≤150 characters: pass.

### Open questions for the author

- (none — no rules verdicted `unclear` in this fixture)

### Next action

Address SG1.1, SG5.1, and SG11.1 before submitting; re-run this skill after revision to confirm the three failures clear.
