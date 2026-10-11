# citeguard report (frozen fixture)

Generated against `skills/citation_verify/tests/fixture_refs.bib` for
regression testing. This file is **not** real citeguard output; it is a
hand-written stand-in shaped like real citeguard output so the citation_verify
skill's parsing/summarization logic can be tested offline.

When a future citeguard version changes its report schema, update this fixture
and `expected_summary.md` together.

---

## Entry 1: @pmid99999001

- status: found
- refs.bib title: Daptomycin-induced eosinophilic pneumonia: a case report
- candidate title: Daptomycin-induced eosinophilic pneumonia: a case report
- candidate doi: 10.1136/bcr-2020-240123
- candidate source: PubMed (PMID 99999001)
- retraction: false
- title similarity: 1.00
- author overlap: 1.00
- year match: true

## Entry 2: @pmid99999002

- status: likely_wrong
- refs.bib title: A case of eosinophilic pneumonia after antibiotic therapy
- candidate title: A case of eosinophilic pneumonia following antibiotic prophylaxis
- candidate doi: 10.1378/chest.99999002
- candidate source: Crossref
- retraction: false
- title similarity: 0.62
- author overlap: 0.50
- year match: true
- note: title diverges materially; author should review

## Entry 3: @pmid99999003

- status: not_found
- refs.bib title: Hand-typed entry with a typo in the DOI
- refs.bib doi: 10.9999/nonexistent.doi.xyz
- refs.bib pmid: 99999003
- candidate: none
- probable cause: DOI does not resolve; PMID not found in PubMed
- retraction: n/a
