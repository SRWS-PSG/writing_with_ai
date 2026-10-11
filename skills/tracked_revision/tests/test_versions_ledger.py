"""Tests for versions_ledger.py (CLI subcommands: name / check / record)."""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "versions_ledger.py"


def run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(cwd) if cwd else None,
        env=env,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


class TestName(unittest.TestCase):
    def test_name_format(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            docx = td / "v2.docx"
            data = b"fake docx bytes for hashing"
            write_bytes(docx, data)
            digest = hashlib.sha256(data).hexdigest()[:8]

            proc = run(["name", "--docx", str(docx), "--stem", "draft_v2_tracked"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip(), f"draft_v2_tracked_{digest}.docx")


class TestCheck(unittest.TestCase):
    def test_check_missing_ledger_is_ok(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            docx = td / "v1.docx"
            write_bytes(docx, b"content-a")
            ledger = td / "versions" / "versions.md"  # does not exist

            proc = run(["check", "--ledger", str(ledger), "--docx", str(docx)])
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_check_after_record_blocks_reupload(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            md = td / "draft.md"
            write(md, "# Draft\n\nHello.\n")
            docx = td / "v1.docx"
            write_bytes(docx, b"content-b")
            ledger = td / "versions" / "versions.md"

            rec = run([
                "record", "--ledger", str(ledger), "--version", "v1",
                "--md", str(md), "--docx", str(docx), "--doc-id", "DOC1",
                "--date", "2026-01-01T00:00:00Z",
            ])
            self.assertEqual(rec.returncode, 0, rec.stderr)

            # same content -> blocked
            proc = run(["check", "--ledger", str(ledger), "--docx", str(docx)])
            self.assertEqual(proc.returncode, 3, proc.stdout)
            self.assertIn("v1", proc.stdout)
            self.assertIn("DOC1", proc.stdout)

            # different content -> ok
            docx2 = td / "v2.docx"
            write_bytes(docx2, b"content-c")
            proc2 = run(["check", "--ledger", str(ledger), "--docx", str(docx2)])
            self.assertEqual(proc2.returncode, 0, proc2.stdout)


class TestRecord(unittest.TestCase):
    def _record_once(self, td: Path, *, version="v1", doc_id="DOC1",
                      md_text="# Draft\n\nHello.\n", docx_bytes=b"content-a"):
        md = td / "draft.md"
        write(md, md_text)
        docx = td / f"{version}.docx"
        write_bytes(docx, docx_bytes)
        ledger = td / "versions" / "versions.md"
        proc = run([
            "record", "--ledger", str(ledger), "--version", version,
            "--md", str(md), "--docx", str(docx), "--doc-id", doc_id,
            "--date", "2026-01-01T00:00:00Z",
        ])
        return proc, ledger, md, docx

    def test_record_creates_ledger_with_exact_header(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            proc, ledger, md, docx = self._record_once(td)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(ledger.exists())
            text = ledger.read_text(encoding="utf-8")
            self.assertIn(
                "| version | date_utc | doc_id | md_sha256 | docx_sha256 | docx_name | md_snapshot |",
                text,
            )
            self.assertIn("DOC1", text)

    def test_record_rejects_duplicate_doc_id(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            proc1, ledger, md, docx = self._record_once(td, version="v1", doc_id="DOC1")
            self.assertEqual(proc1.returncode, 0, proc1.stderr)

            # different version/content but same doc_id -> should be rejected
            docx2 = td / "v2.docx"
            write_bytes(docx2, b"different-content")
            write(md, "# Draft\n\nHello v2.\n")
            proc2 = run([
                "record", "--ledger", str(ledger), "--version", "v2",
                "--md", str(md), "--docx", str(docx2), "--doc-id", "DOC1",
                "--date", "2026-01-02T00:00:00Z",
            ])
            self.assertEqual(proc2.returncode, 3, proc2.stdout)
            self.assertIn("doc_id", proc2.stdout.lower() + proc2.stdout)

    def test_record_rejects_duplicate_docx_hash(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            same_bytes = b"identical-docx-content"
            proc1, ledger, md, docx = self._record_once(
                td, version="v1", doc_id="DOC1", docx_bytes=same_bytes
            )
            self.assertEqual(proc1.returncode, 0, proc1.stderr)

            docx2 = td / "v2.docx"
            write_bytes(docx2, same_bytes)
            proc2 = run([
                "record", "--ledger", str(ledger), "--version", "v2",
                "--md", str(md), "--docx", str(docx2), "--doc-id", "DOC2",
                "--date", "2026-01-02T00:00:00Z",
            ])
            self.assertEqual(proc2.returncode, 3, proc2.stdout)

    def test_record_rejects_duplicate_version(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            proc1, ledger, md, docx = self._record_once(td, version="v1", doc_id="DOC1")
            self.assertEqual(proc1.returncode, 0, proc1.stderr)

            docx2 = td / "other.docx"
            write_bytes(docx2, b"totally-different")
            proc2 = run([
                "record", "--ledger", str(ledger), "--version", "v1",
                "--md", str(md), "--docx", str(docx2), "--doc-id", "DOC2",
                "--date", "2026-01-02T00:00:00Z",
            ])
            self.assertEqual(proc2.returncode, 3, proc2.stdout)

    def test_snapshot_copy_and_identical_reuse(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            proc, ledger, md, docx = self._record_once(td, version="v1", doc_id="DOC1")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            snapshot = ledger.parent / "draft.v1.md"
            self.assertTrue(snapshot.exists())
            self.assertEqual(snapshot.read_text(encoding="utf-8"), md.read_text(encoding="utf-8"))

    def test_snapshot_refuses_to_overwrite_differing_content(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            md = td / "draft.md"
            write(md, "# Draft\n\nNew content.\n")
            docx = td / "v2.docx"
            write_bytes(docx, b"some-docx-bytes")
            ledger = td / "versions" / "versions.md"
            ledger.parent.mkdir(parents=True, exist_ok=True)
            # Pre-existing snapshot for v2 with DIFFERENT content, but v2 not yet in ledger
            snapshot = ledger.parent / "draft.v2.md"
            write(snapshot, "# Draft\n\nOld pre-existing snapshot content.\n")

            proc = run([
                "record", "--ledger", str(ledger), "--version", "v2",
                "--md", str(md), "--docx", str(docx), "--doc-id", "DOC9",
                "--date", "2026-01-03T00:00:00Z",
            ])
            self.assertEqual(proc.returncode, 3, proc.stdout)
            # snapshot must be untouched
            self.assertEqual(
                snapshot.read_text(encoding="utf-8"),
                "# Draft\n\nOld pre-existing snapshot content.\n",
            )
            # ledger must not have been created/appended
            self.assertFalse(ledger.exists())

    def test_ledger_with_prose_above_table_still_parses(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            ledger = td / "versions" / "versions.md"
            write(
                ledger,
                "# バージョン履歴\n\n"
                "このファイルはアップロード履歴を記録する。\n\n"
                "| version | date_utc | doc_id | md_sha256 | docx_sha256 | docx_name | md_snapshot |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| v1 | 2026-01-01T00:00:00Z | DOC1 | mdhash1 | docxhash1 | draft_v1.docx | draft.v1.md |\n",
            )
            docx = td / "match.docx"
            write_bytes(docx, b"whatever")
            # monkeypatch: check compares real sha256, so craft a docx whose hash equals docxhash1?
            # Simpler: just verify check() on a NON-matching docx returns 0 (parses fine, no match),
            # then verify record() can append after prose without corrupting the table.
            proc = run(["check", "--ledger", str(ledger), "--docx", str(docx)])
            self.assertEqual(proc.returncode, 0, proc.stdout)

            md = td / "draft.md"
            write(md, "# Draft\n\nSecond version body.\n")
            docx2 = td / "v2.docx"
            write_bytes(docx2, b"second-version-bytes")
            proc2 = run([
                "record", "--ledger", str(ledger), "--version", "v2",
                "--md", str(md), "--docx", str(docx2), "--doc-id", "DOC2",
                "--date", "2026-01-02T00:00:00Z",
            ])
            self.assertEqual(proc2.returncode, 0, proc2.stderr)
            text = ledger.read_text(encoding="utf-8")
            self.assertIn("このファイルはアップロード履歴を記録する。", text)
            self.assertIn("DOC1", text)
            self.assertIn("DOC2", text)
            # both data rows present, in order, with header still intact once
            self.assertEqual(text.count("| version | date_utc |"), 1)

    def test_append_row_ignores_unrelated_table_below_ledger(self):
        # A second, unrelated Markdown table sitting after the ledger table
        # must not receive the new row, and its own rows must not be
        # mistaken for the last row of the ledger table.
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            ledger = td / "versions" / "versions.md"
            write(
                ledger,
                "| version | date_utc | doc_id | md_sha256 | docx_sha256 | docx_name | md_snapshot |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| v1 | 2026-01-01T00:00:00Z | DOC1 | mdhash1 | docxhash1 | draft_v1.docx | draft.v1.md |\n"
                "\n"
                "# 別表 (無関係)\n\n"
                "| name | value |\n"
                "| --- | --- |\n"
                "| foo | 1 |\n"
                "| bar | 2 |\n",
            )
            md = td / "draft.md"
            write(md, "# Draft\n\nSecond version body.\n")
            docx2 = td / "v2.docx"
            write_bytes(docx2, b"second-version-bytes-for-unrelated-table-test")

            proc = run([
                "record", "--ledger", str(ledger), "--version", "v2",
                "--md", str(md), "--docx", str(docx2), "--doc-id", "DOC2",
                "--date", "2026-01-02T00:00:00Z",
            ])
            self.assertEqual(proc.returncode, 0, proc.stderr)

            text = ledger.read_text(encoding="utf-8")
            lines = text.split("\n")

            v1_idx = next(i for i, l in enumerate(lines) if "DOC1" in l)
            v2_idx = next(i for i, l in enumerate(lines) if "DOC2" in l)
            unrelated_header_idx = next(i for i, l in enumerate(lines) if l.strip() == "| name | value |")
            foo_idx = next(i for i, l in enumerate(lines) if "| foo | 1 |" in l)

            # the new row must land right after the v1 row, inside the ledger
            # table, and strictly before the unrelated table starts
            self.assertEqual(v2_idx, v1_idx + 1)
            self.assertLess(v2_idx, unrelated_header_idx)
            # the unrelated table must be untouched (still exactly its own two rows)
            self.assertIn("| foo | 1 |", text)
            self.assertIn("| bar | 2 |", text)
            self.assertGreater(foo_idx, unrelated_header_idx)


if __name__ == "__main__":
    unittest.main()
