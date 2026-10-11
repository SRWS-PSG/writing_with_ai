"""Offline tests for fetch_csl.py (search / get). No test touches the network."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
ROOT = TESTS.parents[2]
sys.path.insert(0, str(TESTS.parent / "scripts"))

import fetch_csl  # noqa: E402

FIXTURES = TESTS / "fixtures"
INDEX = FIXTURES / "styles_index_sample.json"
JCE = "journal-of-clinical-epidemiology"
EV = "elsevier-vancouver"


def run(capsys, argv):
    code = fetch_csl.main(argv)
    out = capsys.readouterr()
    return code, out.out, out.err


def search(capsys, query, *extra):
    return run(capsys, ["search", "--query", query, "--index-file", str(INDEX), *extra])


def search_ids(capsys, query):
    code, out, _ = search(capsys, query, "--json")
    assert code == 0
    return [item["id"] for item in json.loads(out)]


def get(capsys, dest, style_id=JCE, *extra):
    return run(
        capsys,
        ["get", "--id", style_id, "--dest", str(dest), "--source-dir", str(FIXTURES), *extra],
    )


@pytest.fixture(autouse=True)
def no_real_network(monkeypatch):
    def refuse(url, timeout=30):
        raise AssertionError("unexpected network call: " + url)

    monkeypatch.setattr(fetch_csl, "http_get", refuse)
    monkeypatch.setattr(fetch_csl, "sleep", lambda seconds: None)


# ---------------------------------------------------------------- search


def test_search_jce_single_dependent_hit(capsys):
    code, out, _ = search(capsys, "journal of clinical epidemiology")
    assert code == 0
    assert out.count(JCE) == 1
    assert "\tdependent\t" in out
    assert "matches: 1" in out


def test_search_ranks_exact_before_substring(capsys):
    ids = search_ids(capsys, "respirology")
    assert ids.index("respirology") < ids.index("world-journal-of-respirology")


def test_search_matches_style_id_not_only_title(capsys):
    assert "american-medical-association" in search_ids(capsys, "american medical association")


def test_search_bmj_first(capsys):
    ids = search_ids(capsys, "bmj")
    assert ids[0] == "bmj"
    assert "bmj-open" in ids


def test_search_hyphenated_id_query(capsys):
    assert search_ids(capsys, "bmj-open")[0] == "bmj-open"


def test_search_zero_matches_is_success(capsys):
    code, out, err = search(capsys, "zzzz nonsense journal")
    assert code == 0
    assert out.strip() == 'no match for "zzzz nonsense journal" in 9 styles'
    assert err == ""


def test_search_limit_says_truncated(capsys):
    code, out, _ = search(capsys, "a", "--limit", "2")
    assert code == 0
    assert "showing the first 2 of" in out


def test_search_corrupt_index_fails(capsys, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    code, out, err = run(capsys, ["search", "--query", "bmj", "--index-file", str(bad)])
    assert code != 0
    assert err.startswith("error:")
    assert out == ""


def test_search_index_must_be_a_list(capsys, tmp_path):
    bad = tmp_path / "obj.json"
    bad.write_text('{"a": 1}', encoding="utf-8")
    code, _, err = run(capsys, ["search", "--query", "bmj", "--index-file", str(bad)])
    assert code != 0
    assert "error:" in err


# ------------------------------------------------------------------- get


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_get_dependent_saves_both_files(capsys, tmp_path):
    dest = tmp_path / "styles"
    code, out, _ = get(capsys, dest)
    assert code == 0
    for name in (JCE + ".csl", EV + ".csl"):
        assert (dest / name).read_bytes() == (FIXTURES / name).read_bytes()
    record = json.loads((dest / "csl_source.json").read_text(encoding="utf-8"))
    entry = record[JCE]
    assert entry["dependent"] is True
    assert entry["parent_id"] == EV
    assert entry["use_csl"] == EV + ".csl"
    assert entry["requested_id"] == JCE
    assert entry["title"] == "Journal of Clinical Epidemiology"
    assert entry["sha256"] == {JCE + ".csl": sha(dest / (JCE + ".csl")), EV + ".csl": sha(dest / (EV + ".csl"))}
    assert entry["fetched_at"].endswith("Z")
    lines = out.strip().splitlines()
    assert lines[0] == "style: %s (Journal of Clinical Epidemiology)" % JCE
    assert "dependent: yes -> parent " + EV in lines
    assert lines[-1].startswith("use with pandoc: --csl ")
    assert lines[-1].endswith("/" + EV + ".csl")
    raw = (dest / "csl_source.json").read_bytes()
    assert raw.endswith(b"\n") and b"\r" not in raw


def test_get_independent_style(capsys, tmp_path):
    dest = tmp_path / "styles"
    code, out, _ = get(capsys, dest, EV)
    assert code == 0
    assert sorted(p.name for p in dest.iterdir()) == ["csl_source.json", EV + ".csl"]
    entry = json.loads((dest / "csl_source.json").read_text(encoding="utf-8"))[EV]
    assert entry["dependent"] is False
    assert entry["parent_id"] is None
    assert entry["use_csl"] == EV + ".csl"
    assert "dependent: no" in out.splitlines()
    assert out.strip().splitlines()[-1].endswith("/" + EV + ".csl")


def test_second_get_preserves_first(capsys, tmp_path):
    dest = tmp_path / "styles"
    get(capsys, dest, JCE)
    first = json.loads((dest / "csl_source.json").read_text(encoding="utf-8"))[JCE]
    code, _, _ = get(capsys, dest, EV)
    assert code == 0
    record = json.loads((dest / "csl_source.json").read_text(encoding="utf-8"))
    assert set(record) == {JCE, EV}
    assert record[JCE] == first


def test_rerun_reports_unchanged(capsys, tmp_path):
    dest = tmp_path / "styles"
    get(capsys, dest)
    before = (dest / "csl_source.json").read_bytes()
    code, out, _ = get(capsys, dest)
    assert code == 0
    assert out.count("unchanged: ") == 3
    assert "saved: " not in out
    assert (dest / "csl_source.json").read_bytes() == before


def test_different_existing_file_needs_force(capsys, tmp_path):
    dest = tmp_path / "styles"
    dest.mkdir()
    target = dest / (EV + ".csl")
    target.write_bytes(b"local edit")
    code, _, err = get(capsys, dest, EV)
    assert code != 0
    assert EV + ".csl" in err
    assert target.read_bytes() == b"local edit"
    assert not (dest / "csl_source.json").exists()
    code, _, _ = get(capsys, dest, EV, "--force")
    assert code == 0
    assert target.read_bytes() == (FIXTURES / (EV + ".csl")).read_bytes()


@pytest.mark.parametrize("bad", ["../x", "A B", "", "-lead", "a/b", "UPPER"])
def test_id_validation_rejects(capsys, tmp_path, bad):
    code, _, err = run(capsys, ["get", "--id=" + bad, "--dest", str(tmp_path / "d"), "--source-dir", str(FIXTURES)])
    assert code == 2
    assert "invalid style id" in err
    assert not (tmp_path / "d").exists()


def test_missing_source_file_is_not_found(capsys, tmp_path):
    code, _, err = get(capsys, tmp_path / "d", "no-such-style")
    assert code == 3
    assert "error:" in err


# ------------------------------------------------- injected fake network


def make_fake(responses, calls):
    def fake(url, timeout=30):
        calls.append(url)
        queue = responses[url]
        item = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(item, Exception):
            raise item
        return item

    return fake


def url_of(style_id):
    return "https://www.zotero.org/styles/" + style_id


def csl_bytes(name):
    return (FIXTURES / (name + ".csl")).read_bytes()


def fake_get(monkeypatch, capsys, tmp_path, responses):
    calls = []
    sleeps = []
    monkeypatch.setattr(fetch_csl, "http_get", make_fake(responses, calls))
    monkeypatch.setattr(fetch_csl, "sleep", sleeps.append)
    dest = tmp_path / "styles"
    result = run(capsys, ["get", "--id", JCE, "--dest", str(dest)])
    return result, calls, sleeps, dest


def test_404_exits_3_without_retry(monkeypatch, capsys, tmp_path):
    (code, _, err), calls, sleeps, dest = fake_get(
        monkeypatch, capsys, tmp_path, {url_of(JCE): [(404, b"")]}
    )
    assert code == 3
    assert "404" in err
    assert len(calls) == 1
    assert sleeps == []
    assert not dest.exists()


def test_503_twice_then_success(monkeypatch, capsys, tmp_path):
    responses = {
        url_of(JCE): [(503, b""), (503, b""), (200, csl_bytes(JCE))],
        url_of(EV): [(200, csl_bytes(EV))],
    }
    (code, out, _), calls, sleeps, dest = fake_get(monkeypatch, capsys, tmp_path, responses)
    assert code == 0
    assert calls == [url_of(JCE)] * 3 + [url_of(EV)]
    assert sleeps == [2, 4]
    assert (dest / (EV + ".csl")).read_bytes() == csl_bytes(EV)
    record = json.loads((dest / "csl_source.json").read_text(encoding="utf-8"))
    assert record[JCE]["source_urls"] == [url_of(JCE), url_of(EV)]


def test_network_error_retried_then_fails(monkeypatch, capsys, tmp_path):
    responses = {url_of(JCE): [OSError("timed out")]}
    (code, _, err), calls, sleeps, dest = fake_get(monkeypatch, capsys, tmp_path, responses)
    assert code == 1
    assert len(calls) == 3
    assert "timed out" in err
    assert not dest.exists()


def test_truncated_body_retried_then_succeeds(monkeypatch, capsys, tmp_path):
    import http.client

    responses = {
        url_of(JCE): [http.client.IncompleteRead(b"<style"), (200, csl_bytes(JCE))],
        url_of(EV): [(200, csl_bytes(EV))],
    }
    (code, out, _), calls, sleeps, dest = fake_get(monkeypatch, capsys, tmp_path, responses)
    assert code == 0
    assert calls == [url_of(JCE)] * 2 + [url_of(EV)]
    assert sleeps == [2]
    assert (dest / (JCE + ".csl")).read_bytes() == csl_bytes(JCE)


def test_dest_that_is_a_file_fails_cleanly(capsys, tmp_path):
    dest = tmp_path / "styles"
    dest.write_text("not a directory", encoding="utf-8")
    code, _, err = run(
        capsys, ["get", "--id", JCE, "--dest", str(dest), "--source-dir", str(FIXTURES)]
    )
    assert code == 1
    assert "error:" in err
    assert dest.read_text(encoding="utf-8") == "not a directory"


def test_html_body_retried_then_fails_and_leaves_no_file(monkeypatch, capsys, tmp_path):
    html = b"<!DOCTYPE html><html><body>Please wait</body></html>"
    (code, _, err), calls, _, dest = fake_get(
        monkeypatch, capsys, tmp_path, {url_of(JCE): [(200, html)]}
    )
    assert code == 1
    assert len(calls) == 3
    assert "error:" in err
    assert not dest.exists() or list(dest.iterdir()) == []


def test_other_4xx_not_retried(monkeypatch, capsys, tmp_path):
    (code, _, _), calls, _, _ = fake_get(monkeypatch, capsys, tmp_path, {url_of(JCE): [(403, b"")]})
    assert code == 1
    assert len(calls) == 1


def test_parent_that_is_dependent_is_an_error(monkeypatch, capsys, tmp_path):
    responses = {
        url_of(JCE): [(200, csl_bytes(JCE))],
        url_of(EV): [(200, csl_bytes(JCE))],
    }
    (code, _, err), _, _, dest = fake_get(monkeypatch, capsys, tmp_path, responses)
    assert code == 1
    assert "dependent" in err
    assert not dest.exists()


def test_http_href_is_not_followed(monkeypatch, capsys, tmp_path):
    responses = {
        url_of(JCE): [(200, csl_bytes(JCE))],
        url_of(EV): [(200, csl_bytes(EV))],
    }
    (code, _, _), calls, _, _ = fake_get(monkeypatch, capsys, tmp_path, responses)
    assert code == 0
    assert all(call.startswith("https://www.zotero.org/styles/") for call in calls)


def test_search_over_network_uses_index_url(monkeypatch, capsys):
    calls = []
    body = INDEX.read_bytes()
    monkeypatch.setattr(fetch_csl, "http_get", make_fake({fetch_csl.INDEX_URL: [(200, body)]}, calls))
    code, out, _ = run(capsys, ["search", "--query", "respirology"])
    assert code == 0
    assert calls == [fetch_csl.INDEX_URL]
    assert "respirology" in out


# ------------------------------------------------------------ pandoc render


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc not installed")
def test_pandoc_renders_differently_with_vancouver(tmp_path):
    def render(csl):
        result = subprocess.run(
            [
                shutil.which("pandoc"),
                str(TESTS / "fixture_draft.md"),
                "--citeproc",
                "--bibliography",
                str(TESTS / "fixture_refs.bib"),
                "--csl",
                str(csl),
                "-t",
                "plain",
            ],
            capture_output=True,
            encoding="utf-8",
            cwd=str(tmp_path),
        )
        assert result.returncode == 0, result.stderr
        return result.stdout

    ama = render(ROOT / "demo" / "styles" / "american-medical-association.csl")
    vancouver = render(FIXTURES / (EV + ".csl"))
    assert ama != vancouver
    assert "[1]" in vancouver
    assert "[1,2]" in vancouver or "[1]" in vancouver
    reference_part = vancouver.split("References", 1)[-1]
    assert "[1]" in reference_part
