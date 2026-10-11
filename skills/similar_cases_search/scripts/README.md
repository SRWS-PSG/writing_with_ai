# scripts/ — PubMed search engine for the Writing with AI workflow

`pubmed_search.py` is the committed, reusable engine behind the
`similar_cases_search` skill (and, through it, `letter_to_editor`). It exists so
that **any** assistant — including one without a built-in web-search tool — can
produce grounded BibTeX by running a script. Stdlib only; no install.

## Two responsibilities, kept separate

| Command | Writes | Purpose |
|---|---|---|
| `search` | `<topic>.candidates.md` (**staging, not a `.bib`**) | Query PubMed from a saved search formula; surface a candidates table + verbatim quotes + BibTeX blocks for review. |
| `add` | appends to the named `refs.bib` | Promote **author-approved** PMIDs into the single render bibliography. The only command that touches a `.bib`. |

This split is deliberate: search output never becomes a stray `.bib` that could
be confused with the manuscript's render bibliography. Pandoc only ever sees the
one `refs.bib` you append to with `add`.

## Where the case-specific files live (git-ignored)

Per the repo `CLAUDE.md`, `projects/*` is git-ignored. Keep search formulas and
their outputs there so the repo stays clean:

```
projects/<name>/
  searches/<topic>.query.txt        # the search formula (input; you/AI write it)
  searches/<topic>.candidates.md    # search output (staging; NOT a .bib)
  refs.bib                          # the single render bibliography (add appends here)
```

A `.query.txt` file is plain text: the PubMed query, optionally split over
several lines, with `#` comment lines ignored. Example:

```
# P2: confounding by indication in retrospective cohort
(confounding[tiab] OR "confounding by indication"[tiab])
AND (cohort studies[mh] OR retrospective[tiab])
AND humans[mh]
```

## Usage

The NCBI contact email is **not** hardcoded (E-utilities terms require one).
Pass `--email` or set `$NCBI_EMAIL`.

```powershell
# PowerShell
$env:NCBI_EMAIL = "you@example.com"
python skills/similar_cases_search/scripts/pubmed_search.py search `
    --query-file projects/mycase/searches/confounding.query.txt `
    --max 5 --highlight confounding,indication
# -> writes projects/mycase/searches/confounding.candidates.md

# After the author approves PMIDs from the candidates file:
python skills/similar_cases_search/scripts/pubmed_search.py add `
    --pmids 12345678,23456789 `
    --bib projects/mycase/refs.bib
```

```bash
# bash
export NCBI_EMAIL=you@example.com
python skills/similar_cases_search/scripts/pubmed_search.py search \
    --query-file projects/mycase/searches/confounding.query.txt --max 5
```

### Flags

- `search`: `--query-file` | `--query`, `--max N` (default 5),
  `--mode similar_cases|background_literature`, `--highlight a,b,c`
  (bias the verbatim quote toward sentences containing these terms;
  default is the abstract's first sentence), `--out PATH`
  (default: alongside `--query-file`).
- `add`: `--pmids 1,2,3` (required), `--bib PATH` (required; appends, skips
  keys already present).
- both: `--email`, `--api-key` (or `$NCBI_EMAIL`, `$NCBI_API_KEY`).

## Discipline (matches the skill)

- Never invent metadata. Every field comes from the efetch XML of an explicit
  PMID fetched in this run; a missing field is omitted, not guessed.
- Citation key is always `pmid<PMID>`.
- `add` appends; it never overwrites and never duplicates an existing key.
