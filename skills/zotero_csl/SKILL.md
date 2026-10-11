---
name: zotero_csl
version: 0.1.0
description: |
  Make the references of a manuscript follow the target journal's citation
  format. Given a journal name, find that journal's CSL style in the Zotero
  Style Repository, save it into the manuscript folder
  (`projects/<name>/styles/`), and tell the author the exact `--csl` path to
  give pandoc. Handles the citation FORMAT only: it never creates, edits, or
  exports references, never touches `refs.bib`, and never writes or edits CSL
  XML by hand. Dependent styles (tiny files that only point to a parent style)
  are saved together with their parent, and pandoc is pointed at the parent so
  rendering does not depend on the network. Trigger phrases:
  「JCE の形式にして」「投稿先の引用スタイルにして」「CSL を取ってきて」
  「Zotero のスタイルを使って」「引用の体裁を投稿規定に合わせて」.
allowed-tools:
  - Read
  - Bash
  - AskUserQuestion
---

# zotero_csl: Fetch the target journal's CSL style from the Zotero Style Repository

You fetch a citation STYLE file (CSL) and wire it into the author's pandoc
command. You do not touch the references themselves.

This skill is NOT for:

- Creating, completing, or checking references (`refs.bib` entries) → use
  `similar_cases_search` (add entries) and `citation_verify` (check entries).
- Extracting a journal's other rules (word limits, section structure, number of
  references) → use `submission_guidelines_check`.

## When to invoke

User says something like:

- 「Journal of Clinical Epidemiology の形式にして」「JCE の形式にして」
- 「投稿先の引用スタイルにして」「引用の体裁を投稿規定に合わせて」
- 「CSL を取ってきて」「Zotero のスタイルを使って」
- "Format the references for <journal>"

## Inputs

- **Required**: the manuscript folder: `projects/<name>/`, or `demo/` for
  practice. If unknown, ask.
- **Required**: the target journal name (or a style name such as Vancouver /
  AMA). If unknown, ask.
- **Optional**: the Markdown file to render (default: the `draft.md` in the
  manuscript folder).

## Dependency

Python 3 (standard library only). Network access to `www.zotero.org` is needed
unless the author supplies local copies (`--index-file`, `--source-dir`). The
script only issues GET requests to
`https://www.zotero.org/styles-files/styles.json` and
`https://www.zotero.org/styles/<id>`.

## Procedure

### 1. Identify the manuscript folder and the journal

Confirm both. If either is missing, ask once.

The style index holds full journal titles and style ids, not abbreviations: a
search for "jce" returns no match. When the author gives an abbreviation (JCE,
NEJM, ...), expand it to the full journal title, say which title you expanded it
to, and search for that. If you are not sure of the expansion, ask.

### 2. Search

```bash
python skills/zotero_csl/scripts/fetch_csl.py search --query "<journal name>"
```

Each output line is `id`, title, `dependent` / `independent`, and the style's
`updated` date. The search matches both the title and the style id.

- **One exact hit**: proceed.
- **Several plausible hits** (for example "BMJ" vs "BMJ Open", or variants such
  as `...-brackets`): show the candidates and let the author choose
  (`AskUserQuestion`). Never pick silently.
- **Zero hits** (`no match for "..." in N styles`): say so. Do not hand-write or
  hand-edit a CSL file, and do not substitute a "close" journal. Suggest
  checking the journal's author guidelines for the named reference style
  (Vancouver, AMA, ...) and searching for that style name instead.
- **Error** (`error: ...` on stderr, non-zero exit): report it verbatim. A
  failure is not "no match".

### 3. Get

```bash
python skills/zotero_csl/scripts/fetch_csl.py get --id <style-id> --dest <manuscript folder>/styles
```

The script validates the id, downloads the style, and saves it byte-for-byte.
If a different file with the same name already exists it stops and names the
file; add `--force` only after the author agrees to overwrite.

Exit code 3 means the style id does not exist in the repository.

### 4. Report the pandoc path and command

Quote the script's `use with pandoc: --csl <path>` line, then show the render
command in this repository's usual shape:

```bash
pandoc <draft>.md --citeproc --bibliography refs.bib --csl styles/<use_csl> -o output/<draft>.docx
```

Add `--reference-doc` when the project already uses one.

If the Markdown has a `csl:` line in its YAML front matter (as `demo/draft.md`
does), tell the author that line must be updated to the same path too, and offer
to change that one line. Do not edit any other part of the manuscript.

### 5. Render once and ask for a check

Render once. Then tell the author to compare the reference list with the
journal's author guidelines: the Zotero repository is community-maintained, the
file's `updated` date is shown in the search output, and a style can lag behind
a journal's current rules.

## Dependent styles

A dependent style is a tiny CSL file with no `<citation>` element that only
points to a parent style (`independent-parent` link). pandoc given such a file
silently downloads the parent at render time, so rendering works online and
breaks offline or when the parent changes. For that reason `get` saves both the
dependent file and the parent, and `use with pandoc` names the parent file.
`csl_source.json` in the destination folder records, for every requested style,
the title, whether it is dependent, the parent, the file to give pandoc, the
source URLs, the SHA-256 of each file, and the fetch time.

## Getting references out of Zotero (explanation only; this skill does not run it)

The author, not this skill, puts references into `refs.bib`:

- Export by hand: right-click the Zotero collection → Export → BibTeX → save as
  `projects/<name>/refs.bib`.
- Or install the Better BibTeX plugin and use "Keep updated" (auto-export) on
  the collection, targeting `projects/<name>/refs.bib`. The `.bib` file then
  follows the Zotero collection.

See `tutorials/citation_management.md` (section "Zoteroからのエクスポート").
This skill never writes to `refs.bib`.

## Rules (must follow)

1. **Read-only on `refs.bib` and on manuscript prose.** The only manuscript edit
   allowed is the single `csl:` line in the YAML front matter, and only after the
   author agrees.
2. **Never author or modify CSL XML.** Files come from the script, byte-for-byte.
3. **Never choose among multiple candidates silently.** Show them and ask.
4. **Never report success without the `use with pandoc` line** printed by the
   script.
5. **A search failure is not an empty result.** Distinguish
   `no match for ...` (exit 0) from `error: ...` (non-zero).

## Output format

The final message contains, in order:

1. The commands actually run.
2. The script's `style:`, `dependent:`, `saved:` and `use with pandoc:` lines.
3. The pandoc command to use, and the `csl:` front-matter line if one exists.
4. The reminder to check the reference list against the journal's guidelines,
   including the style's `updated` date.

## Failure modes and how to handle them

| Failure | Handling |
|---|---|
| Zero search matches | Report it; suggest searching by style name; do not write a CSL. |
| Several candidates | Show them; ask the author to choose. |
| `error: ...` on search / get | Report verbatim; no retry beyond the script's own. |
| Exit 3 on `get` | The style id does not exist; search again. |
| Existing different file in `styles/` | The script refuses; ask before `--force`. |
| Parent style missing, itself dependent, or lacking `<citation>` | The script errors; report it, do not patch. |

## Testing this skill

```bash
python -m pytest skills/zotero_csl -q
```

The tests are offline. They use `tests/fixtures/` (a 9-entry sample of the style
index plus verbatim copies of `journal-of-clinical-epidemiology.csl` and
`elsevier-vancouver.csl`) and an injected fake fetch function. They cover:
search ranking and id matching, zero-match vs failure, saving dependent and
independent styles, `csl_source.json` contents and preservation, idempotent
reruns and `--force`, id validation, 404 / 5xx / bad-body retry behavior, and
the dependent-parent chain error. One pandoc test (skipped when pandoc is not
installed) renders `tests/fixture_draft.md` with the AMA and Vancouver styles and
checks the outputs differ. A live check against zotero.org is not part of the
test suite.
