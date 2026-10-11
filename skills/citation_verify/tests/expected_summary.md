## citation-verify summary

- refs.bib: skills/citation_verify/tests/fixture_refs.bib
- report: skills/citation_verify/tests/fixture_citeguard_report.md
- entries checked: 3
- found: 1
- likely_wrong: 1
- not_found: 1
- retraction: 0

### likely_wrong (if any)

| citation key | refs.bib title | candidate title | candidate DOI |
|---|---|---|---|
| `@pmid99999002` | A case of eosinophilic pneumonia after antibiotic therapy | A case of eosinophilic pneumonia following antibiotic prophylaxis | 10.1378/chest.99999002 |

### not_found (if any)

| citation key | refs.bib DOI / PMID | likely cause |
|---|---|---|
| `@pmid99999003` | 10.9999/nonexistent.doi.xyz / 99999003 | DOI does not resolve; PMID not found in PubMed |

### Recommended action

- `likely_wrong`: Open `skills/citation_verify/tests/fixture_citeguard_report.md` to compare diffs. If the candidate is correct, re-run `similar_cases_search` for that PMID, or hand-edit `refs.bib`.
- `not_found`: Verify the DOI / PMID by hand. If the entry was hand-typed, consider re-fetching via `similar_cases_search`.

Full report: skills/citation_verify/tests/fixture_citeguard_report.md
