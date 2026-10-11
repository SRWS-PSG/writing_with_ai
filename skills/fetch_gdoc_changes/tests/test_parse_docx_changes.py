"""parse_docx_changes.py のテスト。

pandoc で作った docx (コメントあり / なし) を parse_docx_changes.py に通し、
1 引数 / 2 引数呼び出しと、A7 の回帰 (中間展開フォルダを廃止したことで、
コメント無し docx の直後にコメントあり docx の古いコメントを引きずらない
こと) を確認する。

注意 (レビュー指摘): pandoc は docx を書き出すとき、コメントが1つも無くても
常に空の word/comments.xml (625 バイト) を zip に含める。そのため
「コメント無し docx」を pandoc の出力そのままにすると word/comments.xml が
実際には存在してしまい、旧コード (展開フォルダを使い回す実装) でも
たまたま空の comments.xml で上書きされて 0 件になってしまい、回帰を
検出できない。A7 のバグは「同じファイル名を使い回して再取得したとき、
2 回目の docx に word/comments.xml エントリが全く無いと、1 回目に展開した
古い comments.xml が残ったまま読まれる」ことなので、テストでは
strip_comments_entry() で word/comments.xml エントリ自体を zip から
取り除き、かつ 1 回目と同じファイル名 (同じ docx_path.stem) を使って
上書きすることで、旧実装の <stem>_unzipped フォルダが再利用される状況を
再現する。
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "parse_docx_changes.py"

HAVE_PANDOC = shutil.which("pandoc") is not None


def run_pandoc(md_text: str, out_docx: Path) -> None:
    md_path = out_docx.with_suffix(".src.md")
    md_path.write_text(md_text, encoding="utf-8")
    subprocess.run(
        ["pandoc", str(md_path), "-o", str(out_docx)],
        check=True,
        capture_output=True,
    )


def strip_comments_entry(src_docx: Path, dst_docx: Path) -> None:
    """word/comments.xml エントリを持たない docx を作る。pandoc は
    コメントが無くても空の comments.xml を常に書き出すので、それを
    そのまま使うと「comments.xml が本当に存在しない」状況を再現できない。"""
    with zipfile.ZipFile(src_docx) as zin:
        with zipfile.ZipFile(dst_docx, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == "word/comments.xml":
                    continue
                zout.writestr(item, zin.read(item.filename))


def run_parser(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={"PYTHONUTF8": "1", **_base_env()},
    )


def _base_env() -> dict:
    import os

    return dict(os.environ)


@unittest.skipUnless(HAVE_PANDOC, "pandoc not found on PATH")
class TestParseDocxChanges(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)

    def _build_with_comment(self, docx_path: Path):
        # comment-start の中身がコメント本文、comment-start と comment-end に
        # 挟まれた地の文がアンカー (make_tracked_md.py が出力する形式と同じ)。
        md = (
            "This is a paragraph with "
            '[Please check this wording.]{.comment-start id="1" author="Tester" '
            'date="2026-01-01T00:00:00Z"}a commented phrase[]{.comment-end id="1"} inside it.\n'
        )
        run_pandoc(md, docx_path)

    def _build_without_comment(self, docx_path: Path):
        """word/comments.xml エントリが本当に無い docx を作る (上の注意参照)。"""
        md = "This is a plain paragraph with no comments at all.\n"
        raw_path = docx_path.with_name(docx_path.stem + "_raw.docx")
        run_pandoc(md, raw_path)
        strip_comments_entry(raw_path, docx_path)
        with zipfile.ZipFile(docx_path) as z:
            assert "word/comments.xml" not in z.namelist()

    def test_one_arg_invocation_writes_next_to_docx(self):
        docx = self.tmp_path / "doc1.docx"
        self._build_with_comment(docx)
        run_parser(str(docx))
        report_json = self.tmp_path / "report.json"
        report_md = self.tmp_path / "report.md"
        self.assertTrue(report_json.exists())
        self.assertTrue(report_md.exists())
        data = json.loads(report_json.read_text(encoding="utf-8"))
        self.assertEqual(len(data["comments"]), 1)
        self.assertEqual(data["comments"][0]["anchor_text"], "a commented phrase")
        self.assertIn("paragraph_context", data["comments"][0])

    def test_two_arg_invocation_writes_into_report_dir(self):
        docx = self.tmp_path / "doc2.docx"
        self._build_with_comment(docx)
        report_dir = self.tmp_path / "out"
        run_parser(str(docx), str(report_dir))
        self.assertTrue((report_dir / "report.json").exists())
        self.assertFalse((self.tmp_path / "report.json").exists())

    def test_second_docx_without_comments_does_not_inherit_first(self):
        """A7: comments.xml を毎回 ZIP から直接読むので、コメント無し docx の
        後に前回のコメントが残らない。

        同じファイル名 (Google Docs から同じ名前で再ダウンロードする実運用) を
        使い回して上書きする。ファイル名が違うと、旧実装 (docx_path.stem ごとに
        別の <stem>_unzipped フォルダを作る) でもフォルダが分かれてしまい、
        このバグを再現できない。"""
        report_dir = self.tmp_path / "shared_report"
        docx_path = self.tmp_path / "manuscript.docx"

        self._build_with_comment(docx_path)
        run_parser(str(docx_path), str(report_dir))
        data1 = json.loads((report_dir / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data1["comments"]), 1)

        # 同じパスに、word/comments.xml エントリが本当に無い docx を上書きする
        self._build_without_comment(docx_path)
        run_parser(str(docx_path), str(report_dir))
        data2 = json.loads((report_dir / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data2["comments"]), 0)

    def test_no_stale_unzipped_folder_created(self):
        """A7: 再利用可能な <stem>_unzipped フォルダを作らない。"""
        docx = self.tmp_path / "doc3.docx"
        self._build_with_comment(docx)
        run_parser(str(docx))
        self.assertFalse((self.tmp_path / "doc3_unzipped").exists())


if __name__ == "__main__":
    unittest.main()
