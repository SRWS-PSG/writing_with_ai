"""Tests for check_direct_edits.py.

Requires pandoc on PATH; skipped otherwise. Uses the repo's demo/refs.bib and
demo/styles/american-medical-association.csl for citeproc rendering (verified
in this test module to contain the page2021prisma / vonelm2007strobe keys the
brief asks for; falls back to a tiny local bib/csl if that assumption ever
breaks, and says so via a skip reason rather than failing silently).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_direct_edits.py"
TESTS_DIR = Path(__file__).resolve().parent
FIXTURE_V1 = TESTS_DIR / "fixture_v1.md"
GOOGLE_EXPORT_DIR = TESTS_DIR / "fixtures_google_export"
GOOGLE_EXPORT_DOCX = GOOGLE_EXPORT_DIR / "reviewed_google_export.docx"
GOOGLE_EXPORT_SNAPSHOT = GOOGLE_EXPORT_DIR / "snapshot_v1.md"
REPO_ROOT = Path(__file__).resolve().parents[3]
DEMO_BIB = REPO_ROOT / "demo" / "refs.bib"
DEMO_CSL = REPO_ROOT / "demo" / "styles" / "american-medical-association.csl"

PANDOC = shutil.which("pandoc")


def _demo_bib_has_expected_keys() -> bool:
    if not DEMO_BIB.exists():
        return False
    text = DEMO_BIB.read_text(encoding="utf-8")
    return "page2021prisma" in text and "vonelm2007strobe" in text


USE_DEMO_REFS = DEMO_BIB.exists() and DEMO_CSL.exists() and _demo_bib_has_expected_keys()

# Fallback tiny bibliography, used only if the repo's demo/refs.bib assumption
# above does not hold (reported via the skip/setup reason, per the brief).
FALLBACK_BIB = """\
@article{page2021prisma,
  title = {The PRISMA 2020 statement},
  author = {Page, Matthew J and McKenzie, Joanne E},
  journal = {BMJ},
  year = {2021},
  volume = {372},
  pages = {n71},
}
@article{vonelm2007strobe,
  title = {The STROBE statement},
  author = {von Elm, Erik and Altman, Douglas G},
  journal = {Journal of Clinical Epidemiology},
  year = {2008},
  volume = {61},
  number = {4},
  pages = {344--349},
}
"""


def run(args: list[str]) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


@unittest.skipUnless(PANDOC, "pandoc not found on PATH")
class TestCheckDirectEdits(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.td = Path(self.tmpdir.name)
        if USE_DEMO_REFS:
            self.bib = DEMO_BIB
            self.csl = DEMO_CSL
        else:
            self.bib = self.td / "refs.bib"
            write(self.bib, FALLBACK_BIB)
            # Use pandoc's built-in AMA-like numeric CSL is not guaranteed available
            # offline, so when the demo CSL is missing we still need *a* CSL. Reuse
            # the demo one if it exists even though the bib fell back, otherwise skip.
            if DEMO_CSL.exists():
                self.csl = DEMO_CSL
            else:
                self.skipTest(
                    "demo/refs.bib did not contain expected keys and "
                    "demo/styles/american-medical-association.csl is missing; "
                    "cannot render citeproc output for this test."
                )

    def tearDown(self):
        self.tmpdir.cleanup()

    def _render_docx(self, md_path: Path, docx_path: Path, track_changes_source: bool = False) -> None:
        cmd = [
            "pandoc", str(md_path),
            "--citeproc", "--bibliography", str(self.bib), "--csl", str(self.csl),
            "-o", str(docx_path),
        ]
        proc = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_identical_content_with_citeproc_exits_zero(self):
        text = (
            "---\ntitle: Probe\n---\n\n"
            "# Introduction\n\n"
            "This is a claim [@page2021prisma; @vonelm2007strobe]. "
            "Another sentence here, with a comma, that stays the same.\n\n"
            "# Methods\n\n"
            "We did the study carefully, following the protocol, as planned [@page2021prisma].\n"
        )
        snapshot = self.td / "draft.v1.md"
        write(snapshot, text)
        docx = self.td / "reviewed.docx"
        self._render_docx(snapshot, docx)

        proc = run(["--reviewed-docx", str(docx), "--snapshot", str(snapshot)])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_one_sentence_edited_is_detected(self):
        snapshot_text = (
            "---\ntitle: Probe\n---\n\n"
            "# Introduction\n\n"
            "This is a claim, based on prior work, [@page2021prisma; @vonelm2007strobe]. "
            "Another sentence here that stays the same.\n"
        )
        snapshot = self.td / "draft.v1.md"
        write(snapshot, snapshot_text)

        edited_text = (
            "---\ntitle: Probe\n---\n\n"
            "# Introduction\n\n"
            "This is a claim, based on prior work, [@page2021prisma; @vonelm2007strobe]. "
            "This sentence was directly changed by the reviewer.\n"
        )
        edited = self.td / "edited.md"
        write(edited, edited_text)
        docx = self.td / "reviewed.docx"
        self._render_docx(edited, docx)

        proc = run(["--reviewed-docx", str(docx), "--snapshot", str(snapshot)])
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("directly changed by the reviewer", proc.stdout)

    def _check_citation_round_trip(self, text: str, *, edited: bool, plain_fragments: tuple[str, ...]):
        self.assertTrue(USE_DEMO_REFS, "citation regression cases require the demo bibliography and CSL")
        snapshot = self.td / "snapshot.md"
        reviewed = self.td / "reviewed.md"
        docx = self.td / "reviewed.docx"
        write(snapshot, text)
        write(reviewed, text.replace("Original", "CHANGEDWORD", 1) if edited else text)
        self._render_docx(reviewed, docx)
        plain = subprocess.run(
            ["pandoc", str(docx), "--track-changes=reject", "-t", "plain", "--wrap=none"],
            capture_output=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(plain.returncode, 0, plain.stderr)
        for fragment in plain_fragments:
            self.assertIn(fragment, plain.stdout)

        proc = run(["--reviewed-docx", str(docx), "--snapshot", str(snapshot), "--json"])
        self.assertEqual(proc.returncode, 2 if edited else 0, proc.stdout + proc.stderr)
        result = json.loads(proc.stdout)
        if edited:
            self.assertIn("CHANGEDWORD", proc.stdout)
            self.assertEqual(len(result["findings"]), 1, proc.stdout)
            finding = result["findings"][0]
            self.assertEqual(finding["snapshot"], ["Original wording remains."])
            self.assertEqual(finding["reviewed"], ["CHANGEDWORD wording remains."])
        else:
            self.assertEqual(result["findings"], [])

    def _check_inline_code_citations(self, *, edited: bool):
        self._check_citation_round_trip(
            "Original wording remains.\n\n"
            "引用は pandoc citekey `[@key]` / で示す。\n\n"
            "`[@page2021prisma]` はコード例です。\n\n"
            "```text\n[@key] @page2021prisma\n```\n\n"
            "Evidence supports the claim [@page2021prisma].\n",
            edited=edited,
            plain_fragments=("[@key]", "[@page2021prisma]", "[@key] @page2021prisma"),
        )

    def test_inline_code_citations_unchanged_exits_zero(self):
        self._check_inline_code_citations(edited=False)

    def test_inline_code_citations_changed_word_is_detected(self):
        self._check_inline_code_citations(edited=True)

    def _check_unresolved_citations(self, *, edited: bool):
        self._check_citation_round_trip(
            "Original wording remains.\n\n"
            "Sources （gray lit, @nosuchkey2026） and (see @alsomissing).\n\n"
            "Grouped [@nosuchkey2026; @alsomissing].\n\n"
            "An unrelated question: uncertain?\n",
            edited=edited,
            plain_fragments=(
                "（gray lit,^(nosuchkey2026?)）",
                "(see^(alsomissing?))",
                "^(nosuchkey2026?,alsomissing?)",
                "uncertain?",
            ),
        )

    def test_unresolved_citations_unchanged_exits_zero(self):
        self._check_unresolved_citations(edited=False)

    def test_unresolved_citations_changed_word_is_detected(self):
        self._check_unresolved_citations(edited=True)

    def test_pending_suggestions_reject_to_snapshot_exits_zero(self):
        snapshot_text = (
            "---\ntitle: Probe\n---\n\n"
            "# Introduction\n\n"
            "This is the original claim, according to the first report, [@page2021prisma]. "
            "It continues here.\n"
        )
        snapshot = self.td / "draft.v1.md"
        write(snapshot, snapshot_text)

        pending_text = (
            "---\ntitle: Probe\n---\n\n"
            "# Introduction\n\n"
            'This is the [original]{.deletion author="R" date="2026-01-01T00:00:00Z"}'
            '[revised]{.insertion author="R" date="2026-01-01T00:00:00Z"} '
            "claim, according to the first report, [@page2021prisma]. It continues here.\n"
        )
        pending = self.td / "pending.md"
        write(pending, pending_text)
        docx = self.td / "reviewed.docx"
        self._render_docx(pending, docx)

        proc = run(["--reviewed-docx", str(docx), "--snapshot", str(snapshot)])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_japanese_paragraph_edit_is_detected(self):
        snapshot_text = (
            "---\ntitle: JP probe\n---\n\n"
            "# はじめに\n\n"
            "これは元の文章です [@page2021prisma]。次の文も続きます。\n\n"
            "# 方法\n\n"
            "対象は成人患者とした [@vonelm2007strobe]。\n"
        )
        snapshot = self.td / "draft.v1.md"
        write(snapshot, snapshot_text)

        edited_text = (
            "---\ntitle: JP probe\n---\n\n"
            "# はじめに\n\n"
            "これは元の文章です [@page2021prisma]。次の文も続きます。\n\n"
            "# 方法\n\n"
            "対象は成人患者と小児患者とした [@vonelm2007strobe]。\n"
        )
        edited = self.td / "edited.md"
        write(edited, edited_text)
        docx = self.td / "reviewed.docx"
        self._render_docx(edited, docx)

        proc = run(["--reviewed-docx", str(docx), "--snapshot", str(snapshot)])
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("小児患者", proc.stdout)

    def test_email_address_in_unchanged_paragraph_exits_zero(self):
        # An email address must survive citation removal.
        text = (
            "---\ntitle: Probe\n---\n\n"
            "# Contact\n\n"
            "For questions, correspondence, or data requests, contact the "
            "corresponding author at user@example.com, or by mail.\n"
        )
        snapshot = self.td / "draft.v1.md"
        write(snapshot, text)
        docx = self.td / "reviewed.docx"
        self._render_docx(snapshot, docx)

        proc = run(["--reviewed-docx", str(docx), "--snapshot", str(snapshot)])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_fixture_v1_round_trip_exits_zero(self):
        # Realistic regression test: render the committed fixture_v1.md (which
        # has commas throughout, and an image reference to a file that does not
        # exist on disk) through the exact pipeline used in production, and
        # check it against itself. The fixture's own front matter declares
        # `bibliography: refs.bib` and `csl: styles/american-medical-association.csl`
        # as paths relative to the markdown file, so pandoc is run with cwd set
        # to a tempdir containing copies of fixture_v1.md plus those two files
        # under those exact relative names (no --bibliography/--csl flags, to
        # avoid pandoc merging a second, nonexistent "refs.bib" into the meta
        # field). pandoc only warns about the missing assets/figure1.png and
        # still exits 0.
        self.assertTrue(FIXTURE_V1.exists(), f"missing fixture: {FIXTURE_V1}")
        work = self.td / "fixture_work"
        work.mkdir()
        fixture_copy = work / "fixture_v1.md"
        shutil.copyfile(FIXTURE_V1, fixture_copy)
        shutil.copyfile(self.bib, work / "refs.bib")
        (work / "styles").mkdir()
        shutil.copyfile(self.csl, work / "styles" / "american-medical-association.csl")

        docx = work / "reviewed.docx"
        proc = subprocess.run(
            ["pandoc", "fixture_v1.md", "--citeproc", "-o", "reviewed.docx"],
            capture_output=True, encoding="utf-8", errors="replace", cwd=str(work),
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

        result = run(["--reviewed-docx", str(docx), "--snapshot", str(fixture_copy)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_real_google_export_fixture_exits_zero(self):
        # Real-world regression: a v2 docx produced by make_tracked_md.py +
        # pandoc, uploaded to Drive, imported as a Google Doc, and exported
        # back to docx by rclone. Nobody edited it directly, so rejecting all
        # tracked changes must reproduce the v1 snapshot exactly. This is not
        # a pandoc-made docx (unlike every other test above) and exposed three
        # generic normalization gaps: Google's export flattens the docx
        # Title/Author/Date paragraph styles into ordinary body text (Title
        # itself disappears, Author/Date remain as plain paragraphs), it
        # duplicates the figure caption as a second, differently-styled
        # paragraph right after the image placeholder, and it splits a tight
        # ordered list (one paragraph, four lines) into four separate
        # paragraphs. The images the snapshot references (assets/figure1.png)
        # do not exist under fixtures_google_export/; `-t plain` never fetches
        # image bytes, so that is not expected to matter.
        self.assertTrue(GOOGLE_EXPORT_DOCX.exists(), f"missing fixture: {GOOGLE_EXPORT_DOCX}")
        self.assertTrue(GOOGLE_EXPORT_SNAPSHOT.exists(), f"missing fixture: {GOOGLE_EXPORT_SNAPSHOT}")

        proc = run(["--reviewed-docx", str(GOOGLE_EXPORT_DOCX), "--snapshot", str(GOOGLE_EXPORT_SNAPSHOT)])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_real_google_export_fixture_detects_edited_word(self):
        # Same fixture pair, but with one word changed in a copy of the
        # snapshot (in a tempdir, so the committed fixture is untouched).
        # This must still be caught as a direct edit despite all the
        # normalization added to make the unedited pair above exit 0.
        self.assertTrue(GOOGLE_EXPORT_SNAPSHOT.exists(), f"missing fixture: {GOOGLE_EXPORT_SNAPSHOT}")
        original = GOOGLE_EXPORT_SNAPSHOT.read_text(encoding="utf-8")
        needle = "same core ideas for protocols"
        replacement = "same core CHANGEDWORD for protocols"
        self.assertIn(needle, original, "fixture text assumption changed; update this test")
        edited = original.replace(needle, replacement)

        edited_snapshot = self.td / "snapshot_v1_edited.md"
        write(edited_snapshot, edited)

        proc = run(["--reviewed-docx", str(GOOGLE_EXPORT_DOCX), "--snapshot", str(edited_snapshot)])
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("CHANGEDWORD", proc.stdout)


if __name__ == "__main__":
    unittest.main()
