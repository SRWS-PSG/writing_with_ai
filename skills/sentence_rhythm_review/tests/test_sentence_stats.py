"""Tests for sentence_stats.py (word counting and the fixture regression)."""
from __future__ import annotations

import importlib.util
import io
import json
import re
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "sentence_stats.py"

_spec = importlib.util.spec_from_file_location("sentence_stats", SCRIPT)
ss = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ss)


class TestWordCount(unittest.TestCase):
    def test_decimal_is_one_word(self):
        self.assertEqual(ss.word_count("The mean was 1.5 mg."), 5)

    def test_several_numbers(self):
        # Values were | 12.5 | 3.25 | and | 1,200 | units
        self.assertEqual(ss.word_count("Values were 12.5, 3.25 and 1,200 units."), 7)

    def test_thousands_with_decimal(self):
        self.assertEqual(ss.word_count("Dose was 1,200.5 mg."), 4)

    def test_p_value_numeric_part_is_one_word(self):
        # Rates | differed | p | 0.05 : "p" stays a word, "0.05" is one word.
        self.assertEqual(ss.word_count("Rates differed (p<0.05)."), 4)
        self.assertEqual(ss.word_count("Rates differed (p = 0.05)."), 4)

    def test_integers_and_list_commas_unchanged(self):
        self.assertEqual(ss.word_count("Seen in 12 patients."), 4)
        # "1,2" is not a thousands group (needs exactly three digits after).
        self.assertEqual(ss.word_count("See items 1,2 here."), 5)

    def test_hyphenated_and_apostrophe_words_unchanged(self):
        self.assertEqual(ss.word_count("A well-known state-of-the-art method."), 4)
        self.assertEqual(ss.word_count("The patient's mother didn't agree."), 5)

    def test_citations_and_markup_still_stripped(self):
        self.assertEqual(
            ss.word_count("The **mean** was 1.5 mg [@smith2020; @doe2021]."), 5)


class TestFixtureRegression(unittest.TestCase):
    def test_fixture_matches_expected_report(self):
        expected = (HERE / "expected_report.md").read_text(encoding="utf-8")
        rows = re.findall(
            r"^\| (P\d)\s*\| (\d+)\s*\| (\d+)\s*\| ([\d.]+)\s*\| ([\d.]+)\s*"
            r"\| (\d+)\s*\| (\d+)\s*\| (\d+)\s*\|$", expected, re.M)
        self.assertEqual(len(rows), 3)

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = ss.main([str(HERE / "fixture.md"), "--json"])
        self.assertEqual(rc, 0)
        got = json.loads(buf.getvalue())

        self.assertEqual(len(got["paragraphs"]), len(rows))
        for p, (_, line, n, mean, sd, mn, mx, over) in zip(got["paragraphs"], rows):
            self.assertEqual(
                (p["line"], p["n"], p["mean"], p["sd"], p["min"], p["max"],
                 p["over_cap"]),
                (int(line), int(n), float(mean), float(sd), int(mn), int(mx),
                 int(over)))
        self.assertEqual(got["overall"], {"n": 15, "mean": 9.6, "sd": 9.3})
        self.assertEqual(sorted(got["rhythm_flags"]), ["2", "3"])
        self.assertIn("uniformly short", got["rhythm_flags"]["2"])
        self.assertIn("uniformly long", got["rhythm_flags"]["3"])


if __name__ == "__main__":
    unittest.main()
