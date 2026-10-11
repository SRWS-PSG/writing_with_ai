"""make_tracked_md.py のテスト。

ゴールデン (同梱フィクスチャの byte 比較 + pandoc 往復) と、
コードレビューで見つかった各バグ (A1-A8) の回帰テストからなる。
すべて tempfile ディレクトリの下だけに書き込む。
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "make_tracked_md.py"
FIXTURES = Path(__file__).resolve().parent

HAVE_PANDOC = shutil.which("pandoc") is not None

DEFAULT_AUTHOR = "Taro Yamada"
DEFAULT_DATE = "2026-09-12T00:00:00Z"


def _load_make_tracked_module():
    """関数単位のテスト (reconcile_not_carried など) のために、CLI スクリプトを
    モジュールとして import する。実行時に main() が動くのは
    __name__ == "__main__" のときだけなので import 自体に副作用はない。"""
    spec = importlib.util.spec_from_file_location("make_tracked_md", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MTM = _load_make_tracked_module()


# ---------------------------------------------------------------- helpers
def _env() -> dict:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    return env


def run_script(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=_env(),
    )


def make_tracked(
    tmp_path: Path,
    old_text: str,
    new_text: str,
    *,
    report: dict | None = None,
    responses: str | None = None,
    author: str = DEFAULT_AUTHOR,
    date: str = DEFAULT_DATE,
    skip_kind: str | None = None,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess:
    """old/new を書いて make_tracked_md.py を実行する。呼び出し側で returncode を見る。"""
    old_path = tmp_path / "old.md"
    new_path = tmp_path / "new.md"
    old_path.write_text(old_text, encoding="utf-8")
    new_path.write_text(new_text, encoding="utf-8")
    out_path = tmp_path / "tracked.md"
    args = [
        "--old", str(old_path),
        "--new", str(new_path),
        "--author", author,
        "--date", date,
        "--out", str(out_path),
    ]
    if report is not None:
        report_path = tmp_path / "report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
        args += ["--report", str(report_path)]
    if responses is not None:
        resp_path = tmp_path / "responses.md"
        resp_path.write_text(responses, encoding="utf-8")
        args += ["--responses", str(resp_path)]
    if skip_kind is not None:
        args += ["--skip-kind", skip_kind]
    if extra_args:
        args += list(extra_args)
    return run_script(args)


def pandoc_to_docx(md_path: Path, docx_path: Path) -> None:
    subprocess.run(["pandoc", str(md_path), "-o", str(docx_path)], check=True, capture_output=True)


def pandoc_plain(path: Path, track_changes: str | None = None) -> str:
    cmd = ["pandoc", str(path), "-t", "plain", "--wrap=none"]
    if track_changes:
        cmd.append(f"--track-changes={track_changes}")
    r = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8")
    return r.stdout


def pandoc_native(path: Path, track_changes: str | None = None) -> str:
    cmd = ["pandoc", str(path), "-t", "native"]
    if track_changes:
        cmd.append(f"--track-changes={track_changes}")
    r = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8")
    return r.stdout


def normalize(text: str) -> str:
    """round trip 比較用の正規化: '-'とスペースだけの行/空行を落とし、連続スペースを畳む。"""
    lines = []
    for line in text.splitlines():
        if re.fullmatch(r"[-\s]*", line):
            continue
        lines.append(re.sub(r" {2,}", " ", line).strip())
    return "\n".join(lines)


def assert_round_trip(test: unittest.TestCase, tracked_md: Path, old_md: Path, new_md: Path, tmp_path: Path) -> None:
    """tracked.md -> docx にして、accept が new 相当、reject が old 相当になることを
    pandoc 経由で確認する。図・表のレンダリング差を無くすため、比較相手の
    old/new も同じように docx を経由させてから plain 化する。"""
    tracked_docx = tmp_path / "tracked_rt.docx"
    old_docx = tmp_path / "old_rt.docx"
    new_docx = tmp_path / "new_rt.docx"
    pandoc_to_docx(tracked_md, tracked_docx)
    pandoc_to_docx(old_md, old_docx)
    pandoc_to_docx(new_md, new_docx)

    accept_actual = normalize(pandoc_plain(tracked_docx, "accept"))
    accept_expected = normalize(pandoc_plain(new_docx))
    test.assertEqual(accept_actual, accept_expected, "accept 後の本文が新版と一致しない")

    reject_actual = normalize(pandoc_plain(tracked_docx, "reject"))
    reject_expected = normalize(pandoc_plain(old_docx))
    test.assertEqual(reject_actual, reject_expected, "reject 後の本文が旧版と一致しない")


# ---------------------------------------------------------------- golden
class TestGoldenFixture(unittest.TestCase):
    def test_byte_compare_with_expected(self):
        with tempfile.TemporaryDirectory() as td:
            out_path = Path(td) / "tracked.md"
            proc = run_script([
                "--old", str(FIXTURES / "fixture_v1.md"),
                "--new", str(FIXTURES / "fixture_v2.md"),
                "--report", str(FIXTURES / "fixture_report.json"),
                "--responses", str(FIXTURES / "fixture_response_table.md"),
                "--author", DEFAULT_AUTHOR,
                "--date", DEFAULT_DATE,
                "--out", str(out_path),
            ])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            actual = out_path.read_text(encoding="utf-8")
            # git の autocrlf でチェックアウト時に改行が変わりうるので正規化してから比較する
            expected = (FIXTURES / "expected_tracked.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
            self.assertEqual(actual, expected)

    @unittest.skipUnless(HAVE_PANDOC, "pandoc not found on PATH")
    def test_golden_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            out_path = tmp_path / "tracked.md"
            proc = run_script([
                "--old", str(FIXTURES / "fixture_v1.md"),
                "--new", str(FIXTURES / "fixture_v2.md"),
                "--report", str(FIXTURES / "fixture_report.json"),
                "--responses", str(FIXTURES / "fixture_response_table.md"),
                "--author", DEFAULT_AUTHOR,
                "--date", DEFAULT_DATE,
                "--out", str(out_path),
            ])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            assert_round_trip(self, out_path, FIXTURES / "fixture_v1.md", FIXTURES / "fixture_v2.md", tmp_path)


# ---------------------------------------------------------------- A1
class TestA1EmphasisBoundary(unittest.TestCase):
    """強調記号が差分境界をまたぐ場合、壊れた span を出さずブロック丸ごと
    置換にフォールバックすること。"""

    def test_bold_crossing_diff_falls_back_to_whole_block(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_text = "Intro **old text** end.\n"
            new_text = "Intro **new text** end.\n"
            proc = make_tracked(tmp_path, old_text, new_text)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            # 壊れた部分置換 (**old / **new だけを span にする) になっていないこと
            self.assertNotIn("[**old]", out)
            self.assertNotIn("[**new]", out)
            # ブロック丸ごとの削除・挿入になっていること
            self.assertIn("[Intro **old text** end.]{.deletion", out)
            self.assertIn("[Intro **new text** end.]{.insertion", out)

    @unittest.skipUnless(HAVE_PANDOC, "pandoc not found on PATH")
    def test_bold_crossing_diff_round_trip_keeps_bold(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_text = "Intro **old text** end.\n"
            new_text = "Intro **new text** end.\n"
            proc = make_tracked(tmp_path, old_text, new_text)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out_path = tmp_path / "tracked.md"
            docx_path = tmp_path / "tracked.docx"
            pandoc_to_docx(out_path, docx_path)
            native = pandoc_native(docx_path, "accept")
            self.assertIn("Strong", native)
            plain = pandoc_plain(docx_path, "accept")
            self.assertNotIn("*", plain)
            self.assertIn("new text", plain)


# ---------------------------------------------------------------- A2
class TestA2Comments(unittest.TestCase):
    def test_comment_in_unchanged_table_not_carried(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            table = (
                "| Step | Tool |\n"
                "|------|------|\n"
                "| Draft | IDE |\n"
            )
            old_text = f"Intro paragraph.\n\n{table}\nEnd paragraph.\n"
            new_text = old_text  # 表は変更なし
            report = {"comments": [
                {"id": "1", "author": "R", "date": DEFAULT_DATE, "text": "表について",
                 "anchor_text": "Draft"},
            ]}
            proc = make_tracked(tmp_path, old_text, new_text, report=report)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            self.assertNotIn("comment-start", out)
            summary = (tmp_path / "tracked.md.summary.md").read_text(encoding="utf-8")
            self.assertIn("ID 1", summary)
            # 表がそのまま (壊れずに) 出力されていること
            self.assertIn("| Draft | IDE |", out)
            if HAVE_PANDOC:
                docx_path = tmp_path / "t.docx"
                pandoc_to_docx(tmp_path / "tracked.md", docx_path)
                native = pandoc_native(docx_path)
                self.assertIn("Table", native)

    def test_comment_in_changed_table_not_carried(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_table = "| Step | Tool |\n|------|------|\n| Draft | IDE |\n"
            new_table = "| Step | Tool |\n|------|------|\n| Draft | IDE + AI |\n"
            old_text = f"Intro paragraph.\n\n{old_table}\nEnd paragraph.\n"
            new_text = f"Intro paragraph.\n\n{new_table}\nEnd paragraph.\n"
            report = {"comments": [
                {"id": "1", "author": "R", "date": DEFAULT_DATE, "text": "表について",
                 "anchor_text": "Draft"},
            ]}
            proc = make_tracked(tmp_path, old_text, new_text, report=report)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            self.assertNotIn("comment-start", out)
            summary = (tmp_path / "tracked.md.summary.md").read_text(encoding="utf-8")
            self.assertIn("ID 1", summary)

    def test_duplicate_anchor_without_context_not_carried(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_text = "First paragraph mentions apple pie.\n\nSecond paragraph also mentions apple pie.\n"
            new_text = old_text
            report = {"comments": [
                {"id": "1", "author": "R", "date": DEFAULT_DATE, "text": "曖昧",
                 "anchor_text": "apple pie"},
            ]}
            proc = make_tracked(tmp_path, old_text, new_text, report=report)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            self.assertNotIn("comment-start", out)
            summary = (tmp_path / "tracked.md.summary.md").read_text(encoding="utf-8")
            self.assertIn("ID 1", summary)
            self.assertIn("一意に特定できません", summary)

    def test_duplicate_anchor_with_disambiguating_context_carried(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_text = "First paragraph mentions apple pie.\n\nSecond paragraph also mentions apple pie.\n"
            new_text = old_text
            report = {"comments": [
                {"id": "1", "author": "R", "date": DEFAULT_DATE, "text": "二番目の方",
                 "anchor_text": "apple pie",
                 "paragraph_context": "Second paragraph also mentions apple pie."},
            ]}
            proc = make_tracked(tmp_path, old_text, new_text, report=report)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            self.assertIn('.comment-start id="1"', out)
            self.assertIn("Second paragraph also mentions", out)
            summary = (tmp_path / "tracked.md.summary.md").read_text(encoding="utf-8")
            self.assertIn("文書に載せたコメント: 1 件", summary)


# ---------------------------------------------------------------- A3
class TestA3DeletedUntrackableBlocks(unittest.TestCase):
    def test_deleted_yaml_front_matter_not_output(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_text = '---\ntitle: "Old title"\n---\n\nBody paragraph.\n'
            new_text = "Body paragraph.\n"
            proc = make_tracked(tmp_path, old_text, new_text)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            self.assertNotIn("Old title", out)
            summary = (tmp_path / "tracked.md.summary.md").read_text(encoding="utf-8")
            self.assertIn("削除されたが追跡できず出力から除外したブロック", summary)

    def test_deleted_fenced_code_block_not_output(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_text = "Body paragraph.\n\n```python\nsecret_value = 42\n```\n\nTail paragraph.\n"
            new_text = "Body paragraph.\n\nTail paragraph.\n"
            proc = make_tracked(tmp_path, old_text, new_text)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            self.assertNotIn("secret_value", out)
            summary = (tmp_path / "tracked.md.summary.md").read_text(encoding="utf-8")
            self.assertIn("削除されたが追跡できず出力から除外したブロック", summary)


# ---------------------------------------------------------------- A4
class TestA4OrderPreservingPairing(unittest.TestCase):
    def test_reorder_reject_keeps_old_order_accept_keeps_new_order(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_text = "Alpha para one.\n\nBeta para two.\n"
            new_text = "Beta para two, revised.\n\nAlpha para one, revised.\n"
            proc = make_tracked(tmp_path, old_text, new_text)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out_path = tmp_path / "tracked.md"
            if HAVE_PANDOC:
                docx_path = tmp_path / "t.docx"
                pandoc_to_docx(out_path, docx_path)
                reject_plain = pandoc_plain(docx_path, "reject")
                accept_plain = pandoc_plain(docx_path, "accept")
                self.assertLess(
                    reject_plain.find("Alpha para one."), reject_plain.find("Beta para two.")
                )
                self.assertLess(
                    accept_plain.find("Beta para two, revised."),
                    accept_plain.find("Alpha para one, revised."),
                )
                assert_round_trip(self, out_path, tmp_path / "old.md", tmp_path / "new.md", tmp_path)


# ---------------------------------------------------------------- A5
class TestA5Robustness(unittest.TestCase):
    def test_attribute_escaping(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_text = "Foo bar baz.\n"
            new_text = "Foo qux baz.\n"
            proc = make_tracked(tmp_path, old_text, new_text, author='A "B" \\C')
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            self.assertIn('author="A \\"B\\" \\\\C"', out)
            if HAVE_PANDOC:
                docx_path = tmp_path / "t.docx"
                pandoc_to_docx(tmp_path / "tracked.md", docx_path)
                native = pandoc_native(docx_path, "all")
                self.assertIn('"insertion"', native)
                self.assertIn('"deletion"', native)
                plain = pandoc_plain(docx_path)
                self.assertNotIn('"B"', plain)  # 属性値の文字列が地の文に漏れ出していない

    def test_missing_report_file_errors(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_path = tmp_path / "old.md"
            new_path = tmp_path / "new.md"
            old_path.write_text("Foo.\n", encoding="utf-8")
            new_path.write_text("Bar.\n", encoding="utf-8")
            proc = run_script([
                "--old", str(old_path), "--new", str(new_path),
                "--report", str(tmp_path / "missing_report.json"),
                "--out", str(tmp_path / "tracked.md"),
            ])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("report", proc.stderr)

    def test_missing_responses_file_errors(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_path = tmp_path / "old.md"
            new_path = tmp_path / "new.md"
            old_path.write_text("Foo.\n", encoding="utf-8")
            new_path.write_text("Bar.\n", encoding="utf-8")
            proc = run_script([
                "--old", str(old_path), "--new", str(new_path),
                "--responses", str(tmp_path / "missing_responses.md"),
                "--out", str(tmp_path / "tracked.md"),
            ])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("responses", proc.stderr)

    def test_response_table_missing_required_column_errors(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            report = {"comments": [
                {"id": "1", "author": "R", "date": DEFAULT_DATE, "text": "t", "anchor_text": "Foo"},
            ]}
            responses = "| ID | メモ |\n|----|------|\n| 1 | hello |\n"
            proc = make_tracked(tmp_path, "Foo.\n", "Bar.\n", report=report, responses=responses)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("必須列", proc.stderr)

    def test_response_table_duplicate_id_errors(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            report = {"comments": [
                {"id": "1", "author": "R", "date": DEFAULT_DATE, "text": "t", "anchor_text": "Foo"},
            ]}
            responses = (
                "| ID | 区分 | 対応 | 返答 |\n"
                "|----|------|------|------|\n"
                "| 1 | 内容 | 修正 | ok |\n"
                "| 1 | 内容 | 修正 | ok again |\n"
            )
            proc = make_tracked(tmp_path, "Foo.\n", "Bar.\n", report=report, responses=responses)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("重複", proc.stderr)

    def test_response_table_unknown_id_errors(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            report = {"comments": [
                {"id": "1", "author": "R", "date": DEFAULT_DATE, "text": "t", "anchor_text": "Foo"},
            ]}
            responses = (
                "| ID | 区分 | 対応 | 返答 |\n"
                "|----|------|------|------|\n"
                "| 1 | 内容 | 修正 | ok |\n"
                "| 99 | 内容 | 修正 | 存在しない |\n"
            )
            proc = make_tracked(tmp_path, "Foo.\n", "Bar.\n", report=report, responses=responses)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("99", proc.stderr)

    def test_report_comment_without_row_errors(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            report = {"comments": [
                {"id": "1", "author": "R", "date": DEFAULT_DATE, "text": "t", "anchor_text": "Foo"},
                {"id": "2", "author": "R", "date": DEFAULT_DATE, "text": "t2", "anchor_text": "Bar"},
            ]}
            responses = (
                "| ID | 区分 | 対応 | 返答 |\n"
                "|----|------|------|------|\n"
                "| 1 | 内容 | 修正 | ok |\n"
            )
            proc = make_tracked(tmp_path, "Foo.\n", "Bar.\n", report=report, responses=responses)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("2", proc.stderr)

    def test_non_typo_row_with_empty_reply_errors(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            report = {"comments": [
                {"id": "1", "author": "R", "date": DEFAULT_DATE, "text": "t", "anchor_text": "Foo"},
            ]}
            responses = (
                "| ID | 区分 | 対応 | 返答 |\n"
                "|----|------|------|------|\n"
                "| 1 | 内容 | 修正 |  |\n"
            )
            proc = make_tracked(tmp_path, "Foo.\n", "Bar.\n", report=report, responses=responses)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("返答", proc.stderr)

    def test_typo_row_with_fix_action_and_empty_reply_is_skipped_not_error(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            report = {"comments": [
                {"id": "1", "author": "R", "date": DEFAULT_DATE, "text": "typo fix", "anchor_text": "Foo"},
            ]}
            responses = (
                "| ID | 区分 | 対応 | 返答 |\n"
                "|----|------|------|------|\n"
                "| 1 | typo | 修正 |  |\n"
            )
            proc = make_tracked(tmp_path, "Foo.\n", "Bar.\n", report=report, responses=responses)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            summary = (tmp_path / "tracked.md.summary.md").read_text(encoding="utf-8")
            self.assertIn("ID 1", summary)

    def test_typo_row_with_non_fix_action_is_carried(self):
        """typo 区分でも 対応 が「修正」以外なら、通常のコメントとして載せる。"""
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_text = "The value shoud be checked.\n"
            new_text = old_text
            report = {"comments": [
                {"id": "1", "author": "R", "date": DEFAULT_DATE, "text": "typo: should",
                 "anchor_text": "shoud"},
            ]}
            responses = (
                "| ID | 区分 | 対応 | 返答 |\n"
                "|----|------|------|------|\n"
                "| 1 | typo | 確認中 | まだ直していません |\n"
            )
            proc = make_tracked(tmp_path, old_text, new_text, report=report, responses=responses)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            self.assertIn('.comment-start id="1"', out)

    def test_pipe_escape_in_response_table_cell(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            report = {"comments": [
                {"id": "1", "author": "R", "date": DEFAULT_DATE, "text": "t", "anchor_text": "Foo"},
            ]}
            responses = (
                "| ID | 区分 | 対応 | 返答 |\n"
                "|----|------|------|------|\n"
                r"| 1 | 内容 | 修正 | a \| b |" "\n"
            )
            proc = make_tracked(tmp_path, "Foo.\n", "Bar.\n", report=report, responses=responses)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            self.assertIn("a | b", out)

    def test_reply_ids_avoid_collision_with_high_report_ids(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            report = {"comments": [
                {"id": "2500", "author": "R", "date": DEFAULT_DATE, "text": "t", "anchor_text": "Foo"},
            ]}
            responses = (
                "| ID | 区分 | 対応 | 返答 |\n"
                "|----|------|------|------|\n"
                "| 2500 | 内容 | 修正 | done |\n"
            )
            proc = make_tracked(tmp_path, "Foo.\n", "Bar.\n", report=report, responses=responses)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            self.assertNotIn('id="2500"' + "000", out)  # 変な連結が起きていないことの簡易チェック
            self.assertIn('id="3000"', out)
            self.assertNotIn('id="1000"', out)


# ---------------------------------------------------------------- A6
class TestA6HardBreakAndLineEndings(unittest.TestCase):
    def test_hard_break_preserved_and_lf_output(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_text = "Line one.  \nLine two continues.\n"
            new_text = "Line one, revised.  \nLine two continues.\n"
            proc = make_tracked(tmp_path, old_text, new_text)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out_path = tmp_path / "tracked.md"
            raw = out_path.read_bytes()
            self.assertNotIn(b"\r\n", raw)
            summary_path = tmp_path / "tracked.md.summary.md"
            self.assertNotIn(b"\r\n", summary_path.read_bytes())
            if HAVE_PANDOC:
                docx_path = tmp_path / "t.docx"
                pandoc_to_docx(out_path, docx_path)
                native = pandoc_native(docx_path, "accept")
                self.assertIn("LineBreak", native)


# ---------------------------------------------------------------- A8
class TestA8WhitespaceAtSpanEdges(unittest.TestCase):
    def test_leading_trailing_whitespace_outside_span(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_text = "Heading text here.\n"
            new_text = "Heading text here plus more.\n"
            proc = make_tracked(tmp_path, old_text, new_text)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            # 挿入 span の中身が空白で始まっていないこと (外に出ているはず)
            for mm in re.finditer(r"\[([^\]]*)\]\{\.insertion[^}]*\}", out):
                content = mm.group(1)
                if content.strip():
                    self.assertEqual(content, content.strip(), f"span 内に空白が残っている: {content!r}")

    @unittest.skipUnless(HAVE_PANDOC, "pandoc not found on PATH")
    def test_whitespace_survives_docx_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_text = "# Objective\n\nBody text.\n"
            new_text = "# Objective and scope\n\nBody text.\n"
            proc = make_tracked(tmp_path, old_text, new_text)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out_path = tmp_path / "tracked.md"
            docx_path = tmp_path / "t.docx"
            pandoc_to_docx(out_path, docx_path)
            plain = pandoc_plain(docx_path, "accept")
            self.assertIn("Objective and scope", plain)
            self.assertNotIn("Objectiveand", plain)


# ---------------------------------------------------------------- own-comment exclusion
class TestOwnCommentExclusion(unittest.TestCase):
    """ラウンド2以降、report.json には前回自分が書いた返信コメントも混ざって
    返ってくる。既定ではそれらを除外し、--include-own-comments で無効化できる。"""

    def _report_with_own_and_others(self):
        return {
            "comments": [
                {"id": "1", "author": "Reviewer B", "date": DEFAULT_DATE,
                 "text": "レビュアーのコメント", "anchor_text": "Foo"},
                {"id": "2", "author": DEFAULT_AUTHOR, "date": DEFAULT_DATE,
                 "text": "前ラウンドで自分が書いた返信", "anchor_text": "Bar"},
            ]
        }

    def test_own_comment_excluded_by_default_no_row_needed(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            report = self._report_with_own_and_others()
            # id "2" (自分のコメント) の行は response_table に無いが、
            # 既定では検証対象外になるのでエラーにならないはず。
            responses = (
                "| ID | 区分 | 対応 | 返答 |\n"
                "|----|------|------|------|\n"
                "| 1 | 内容 | 修正 | 対応しました |\n"
            )
            old_text = "Foo appears here. Bar appears here too.\n"
            new_text = old_text
            proc = make_tracked(tmp_path, old_text, new_text, report=report, responses=responses)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            self.assertIn('.comment-start id="1"', out)
            self.assertNotIn('.comment-start id="2"', out)
            summary = (tmp_path / "tracked.md.summary.md").read_text(encoding="utf-8")
            self.assertIn("自分のコメントとして除外: 1 件 → ID 2", summary)

    def test_own_comment_included_with_flag_requires_row(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            report = self._report_with_own_and_others()
            responses = (
                "| ID | 区分 | 対応 | 返答 |\n"
                "|----|------|------|------|\n"
                "| 1 | 内容 | 修正 | 対応しました |\n"
            )
            old_text = "Foo appears here. Bar appears here too.\n"
            new_text = old_text
            proc = make_tracked(
                tmp_path, old_text, new_text, report=report, responses=responses,
                extra_args=["--include-own-comments"],
            )
            # --include-own-comments を付けると、自分のコメント (id 2) も
            # 通常のコメントとして検証対象になり、行が無いのでエラーになる。
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("2", proc.stderr)

    def test_own_comment_included_with_flag_and_row_is_carried(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            report = self._report_with_own_and_others()
            responses = (
                "| ID | 区分 | 対応 | 返答 |\n"
                "|----|------|------|------|\n"
                "| 1 | 内容 | 修正 | 対応しました |\n"
                "| 2 | 内容 | 修正 | 自分の返信にも対応 |\n"
            )
            old_text = "Foo appears here. Bar appears here too.\n"
            new_text = old_text
            proc = make_tracked(
                tmp_path, old_text, new_text, report=report, responses=responses,
                extra_args=["--include-own-comments"],
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            self.assertIn('.comment-start id="1"', out)
            self.assertIn('.comment-start id="2"', out)
            summary = (tmp_path / "tracked.md.summary.md").read_text(encoding="utf-8")
            self.assertIn("自分のコメントとして除外: 0 件", summary)


# ---------------------------------------------------------------- safety net (reconciliation)
class TestReconcileNotCarried(unittest.TestCase):
    """summary からコメントが理由なく消えないための安全網 reconcile_not_carried()
    を関数単位で検証する。

    レビューで指摘された「carried_ids にも not_carried にも無いコメントが
    黙って消える」経路は、A2 の修正 (アンカー付けの時点で表・コード/生
    HTML/YAML ブロックを除外し、資格を得たコメントは必ずどこかの block
    出力で comment-start/comment-end が emit される) によって、現状の
    main() のロジックからは実際には到達できないことを確認した (下記の
    エンドツーエンド確認テストを参照)。そのため、この安全網そのものは
    関数単位のテストで検証し、「本当に踏める入力」をでっち上げない。"""

    def test_adds_missing_id_with_reason(self):
        comments = [{"id": "7", "author": "R"}]
        not_carried: list[dict] = []
        MTM.reconcile_not_carried(comments, carried_ids=set(), skipped_ids=set(), not_carried=not_carried)
        self.assertEqual(len(not_carried), 1)
        self.assertEqual(not_carried[0]["id"], "7")
        self.assertIn("出力に含まれませんでした", not_carried[0]["reason"])

    def test_does_not_duplicate_already_listed_id(self):
        comments = [{"id": "7", "author": "R"}]
        not_carried = [{"id": "7", "reason": "既存の理由"}]
        MTM.reconcile_not_carried(comments, carried_ids=set(), skipped_ids=set(), not_carried=not_carried)
        self.assertEqual(len(not_carried), 1)
        self.assertEqual(not_carried[0]["reason"], "既存の理由")

    def test_skips_skipped_and_carried_ids(self):
        comments = [
            {"id": "1", "author": "R"},  # skipped
            {"id": "2", "author": "R"},  # carried
            {"id": "3", "author": "R"},  # 本当に漏れているもの
        ]
        not_carried: list[dict] = []
        MTM.reconcile_not_carried(
            comments, carried_ids={"2"}, skipped_ids={"1"}, not_carried=not_carried
        )
        self.assertEqual([item["id"] for item in not_carried], ["3"])

    def test_end_to_end_current_pipeline_never_triggers_safety_net(self):
        """調査結果の記録: 現行 main() のパイプラインでは、アンカー付けに
        成功したコメントが carried_ids からも not_carried からも漏れる
        経路が無いことを、ゴールデンフィクスチャで確認する (安全網が
        何もしなかったことを summary の件数から確認する)。"""
        with tempfile.TemporaryDirectory() as td:
            out_path = Path(td) / "tracked.md"
            proc = run_script([
                "--old", str(FIXTURES / "fixture_v1.md"),
                "--new", str(FIXTURES / "fixture_v2.md"),
                "--report", str(FIXTURES / "fixture_report.json"),
                "--responses", str(FIXTURES / "fixture_response_table.md"),
                "--author", DEFAULT_AUTHOR,
                "--date", DEFAULT_DATE,
                "--out", str(out_path),
            ])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            summary = (Path(td) / "tracked.md.summary.md").read_text(encoding="utf-8")
            self.assertIn("載せなかったコメント (位置を特定できない): 0 件", summary)


# ---------------------------------------------------------------- review bug 1: escaped pipes
class TestReviewBug1EscapedPipeInTable(unittest.TestCase):
    """`A \\| B` のようにエスケープされた `|` を含むセルが、単純な `.split("|")`
    で余分な列に割れてデータを失わないこと。"""

    def test_escaped_pipe_cell_round_trip_and_value_present(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_table = (
                "| Col1 | Col2 |\n"
                "|------|------|\n"
                r"| A \| B | old value |" "\n"
            )
            new_table = (
                "| Col1 | Col2 |\n"
                "|------|------|\n"
                r"| A \| B | new value |" "\n"
            )
            old_text = f"Intro paragraph.\n\n{old_table}\nEnd paragraph.\n"
            new_text = f"Intro paragraph.\n\n{new_table}\nEnd paragraph.\n"
            proc = make_tracked(tmp_path, old_text, new_text)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            # エスケープされた | を含むセルが壊れず、他方のセルの変更後の値が残っていること
            self.assertIn(r"A \| B", out)
            if HAVE_PANDOC:
                out_path = tmp_path / "tracked.md"
                docx_path = tmp_path / "t.docx"
                pandoc_to_docx(out_path, docx_path)
                accept_plain = pandoc_plain(docx_path, "accept")
                reject_plain = pandoc_plain(docx_path, "reject")
                self.assertIn("new value", accept_plain)
                self.assertIn("A | B", accept_plain)
                self.assertIn("old value", reject_plain)
                self.assertIn("A | B", reject_plain)
                assert_round_trip(
                    self, out_path, tmp_path / "old.md", tmp_path / "new.md", tmp_path
                )


# ---------------------------------------------------------------- review bug 2: inline code
class TestReviewBug2InlineCodeAtomic(unittest.TestCase):
    """インラインコードスパンの内部で差分境界やコメント境界が切れて、
    span マークアップがコード内容としてそのまま出力されないこと。"""

    @unittest.skipUnless(HAVE_PANDOC, "pandoc not found on PATH")
    def test_change_inside_inline_code_round_trips_without_literal_markup(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_text = "Use `alpha beta gamma` here.\n"
            new_text = "Use `alpha delta gamma` here.\n"
            proc = make_tracked(tmp_path, old_text, new_text)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out_path = tmp_path / "tracked.md"
            docx_path = tmp_path / "t.docx"
            pandoc_to_docx(out_path, docx_path)
            accept_plain = pandoc_plain(docx_path, "accept")
            self.assertNotIn("insertion", accept_plain)
            self.assertNotIn("deletion", accept_plain)
            self.assertNotIn("{.", accept_plain)
            self.assertIn("alpha delta gamma", accept_plain)
            reject_plain = pandoc_plain(docx_path, "reject")
            self.assertNotIn("insertion", reject_plain)
            self.assertNotIn("deletion", reject_plain)
            self.assertNotIn("{.", reject_plain)
            self.assertIn("alpha beta gamma", reject_plain)

    def test_comment_anchored_inside_inline_code_produces_no_literal_markup(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            old_text = "Use `alpha beta gamma` here.\n"
            new_text = old_text
            report = {"comments": [
                {"id": "1", "author": "R", "date": DEFAULT_DATE, "text": "about beta",
                 "anchor_text": "beta"},
            ]}
            proc = make_tracked(tmp_path, old_text, new_text, report=report)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            # コード スパン自体は無傷のまま出力されていること (中に comment-start/end が
            # 割り込んでいない)
            self.assertIn("`alpha beta gamma`", out)
            if HAVE_PANDOC:
                docx_path = tmp_path / "t.docx"
                pandoc_to_docx(tmp_path / "tracked.md", docx_path)
                plain = pandoc_plain(docx_path)
                self.assertNotIn("comment-start", plain)
                self.assertNotIn("{.", plain)
                self.assertIn("alpha beta gamma", plain)


# ---------------------------------------------------------------- review bug 3: comment in table
class TestReviewBug3CommentAnchorAlsoInTable(unittest.TestCase):
    """アンカーが表セルにも段落にも一致する場合、表側を数え損ねて段落側に
    誤って乗せないこと。"""

    def test_anchor_in_table_and_paragraph_not_carried(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            table = (
                "| Setting | Value |\n"
                "|---------|-------|\n"
                "| Control | 5 |\n"
            )
            old_text = f"The system uses Control feedback for tuning.\n\n{table}\nEnd.\n"
            new_text = old_text
            report = {"comments": [
                {"id": "1", "author": "R", "date": DEFAULT_DATE, "text": "which Control?",
                 "anchor_text": "Control"},
            ]}
            proc = make_tracked(tmp_path, old_text, new_text, report=report)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            self.assertNotIn("comment-start", out)
            summary = (tmp_path / "tracked.md.summary.md").read_text(encoding="utf-8")
            self.assertIn("ID 1", summary)
            self.assertIn("表内", summary)


# ---------------------------------------------------------------- review bug 4: repeated anchor
class TestReviewBug4RepeatedAnchorContextMatch(unittest.TestCase):
    """anchor がその段落内で複数回出現していても、paragraph_context が
    その段落と厳密に一致するなら、類似した別の段落 (出現1回) に誤って
    乗せないこと (乗せられないなら、乗せずに諦める)。"""

    def test_context_matches_paragraph_with_repeated_anchor_not_carried_elsewhere(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            para_a = "Alpha Control mentions Control twice here."
            para_b = "Beta Control mentions something else nearby."
            old_text = f"{para_a}\n\n{para_b}\n"
            new_text = old_text
            report = {"comments": [
                {"id": "1", "author": "R", "date": DEFAULT_DATE, "text": "which one?",
                 "anchor_text": "Control", "paragraph_context": para_a},
            ]}
            proc = make_tracked(tmp_path, old_text, new_text, report=report)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            self.assertNotIn("comment-start", out)
            summary = (tmp_path / "tracked.md.summary.md").read_text(encoding="utf-8")
            self.assertIn("ID 1", summary)


# ---------------------------------------------------------------- review bug 5: heading + body
class TestReviewBug5HeadingImmediatelyFollowedByBody(unittest.TestCase):
    """ATX 見出し行の直後 (空行なし) に本文行が続く場合、見出しと本文が
    1つの段落に結合されて丸ごと見出しとしてレンダリングされないこと。"""

    def test_heading_and_body_stay_separate_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            text = "# Introduction\nBody text right after heading.\n"
            proc = make_tracked(tmp_path, text, text)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out_path = tmp_path / "tracked.md"
            out = out_path.read_text(encoding="utf-8")
            self.assertIn("# Introduction\n\nBody text right after heading.", out)
            if HAVE_PANDOC:
                native_accept = pandoc_native(out_path, "accept")
                self.assertIn("Header", native_accept)
                self.assertIn("Para", native_accept)
                native_reject = pandoc_native(out_path, "reject")
                self.assertIn("Header", native_reject)
                self.assertIn("Para", native_reject)


# ---------------------------------------------------------------- row-match (label pairing)
class TestRowMatchLabelPairing(unittest.TestCase):
    """diff_table() の行対応付け。以前は行数が同じ replace ハンクを位置で
    対応付けていたため、1行削除して他の行の値も変わっただけで、削除行が
    別の行に「書き換わった」ように見えていた (medical-safety PR #60 の
    shared/docx_redline.py の移植元と同じ不具合)。label モード (既定) は
    先頭のラベル列で行を対応付け、text モードは旧来の挙動を再現する。"""

    OLD_TABLE = (
        "| Group | Setting | OR |\n"
        "|---|---|---|\n"
        "| Age | UE | 1.2 |\n"
        "| Age | night | 1.5 |\n"
        "| Sex | male | 0.9 |"
    )
    NEW_TABLE = (
        "| Group | Setting | OR |\n"
        "|---|---|---|\n"
        "| Age | night | 1.6 |\n"
        "| Sex | male | 0.8 |\n"
        "| Sex | female | 1.1 |"
    )

    def test_deleted_row_label_pairing_default(self):
        m = MTM.Marks(DEFAULT_AUTHOR, DEFAULT_DATE)
        out = MTM.diff_table(self.OLD_TABLE, self.NEW_TABLE, m)
        self.assertIsNotNone(out)
        # Age|UE|1.2 は丸ごと削除される (別の行への書き換えに見えない)
        self.assertIn(
            '| [Age]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | '
            '[UE]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | '
            '[1.2]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"} |',
            out,
        )
        # Age|night は残り、OR 列だけがセル差分される
        self.assertIn(
            '| Age | night | [1.5]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"}'
            '[1.6]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} |',
            out,
        )
        # Sex|male は残り、OR 列だけがセル差分される
        self.assertIn(
            '| Sex | male | [0.9]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"}'
            '[0.8]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} |',
            out,
        )
        # Sex|female|1.1 は丸ごと挿入される
        self.assertIn(
            '| [Sex]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | '
            '[female]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | '
            '[1.1]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} |',
            out,
        )
        # 削除セル3 + 部分差分2 = 5、挿入セル3 + 部分差分2 = 5 で数が揃う
        self.assertEqual(out.count(".deletion"), 5)
        self.assertEqual(out.count(".insertion"), 5)

    @unittest.skipUnless(HAVE_PANDOC, "pandoc not found on PATH")
    def test_deleted_row_label_pairing_accept_reject_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            proc = make_tracked(tmp_path, self.OLD_TABLE + "\n", self.NEW_TABLE + "\n")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out_path = tmp_path / "tracked.md"
            assert_round_trip(
                self, out_path, tmp_path / "old.md", tmp_path / "new.md", tmp_path
            )

    def test_text_mode_reproduces_old_positional_pairing(self):
        m = MTM.Marks(DEFAULT_AUTHOR, DEFAULT_DATE)
        out = MTM.diff_table(self.OLD_TABLE, self.NEW_TABLE, m, row_match="text")
        # 旧来の挙動: 行数が同じ (3 行 -> 3 行) replace ハンクなので、位置で
        # 対応付けられ、Age|UE|1.2 の行そのものが Age|night... へセル差分される
        self.assertIn(
            '| Age | [UE]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"}'
            '[night]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | '
            '[1.2]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"}'
            '[1.6]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} |',
            out,
        )
        # デフォルト (label) の出力とは異なること
        label_out = MTM.diff_table(self.OLD_TABLE, self.NEW_TABLE, m, row_match="label")
        self.assertNotEqual(out, label_out)

    def test_cli_row_match_text_flag_matches_direct_call(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            proc = make_tracked(
                tmp_path,
                self.OLD_TABLE + "\n",
                self.NEW_TABLE + "\n",
                extra_args=["--row-match", "text"],
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            out = (tmp_path / "tracked.md").read_text(encoding="utf-8")
            m = MTM.Marks(DEFAULT_AUTHOR, DEFAULT_DATE)
            expected = MTM.diff_table(self.OLD_TABLE, self.NEW_TABLE, m, row_match="text")
            for line in expected.split("\n"):
                self.assertIn(line, out)

    def test_header_cell_change_is_cell_diffed(self):
        old_table = "| Group | Setting | OR |\n|---|---|---|\n| Age | UE | 1.2 |"
        new_table = "| Group | Setting | OR (95% CI) |\n|---|---|---|\n| Age | UE | 1.2 |"
        m = MTM.Marks(DEFAULT_AUTHOR, DEFAULT_DATE)
        out = MTM.diff_table(old_table, new_table, m)
        self.assertIsNotNone(out)
        self.assertIn(
            '| Group | Setting | OR [(95% CI)]{.insertion author="Taro Yamada" '
            'date="2026-09-12T00:00:00Z"} |',
            out,
        )
        # データ行は変更なしのまま
        self.assertIn("| Age | UE | 1.2 |", out.split("\n")[-1])

    def test_header_column_count_change_falls_back_to_whole_table(self):
        old_table = "| Group | Setting | OR |\n|---|---|---|\n| Age | UE | 1.2 |"
        new_table = "| Group | Setting | OR | Notes |\n|---|---|---|---|\n| Age | UE | 1.2 | ok |"
        m = MTM.Marks(DEFAULT_AUTHOR, DEFAULT_DATE)
        self.assertIsNone(MTM.diff_table(old_table, new_table, m))

    def test_row_column_count_change_falls_back_to_row_delete_insert(self):
        old_table = (
            "| Group | Setting | OR |\n"
            "|---|---|---|\n"
            "| Age | UE | 1.2 |\n"
            "| Sex | male | 0.9 |"
        )
        new_table = (
            "| Group | Setting | OR |\n"
            "|---|---|---|\n"
            "| Age | UE | 1.2 | extra |\n"
            "| Sex | male | 0.8 |"
        )
        m = MTM.Marks(DEFAULT_AUTHOR, DEFAULT_DATE)
        out = MTM.diff_table(old_table, new_table, m)
        self.assertIsNotNone(out)
        # 列数が変わった Age 行は丸ごと削除+挿入 (表全体のフォールバックにはならない)
        self.assertIn(
            '| [Age]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | '
            '[UE]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | '
            '[1.2]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"} |',
            out,
        )
        self.assertIn(
            '| [Age]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | '
            '[UE]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | '
            '[1.2]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | '
            '[extra]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} |',
            out,
        )
        # 影響を受けない Sex 行はセル単位で差分される (表全体が失われていない)
        self.assertIn(
            '| Sex | male | [0.9]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"}'
            '[0.8]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} |',
            out,
        )

    def test_label_width_one_when_second_column_numeric(self):
        old_cells = [["Age", "1.2"], ["Age", "1.5"], ["Sex", "0.9"]]
        new_cells = [["Age", "1.6"], ["Sex", "0.8"]]
        self.assertEqual(MTM._table_label_width(old_cells, new_cells), 1)

    def test_label_width_two_when_second_column_non_numeric(self):
        old_cells = [["Age", "UE"], ["Age", "night"], ["Sex", "male"]]
        new_cells = [["Age", "night"], ["Sex", "male"]]
        self.assertEqual(MTM._table_label_width(old_cells, new_cells), 2)

    def test_duplicate_label_unchanged_rows_stay_anchored(self):
        # ラベル列だけで対応付けると、Age|Age|Sex -> Age|Sex の最長一致は
        # old[1:3]<->new[0:2] になり、Age|1.2 が削除・1.5->1.2 のセル差分に
        # 見えてしまう (キー単位のみのマッチングの回帰)。行全体テキストで
        # まず一致行をアンカーにすれば、不変の Age|1.2 と Sex|0.9 は残り、
        # 変化した行 (Age|1.5) だけが丸ごと削除される。
        old_table = "| Group | OR |\n|---|---|\n| Age | 1.2 |\n| Age | 1.5 |\n| Sex | 0.9 |"
        new_table = "| Group | OR |\n|---|---|\n| Age | 1.2 |\n| Sex | 0.9 |"
        m = MTM.Marks(DEFAULT_AUTHOR, DEFAULT_DATE)
        out = MTM.diff_table(old_table, new_table, m)
        self.assertIsNotNone(out)
        self.assertIn("| Age | 1.2 |", out)
        self.assertIn("| Sex | 0.9 |", out)
        self.assertIn(
            '| [Age]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"} | '
            '[1.5]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"} |',
            out,
        )
        self.assertEqual(out.count(".insertion"), 0)
        self.assertEqual(out.count(".deletion"), 2)

    def test_duplicate_label_with_changed_value_still_cell_diffed(self):
        # 重複ラベル (Age, Age, Sex) に加えて実際の値変更 (1.5 -> 1.6) が
        # 混在する場合でも、不変の2行はアンカーとして残り、変化した行だけが
        # セル差分される。
        old_table = (
            "| Group | OR |\n|---|---|\n| Age | 1.2 |\n| Age | 1.5 |\n| Sex | 0.9 |"
        )
        new_table = (
            "| Group | OR |\n|---|---|\n| Age | 1.2 |\n| Age | 1.6 |\n| Sex | 0.9 |"
        )
        m = MTM.Marks(DEFAULT_AUTHOR, DEFAULT_DATE)
        out = MTM.diff_table(old_table, new_table, m)
        self.assertIsNotNone(out)
        self.assertIn("| Age | 1.2 |", out)
        self.assertIn("| Sex | 0.9 |", out)
        self.assertIn(
            '| Age | [1.5]{.deletion author="Taro Yamada" date="2026-09-12T00:00:00Z"}'
            '[1.6]{.insertion author="Taro Yamada" date="2026-09-12T00:00:00Z"} |',
            out,
        )
        self.assertEqual(out.count(".deletion"), 1)
        self.assertEqual(out.count(".insertion"), 1)


if __name__ == "__main__":
    unittest.main()
