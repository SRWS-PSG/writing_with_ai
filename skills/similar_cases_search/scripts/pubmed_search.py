#!/usr/bin/env python3
"""PubMed-grounded reference search for the "Writing with AI" workflow.

This is the committed, reusable engine behind the `similar_cases_search` skill
(and, through it, `letter_to_editor`). It exists so that *any* assistant —
including ones that cannot browse the web — can produce grounded BibTeX by
running a script, instead of relying on a built-in web-search tool.

Two subcommands, deliberately separated so search output never gets mistaken
for the manuscript's render bibliography:

  search   Read a search formula (from a file under projects/<name>/searches/
           or inline), query PubMed via NCBI E-utilities, and write a
           *staging* file `<topic>.candidates.md`. This file is NOT a .bib;
           it holds a candidates table, verbatim supporting quotes, and
           BibTeX blocks inside fenced ```bibtex code blocks for review.

  add      Given approved PMIDs, fetch their records and APPEND @article
           blocks to the single render bibliography (refs.bib), skipping
           keys that already exist. This is the only command that writes a
           .bib, and it only ever appends to the one file you name.

Design rules (mirror the skill's discipline):
  * Never invent citation metadata. Every field comes from the efetch XML of
    an explicit PMID fetched in this run. Missing field -> omitted, not guessed.
  * Citation key is always `pmid<PMID>`.
  * The NCBI contact email is NOT hardcoded. Supply --email or set
    $NCBI_EMAIL. (NCBI E-utilities terms of use require a contact email.)

Stdlib only (urllib, xml.etree) so it runs anywhere Python 3 does, no install.

Examples
--------
  # 1) Save a search formula in the (git-ignored) project folder:
  #    projects/mycase/searches/confounding.query.txt
  #
  # 2) Run the search; writes projects/mycase/searches/confounding.candidates.md
  set NCBI_EMAIL=you@example.com           # PowerShell: $env:NCBI_EMAIL = "you@example.com"
  python pubmed_search.py search \
      --query-file projects/mycase/searches/confounding.query.txt \
      --max 5 --highlight confounding,indication

  # 3) After the author approves PMIDs, append them to the render bibliography:
  python pubmed_search.py add \
      --pmids 12345678,23456789 \
      --bib projects/mycase/refs.bib
"""

import argparse
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL = "writing_with_AI"


def _utf8_stdout():
    """Windows consoles default to cp932; force UTF-8 so quotes/titles survive."""
    if sys.platform.startswith("win"):
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8")
            except AttributeError:
                pass


def resolve_email(arg_email):
    email = arg_email or os.environ.get("NCBI_EMAIL")
    if not email:
        sys.exit(
            "error: NCBI contact email is required.\n"
            "  Pass --email you@example.com, or set the NCBI_EMAIL environment "
            "variable.\n  (NCBI E-utilities terms of use require a contact email.)"
        )
    return email


def _common_params(email, api_key):
    params = {"tool": TOOL, "email": email}
    if api_key:
        params["api_key"] = api_key
    return params


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def esearch(query, retmax, email, api_key):
    params = _common_params(email, api_key)
    params.update({"db": "pubmed", "term": query, "retmax": str(retmax),
                   "sort": "relevance"})
    url = f"{EUTILS}/esearch.fcgi?{urllib.parse.urlencode(params)}"
    root = ET.fromstring(_get(url))
    count_elem = root.find(".//Count")
    total = count_elem.text if count_elem is not None else "?"
    pmids = [e.text for e in root.findall(".//IdList/Id")]
    return pmids, total


def _text(elem):
    return "".join(elem.itertext()).strip() if elem is not None else ""


def _pick_quote(abstract, highlight):
    """One verbatim fragment (<=40 words) showing why the record is relevant.

    Default: the abstract's first sentence. If --highlight terms are given,
    prefer the first sentence containing any of them. Quotes are copied
    verbatim (never paraphrased) so they stay auditable; long sentences are
    truncated with an ellipsis rather than reworded.
    """
    if not abstract:
        return "[no abstract available]"
    sentences = [s.strip() for s in re.split(r"(?<=\.)\s+", abstract) if s.strip()]
    if not sentences:
        return abstract
    chosen = sentences[0]
    if highlight:
        terms = [t.strip().lower() for t in highlight if t.strip()]
        for s in sentences:
            if any(t in s.lower() for t in terms):
                chosen = s
                break
    words = chosen.split()
    if len(words) > 40:
        chosen = " ".join(words[:40]) + " ..."
    return chosen


def parse_articles(xml_data, highlight):
    root = ET.fromstring(xml_data)
    articles = []
    for art in root.findall(".//PubmedArticle"):
        pmid = _text(art.find(".//MedlineCitation/PMID"))
        title = _text(art.find(".//MedlineCitation/Article/ArticleTitle"))

        authors = []
        for author in art.findall(".//MedlineCitation/Article/AuthorList/Author"):
            last = author.find("LastName")
            fore = author.find("ForeName")
            initials = author.find("Initials")
            if last is not None and last.text:
                name = last.text
                if fore is not None and fore.text:
                    name += ", " + fore.text
                elif initials is not None and initials.text:
                    name += ", " + initials.text
                authors.append(name)
        author_str = " and ".join(authors) if authors else ""

        journal = _text(art.find(".//Journal/Title"))
        if not journal:
            journal = _text(art.find(".//Journal/ISOAbbreviation"))

        year = _text(art.find(".//Journal/JournalIssue/PubDate/Year"))
        if not year:
            medline = _text(art.find(".//Journal/JournalIssue/PubDate/MedlineDate"))
            m = re.search(r"\d{4}", medline)
            year = m.group(0) if m else ""

        volume = _text(art.find(".//Journal/JournalIssue/Volume"))
        issue = _text(art.find(".//Journal/JournalIssue/Issue"))
        pages = _text(art.find(".//Article/Pagination/MedlinePgn"))

        doi = ""
        for aid in art.findall(".//PubmedData/ArticleIdList/ArticleId"):
            if aid.attrib.get("IdType") == "doi":
                doi = (aid.text or "").strip()
                break

        # Publication types (lets the author prefer reviews/guidelines/RCTs).
        ptypes = [_text(p) for p in
                  art.findall(".//MedlineCitation/Article/PublicationTypeList/PublicationType")]
        ptypes = [p for p in ptypes if p and p.lower() != "journal article"]

        abstract_parts = art.findall(".//MedlineCitation/Article/Abstract/AbstractText")
        abstract = " ".join(_text(p) for p in abstract_parts).strip()
        quote = _pick_quote(abstract, highlight)

        articles.append({
            "pmid": pmid, "title": title, "author": author_str,
            "journal": journal, "year": year, "volume": volume, "issue": issue,
            "pages": pages, "doi": doi, "ptypes": ptypes, "quote": quote,
            "bibtex": _bibtex(pmid, title, author_str, journal, year,
                              volume, issue, pages, doi),
        })
    return articles


def efetch(pmids, email, api_key, highlight):
    if not pmids:
        return []
    params = _common_params(email, api_key)
    params.update({"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"})
    url = f"{EUTILS}/efetch.fcgi?{urllib.parse.urlencode(params)}"
    # Be polite: 3 req/s without a key, 10 with. We only issue one efetch here.
    time.sleep(0.34 if not api_key else 0.1)
    return parse_articles(_get(url), highlight)


def _bibtex(pmid, title, author, journal, year, volume, issue, pages, doi):
    lines = [f"@article{{pmid{pmid},"]
    lines.append(f"  title = {{{title}}},")
    if author:
        lines.append(f"  author = {{{author}}},")
    if journal:
        lines.append(f"  journal = {{{journal}}},")
    if year:
        lines.append(f"  year = {{{year}}},")
    if volume:
        lines.append(f"  volume = {{{volume}}},")
    if issue:
        lines.append(f"  number = {{{issue}}},")
    if pages:
        lines.append(f"  pages = {{{pages}}},")
    if doi:
        lines.append(f"  doi = {{{doi}}},")
    lines.append(f"  pmid = {{{pmid}}}")
    lines.append("}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# search subcommand                                                           #
# --------------------------------------------------------------------------- #

def read_query(args):
    if args.query_file:
        with open(args.query_file, "r", encoding="utf-8") as fh:
            # Allow comment lines starting with '#'; join the rest into one query.
            lines = [ln.rstrip("\n") for ln in fh]
        body = [ln for ln in lines if not ln.lstrip().startswith("#")]
        query = " ".join(ln.strip() for ln in body if ln.strip())
        if not query:
            sys.exit(f"error: no query found in {args.query_file} "
                     "(all lines blank or comments).")
        return query
    if args.query:
        return args.query
    sys.exit("error: provide --query-file or --query.")


def default_out_path(args):
    if args.out:
        return args.out
    if args.query_file:
        stem = re.sub(r"\.query$", "", os.path.splitext(args.query_file)[0])
        return stem + ".candidates.md"
    return None


def render_candidates_md(query, total, mode, articles):
    out = []
    out.append("# similar_cases_search candidates (staging — not a render .bib)")
    out.append("")
    out.append(f"- Mode: `{mode}`")
    out.append(f"- Query: `{query}`")
    out.append(f"- Total hits: {total} (showing {len(articles)})")
    out.append("")
    out.append("> Review the verbatim quotes below, then promote approved PMIDs "
               "into `refs.bib` with:")
    out.append(">")
    pmids_example = ",".join(a["pmid"] for a in articles) or "<pmids>"
    out.append(f">     python pubmed_search.py add --pmids {pmids_example} "
               "--bib refs.bib")
    out.append("")
    out.append("| # | PMID | Year | Journal | Type | Title |")
    out.append("|---|---|---|---|---|---|")
    for i, a in enumerate(articles, 1):
        ptype = a["ptypes"][0] if a["ptypes"] else ""
        title = a["title"].replace("|", "\\|")
        out.append(f"| {i} | {a['pmid']} | {a['year']} | {a['journal']} | "
                   f"{ptype} | {title} |")
    out.append("")
    out.append("## Supporting quotes (verbatim from each abstract)")
    out.append("")
    for i, a in enumerate(articles, 1):
        out.append(f"- **#{i} (PMID {a['pmid']})**: \"{a['quote']}\"")
    out.append("")
    out.append("## BibTeX (for audit — copy approved blocks, or use `add`)")
    out.append("")
    out.append("```bibtex")
    out.append("\n\n".join(a["bibtex"] for a in articles))
    out.append("```")
    out.append("")
    return "\n".join(out)


def cmd_search(args):
    email = resolve_email(args.email)
    api_key = args.api_key or os.environ.get("NCBI_API_KEY")
    highlight = args.highlight.split(",") if args.highlight else []
    query = read_query(args)

    print(f"Query: {query}", file=sys.stderr)
    pmids, total = esearch(query, args.max, email, api_key)
    if not pmids:
        sys.exit("No hits. Broaden the query (drop a term, switch [mh] -> [tiab], "
                 "or remove a publication-type filter) and retry.")
    articles = efetch(pmids, email, api_key, highlight)

    md = render_candidates_md(query, total, args.mode, articles)
    print(md)

    out_path = default_out_path(args)
    if out_path:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(md)
        print(f"\n[wrote staging file] {out_path}", file=sys.stderr)
    else:
        print("\n[no --out given and no --query-file to derive a path; "
              "candidates printed to stdout only]", file=sys.stderr)


# --------------------------------------------------------------------------- #
# add subcommand                                                              #
# --------------------------------------------------------------------------- #

def existing_keys(bib_path):
    if not os.path.exists(bib_path):
        return set()
    with open(bib_path, "r", encoding="utf-8") as fh:
        text = fh.read()
    return set(re.findall(r"@\w+\{\s*(pmid\d+)\s*,", text))


def cmd_add(args):
    email = resolve_email(args.email)
    api_key = args.api_key or os.environ.get("NCBI_API_KEY")
    pmids = [p.strip() for p in args.pmids.split(",") if p.strip()]
    if not pmids:
        sys.exit("error: --pmids is empty.")

    have = existing_keys(args.bib)
    wanted = [p for p in pmids if f"pmid{p}" not in have]
    skipped = [p for p in pmids if f"pmid{p}" in have]

    if not wanted:
        print(f"Nothing to add: all of {pmids} already in {args.bib}.")
        return

    articles = efetch(wanted, email, api_key, highlight=[])
    fetched = {a["pmid"] for a in articles}
    missing = [p for p in wanted if p not in fetched]

    blocks = "\n\n".join(a["bibtex"] for a in articles)
    needs_newline = os.path.exists(args.bib) and os.path.getsize(args.bib) > 0
    os.makedirs(os.path.dirname(os.path.abspath(args.bib)) or ".", exist_ok=True)
    with open(args.bib, "a", encoding="utf-8") as fh:
        if needs_newline:
            fh.write("\n\n")
        fh.write(blocks + "\n")

    print(f"Appended {len(articles)} entr{'y' if len(articles)==1 else 'ies'} "
          f"to {args.bib}:")
    for a in articles:
        print(f"  + pmid{a['pmid']}  {a['journal']} {a['year']}")
    if skipped:
        print(f"Skipped (already present): {', '.join('pmid'+p for p in skipped)}")
    if missing:
        print(f"WARNING: no PubMed record returned for: {', '.join(missing)} "
              "(check the PMIDs).", file=sys.stderr)


def main():
    _utf8_stdout()
    parser = argparse.ArgumentParser(
        description="PubMed-grounded reference search (Writing with AI workflow).")
    sub = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--email", help="NCBI contact email (or set $NCBI_EMAIL).")
    common.add_argument("--api-key", help="NCBI API key (or set $NCBI_API_KEY).")

    p_search = sub.add_parser("search", parents=[common],
                              help="Search PubMed and write a candidates.md staging file.")
    p_search.add_argument("--query-file", help="Path to a search-formula file "
                          "(projects/<name>/searches/<topic>.query.txt).")
    p_search.add_argument("--query", help="Inline query string (alternative to --query-file).")
    p_search.add_argument("--max", type=int, default=5, help="Max candidates (default 5).")
    p_search.add_argument("--mode", default="similar_cases",
                          choices=["similar_cases", "background_literature"],
                          help="Search mode label recorded in the output (default similar_cases).")
    p_search.add_argument("--highlight", help="Comma-separated terms to bias quote "
                          "selection toward (default: first sentence).")
    p_search.add_argument("--out", help="Output path for the candidates.md staging "
                          "file (default: alongside --query-file).")
    p_search.set_defaults(func=cmd_search)

    p_add = sub.add_parser("add", parents=[common],
                           help="Fetch approved PMIDs and append them to a refs.bib.")
    p_add.add_argument("--pmids", required=True, help="Comma-separated approved PMIDs.")
    p_add.add_argument("--bib", required=True, help="Path to the render bibliography "
                       "(projects/<name>/refs.bib) to append to.")
    p_add.set_defaults(func=cmd_add)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
