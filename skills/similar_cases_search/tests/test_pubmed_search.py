"""Tests for pubmed_search.py: BibTeX escaping and collective authors.

Offline only: efetch XML is parsed from strings / the frozen fixture, and the
BibTeX is rendered through pandoc (skipped when pandoc is not installed).
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "pubmed_search.py"

_spec = importlib.util.spec_from_file_location("pubmed_search", SCRIPT)
ps = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ps)

HAVE_PANDOC = shutil.which("pandoc") is not None


def efetch_xml(title: str, authors_xml: str, pmid: str = "99999100") -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation Status="MEDLINE" Owner="NLM">
      <PMID Version="1">{pmid}</PMID>
      <Article PubModel="Print">
        <Journal>
          <JournalIssue CitedMedium="Print">
            <PubDate><Year>2020</Year></PubDate>
          </JournalIssue>
          <Title>Test Journal</Title>
        </Journal>
        <ArticleTitle>{title}</ArticleTitle>
        <AuthorList CompleteYN="Y">{authors_xml}</AuthorList>
      </Article>
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>
"""


def person(last: str, fore: str) -> str:
    return (f"<Author ValidYN='Y'><LastName>{last}</LastName>"
            f"<ForeName>{fore}</ForeName><Initials>X</Initials></Author>")


def collective(name: str) -> str:
    return f"<Author ValidYN='Y'><CollectiveName>{name}</CollectiveName></Author>"


def render_plain(bibtex: str) -> str:
    """Render one BibTeX block through pandoc citeproc and return plain text."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "d.md").write_text('---\nnocite: "@*"\n---\n', encoding="utf-8")
        (td / "r.bib").write_text(bibtex + "\n", encoding="utf-8", newline="\n")
        proc = subprocess.run(
            ["pandoc", "d.md", "--citeproc", "--bibliography", "r.bib",
             "-t", "plain"],
            capture_output=True, encoding="utf-8", cwd=str(td))
        assert proc.returncode == 0, proc.stderr
        return proc.stdout


class TestBibtexEscape(unittest.TestCase):
    def test_special_characters(self):
        esc = ps._bibtex_escape
        self.assertEqual(esc("50%"), r"50\%")
        self.assertEqual(esc("Trial #2"), r"Trial \#2")
        self.assertEqual(esc("$100"), r"\$100")
        self.assertEqual(esc("~5 mg"), r"\textasciitilde{}5 mg")
        self.assertEqual(esc("a\\b"), r"a\textbackslash{}b")
        self.assertEqual(esc("a { b"), r"a \{ b")
        self.assertEqual(esc("a } b"), r"a \} b")

    def test_backslash_not_double_escaped(self):
        # A literal backslash followed by '%' must become two separate escapes,
        # not have the backslash of "\%" re-escaped.
        self.assertEqual(ps._bibtex_escape("\\%"), r"\textbackslash{}\%")

    def test_plain_text_unchanged(self):
        for s in ("Risk & benefit of X", "The IL_6 pathway", "Volume 10^3 cells",
                  "Daptomycin-induced eosinophilic pneumonia: a case report", ""):
            self.assertEqual(ps._bibtex_escape(s), s)

    @unittest.skipUnless(HAVE_PANDOC, "pandoc not installed")
    def test_round_trip_through_pandoc(self):
        title = ("A 50% reduction, Trial #2, costs of $100 and $200, "
                 "dose ~5 mg, back\\slash, unbalanced } and { braces")
        bib = ps._bibtex("1", title, "", "J", "2020", "", "", "", "")
        out = render_plain(bib).lower()
        for frag in ("a 50% reduction", "trial #2", "costs of $100 and $200",
                     "dose ~5 mg", "back\\slash", "unbalanced } and { braces"):
            self.assertIn(frag, out)


class TestParseArticles(unittest.TestCase):
    @unittest.skipUnless(HAVE_PANDOC, "pandoc not installed")
    def test_special_characters_in_efetch_title_render_intact(self):
        title = "A 50% drop in Trial #2: $100 per patient, dose ~5 mg"
        arts = ps.parse_articles(efetch_xml(title, person("Doe", "Jane")), [])
        self.assertEqual(arts[0]["title"], title)
        out = render_plain(arts[0]["bibtex"]).lower()
        self.assertIn("a 50% drop in trial #2: $100 per patient, dose ~5 mg", out)

    def test_collective_only(self):
        arts = ps.parse_articles(
            efetch_xml("T", collective("RECOVERY Collaborative Group")), [])
        self.assertEqual(arts[0]["author"], "{RECOVERY Collaborative Group}")
        self.assertIn("  author = {{RECOVERY Collaborative Group}},",
                      arts[0]["bibtex"])

    def test_collective_and_persons_keep_order(self):
        xml = efetch_xml(
            "T",
            person("Smith", "Ann") + collective("RECOVERY Collaborative Group")
            + person("Horby", "Peter"))
        arts = ps.parse_articles(xml, [])
        self.assertEqual(
            arts[0]["author"],
            "Smith, Ann and {RECOVERY Collaborative Group} and Horby, Peter")

    def test_collective_name_is_escaped(self):
        arts = ps.parse_articles(
            efetch_xml("T", collective("Group 50% &amp; Co #1")), [])
        self.assertEqual(arts[0]["author"], r"{Group 50\% & Co \#1}")

    @unittest.skipUnless(HAVE_PANDOC, "pandoc not installed")
    def test_collective_author_renders_as_one_name(self):
        xml = efetch_xml(
            "T", collective("RECOVERY Collaborative Group") + person("Horby", "Peter"))
        arts = ps.parse_articles(xml, [])
        out = render_plain(arts[0]["bibtex"])
        self.assertIn("RECOVERY Collaborative Group", out)
        self.assertNotIn("Group, RECOVERY", out)

    @unittest.skipUnless(HAVE_PANDOC, "pandoc not installed")
    def test_collective_only_renders(self):
        arts = ps.parse_articles(
            efetch_xml("T", collective("RECOVERY Collaborative Group")), [])
        self.assertIn("RECOVERY Collaborative Group", render_plain(arts[0]["bibtex"]))


class TestFixture(unittest.TestCase):
    def test_fixture_produces_expected_bib(self):
        arts = ps.parse_articles((HERE / "fixture_efetch.xml").read_bytes(), [])
        got = "\n\n".join(a["bibtex"] for a in arts)
        expected = (HERE / "expected_refs.bib").read_text(encoding="utf-8")
        body = "\n".join(
            ln for ln in expected.splitlines() if not ln.startswith("%")).strip()
        self.assertEqual(got.strip(), body)


if __name__ == "__main__":
    unittest.main()
