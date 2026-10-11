#!/usr/bin/env python3
"""Find a journal's CSL style in the Zotero Style Repository and save it.

Two subcommands:

  search  List styles whose title or id matches a journal name.
  get     Download one style (and, for a dependent style, its parent) into a
          manuscript folder and record where the files came from.

This tool handles the citation FORMAT only. It never reads or writes refs.bib
and never edits CSL XML: files are saved byte-for-byte as received.

A dependent style is a tiny CSL file that has no <citation> element and only
points to a parent ("independent-parent" link). pandoc given such a file
downloads the parent from the network at render time, so `get` saves the
parent too and reports the parent as the file to pass to pandoc.

Network use is limited to GET requests to
https://www.zotero.org/styles-files/styles.json and
https://www.zotero.org/styles/<id>. Use --index-file / --source-dir to work
from local copies without any network access.

Usage:
    python fetch_csl.py search --query "Journal of Clinical Epidemiology"
    python fetch_csl.py search --query bmj --limit 5 --json
    python fetch_csl.py search --query bmj --index-file styles_index.json
    python fetch_csl.py get --id journal-of-clinical-epidemiology --dest projects/my_paper/styles
    python fetch_csl.py get --id elsevier-vancouver --dest styles --source-dir local_csl --force

Exit codes: 0 success (including zero search matches), 1 any other failure,
2 bad arguments, 3 style id not found.
"""

import argparse
import hashlib
import http.client
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

INDEX_URL = "https://www.zotero.org/styles-files/styles.json"
STYLE_URL_PREFIX = "https://www.zotero.org/styles/"
USER_AGENT = (
    "writing_with_ai-zotero_csl/0.1 "
    "(+https://github.com/SRWS-PSG/writing_with_ai)"
)
CSL_NS = "http://purl.org/net/xbiblio/csl"
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SOURCE_FILE = "csl_source.json"

TIMEOUT_SECONDS = 30
MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (2, 4)

EXIT_OK = 0
EXIT_FAILURE = 1
EXIT_BAD_ARGS = 2
EXIT_NOT_FOUND = 3


class CslError(Exception):
    """A failure that maps to a process exit code."""

    def __init__(self, message, code=EXIT_FAILURE):
        super().__init__(message)
        self.code = code


class StyleNotFound(CslError):
    """The requested style id does not exist (HTTP 404 or missing local file)."""

    def __init__(self, message):
        super().__init__(message, EXIT_NOT_FOUND)


def http_get(url, timeout=TIMEOUT_SECONDS):
    """GET url and return (status, body bytes).

    HTTP error statuses are returned, not raised. Connection problems and
    timeouts raise OSError (urllib.error.URLError is a subclass); a body cut
    off mid-read raises http.client.HTTPException. Tests replace this
    function, so no test needs the network.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, b""


def sleep(seconds):
    """Backoff sleep. Tests replace this function so nothing really waits."""
    time.sleep(seconds)


def check_style_id(style_id):
    """Return style_id if it is a safe style id, else raise CslError (exit 2)."""
    if not isinstance(style_id, str) or not ID_PATTERN.match(style_id):
        raise CslError(
            "invalid style id %r (allowed: lowercase letters, digits, hyphen; "
            "must start with a letter or digit)" % (style_id,),
            EXIT_BAD_ARGS,
        )
    return style_id


def style_url(style_id):
    """Return the Zotero Style Repository URL of a validated style id."""
    return STYLE_URL_PREFIX + check_style_id(style_id)


def fetch_validated(url, parse):
    """GET url with retries and return parse(body).

    Retries (up to MAX_ATTEMPTS, backoff 2 s then 4 s) on connection errors,
    timeouts, HTTP 5xx, HTTP 429, and a 200 body that parse() rejects with
    ValueError. HTTP 404 raises StyleNotFound without retry. Other statuses
    fail without retry.
    """
    if url != INDEX_URL and not url.startswith(STYLE_URL_PREFIX):
        raise CslError("refusing to fetch unexpected URL: %s" % url)
    last_problem = "unknown failure"
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            status, body = http_get(url)
        except (OSError, http.client.HTTPException) as error:
            last_problem = "network error: %s" % (error or type(error).__name__)
        else:
            if status == 404:
                raise StyleNotFound("not found (HTTP 404): %s" % url)
            if status == 200:
                try:
                    return parse(body)
                except ValueError as error:
                    last_problem = "unusable response body: %s" % error
            elif status == 429 or status >= 500:
                last_problem = "HTTP %d" % status
            else:
                raise CslError("HTTP %d for %s" % (status, url))
        if attempt < MAX_ATTEMPTS:
            sleep(BACKOFF_SECONDS[attempt - 1])
    raise CslError(
        "giving up on %s after %d attempts (%s)" % (url, MAX_ATTEMPTS, last_problem)
    )


def parse_index(body):
    """Parse the style index body into a list of dicts, or raise ValueError."""
    try:
        data = json.loads(body.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("index is not valid JSON: %s" % error)
    if not isinstance(data, list):
        raise ValueError("index is not a JSON list")
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError("index entry is not an object")
        if not isinstance(entry.get("name"), str):
            raise ValueError("index entry without a string 'name'")
        if not isinstance(entry.get("title"), str):
            raise ValueError("index entry without a string 'title'")
    return data


def load_index(index_file=None):
    """Return the style index, from a local file or from the repository."""
    if index_file:
        try:
            body = Path(index_file).read_bytes()
        except OSError as error:
            raise CslError("cannot read index file: %s" % error)
        try:
            return parse_index(body)
        except ValueError as error:
            raise CslError("bad index file %s: %s" % (index_file, error))
    return fetch_validated(INDEX_URL, parse_index)


def normalise(text):
    """Lowercase and collapse whitespace."""
    return " ".join(text.lower().split())


def match_rank(entry, query):
    """Return 0 (exact), 1 (prefix), 2 (substring), or None (no match)."""
    title = normalise(entry["title"])
    name = normalise(entry["name"].replace("-", " "))
    query_name = normalise(query.replace("-", " "))
    pairs = [(title, query), (name, query_name)]
    ranks = []
    for text, needle in pairs:
        if not needle:
            continue
        if text == needle:
            ranks.append(0)
        elif text.startswith(needle):
            ranks.append(1)
        elif needle in text:
            ranks.append(2)
    if not ranks:
        return None
    return min(ranks)


def search_index(index, query):
    """Return index entries matching query, best match first."""
    normalised = normalise(query)
    ranked = []
    for entry in index:
        rank = match_rank(entry, normalised)
        if rank is not None:
            ranked.append((rank, entry["title"].lower(), entry["name"], entry))
    ranked.sort(key=lambda item: item[:3])
    return [item[3] for item in ranked]


def describe(entry):
    """Return the output fields of one index entry."""
    return {
        "id": entry["name"],
        "title": entry["title"],
        "dependent": bool(entry.get("dependent")),
        "updated": entry.get("updated", ""),
    }


def cmd_search(args):
    """Run the search subcommand."""
    query = normalise(args.query)
    if not query:
        raise CslError("--query is empty", EXIT_BAD_ARGS)
    if args.limit < 1:
        raise CslError("--limit must be at least 1", EXIT_BAD_ARGS)
    index = load_index(args.index_file)
    matches = search_index(index, query)
    shown = [describe(entry) for entry in matches[: args.limit]]
    if args.json:
        print(json.dumps(shown, ensure_ascii=False, indent=2))
        return EXIT_OK
    if not matches:
        print('no match for "%s" in %d styles' % (args.query, len(index)))
        return EXIT_OK
    for item in shown:
        kind = "dependent" if item["dependent"] else "independent"
        print("%s\t%s\t%s\tupdated %s" % (item["id"], item["title"], kind, item["updated"]))
    print("matches: %d" % len(matches))
    if len(matches) > len(shown):
        print(
            "showing the first %d of %d (raise --limit to see more)"
            % (len(shown), len(matches))
        )
    return EXIT_OK


def parse_style(body):
    """Parse CSL bytes and return the root element, or raise ValueError."""
    try:
        root = ET.fromstring(body)
    except ET.ParseError as error:
        raise ValueError("not well-formed XML: %s" % error)
    if root.tag != "{%s}style" % CSL_NS:
        raise ValueError("root element is %s, not a CSL <style>" % root.tag)
    return root


def parent_link(root):
    """Return the independent-parent href of a style, or None."""
    for link in root.findall("{%s}info/{%s}link" % (CSL_NS, CSL_NS)):
        if link.get("rel") == "independent-parent":
            return link.get("href")
    return None


def has_citation(root):
    """Return True if the style defines a <citation> element."""
    return root.find("{%s}citation" % CSL_NS) is not None


def style_title(root, style_id):
    """Return the style's own <info><title>, or style_id when absent."""
    node = root.find("{%s}info/{%s}title" % (CSL_NS, CSL_NS))
    if node is not None and node.text and node.text.strip():
        return node.text.strip()
    return style_id


def obtain_style(style_id, source_dir):
    """Return (body bytes, root element, source label) for one style id."""
    check_style_id(style_id)
    if source_dir:
        path = Path(source_dir) / (style_id + ".csl")
        try:
            body = path.read_bytes()
        except FileNotFoundError:
            raise StyleNotFound("no such style file: %s" % path.as_posix())
        except OSError as error:
            raise CslError("cannot read %s: %s" % (path.as_posix(), error))
        try:
            root = parse_style(body)
        except ValueError as error:
            raise CslError("%s: %s" % (path.as_posix(), error))
        return body, root, path.as_posix()
    url = style_url(style_id)

    def parse(body):
        return body, parse_style(body)

    body, root = fetch_validated(url, parse)
    return body, root, url


def parent_id_from_href(href):
    """Return the validated parent style id from an independent-parent href."""
    last = (href or "").rstrip("/").rsplit("/", 1)[-1]
    try:
        return check_style_id(last)
    except CslError:
        raise CslError("independent-parent link has no usable style id: %r" % href)


def sha256_hex(data):
    """Return the hex SHA-256 digest of bytes."""
    return hashlib.sha256(data).hexdigest()


def write_atomic(path, data):
    """Write bytes to path via a temp file in the same directory."""
    handle, temp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".part")
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
        os.replace(temp_name, str(path))
    except BaseException:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def plan_writes(dest, files, force):
    """Decide per file: 'new', 'unchanged', or 'overwrite'. Refuse conflicts."""
    plan = []
    for name, data in files:
        path = dest / name
        if not path.exists():
            plan.append((name, data, "new"))
            continue
        if path.read_bytes() == data:
            plan.append((name, data, "unchanged"))
            continue
        if not force:
            raise CslError(
                "%s already exists with different content; use --force to overwrite"
                % path.as_posix()
            )
        plan.append((name, data, "overwrite"))
    return plan


def load_source_record(path):
    """Return the existing csl_source.json object (or {})."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise CslError("cannot read %s: %s" % (path.as_posix(), error))
    if not isinstance(data, dict):
        raise CslError("%s is not a JSON object" % path.as_posix())
    return data


def cmd_get(args):
    """Run the get subcommand."""
    style_id = check_style_id(args.id)
    body, root, source = obtain_style(style_id, args.source_dir)
    title = style_title(root, style_id)
    files = [(style_id + ".csl", body)]
    source_urls = [source]
    parent_id = None
    href = parent_link(root)
    if href and not has_citation(root):
        parent_id = parent_id_from_href(href)
        parent_body, parent_root, parent_source = obtain_style(parent_id, args.source_dir)
        if parent_link(parent_root) and not has_citation(parent_root):
            raise CslError(
                "parent style %s is itself dependent; chains are not followed" % parent_id
            )
        if not has_citation(parent_root):
            raise CslError("parent style %s has no <citation> element" % parent_id)
        files.append((parent_id + ".csl", parent_body))
        source_urls.append(parent_source)
    elif not has_citation(root):
        raise CslError("style %s has neither <citation> nor an independent-parent link" % style_id)
    use_csl = files[-1][0]
    dest = Path(args.dest)
    plan = plan_writes(dest, files, args.force)
    record_path = dest / SOURCE_FILE
    records = load_source_record(record_path)
    entry = {
        "title": title,
        "requested_id": style_id,
        "dependent": parent_id is not None,
        "parent_id": parent_id,
        "use_csl": use_csl,
        "source_urls": source_urls,
        "sha256": {name: sha256_hex(data) for name, data in files},
    }
    old = records.get(style_id)
    old_core = None
    if isinstance(old, dict):
        old_core = {key: value for key, value in old.items() if key != "fetched_at"}
    dest.mkdir(parents=True, exist_ok=True)
    for name, data, state in plan:
        path = dest / name
        if state != "unchanged":
            write_atomic(path, data)
    record_state = "unchanged"
    if old_core != entry:
        record_state = "saved"
        entry["fetched_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        records[style_id] = entry
        text = json.dumps(records, ensure_ascii=False, indent=2) + "\n"
        write_atomic(record_path, text.encode("utf-8"))
    print("style: %s (%s)" % (style_id, title))
    if parent_id:
        print("dependent: yes -> parent %s" % parent_id)
    else:
        print("dependent: no")
    for name, data, state in plan:
        label = "unchanged" if state == "unchanged" else "saved"
        print("%s: %s" % (label, (dest / name).as_posix()))
    print("%s: %s" % (record_state, record_path.as_posix()))
    print("use with pandoc: --csl %s" % (dest / use_csl).as_posix())
    return EXIT_OK


def build_parser():
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)
    search = sub.add_parser("search", help="find styles by journal name or style id")
    search.add_argument("--query", required=True, help="journal name or style id")
    search.add_argument("--limit", type=int, default=10, help="max candidates to print")
    search.add_argument("--json", action="store_true", help="emit JSON")
    search.add_argument("--index-file", default=None, help="read this local styles.json")
    get = sub.add_parser("get", help="save a style (and its parent) into a folder")
    get.add_argument("--id", required=True, help="style id, e.g. elsevier-vancouver")
    get.add_argument("--dest", required=True, help="folder to save into")
    get.add_argument("--source-dir", default=None, help="read <id>.csl from here instead of the network")
    get.add_argument("--force", action="store_true", help="overwrite files that differ")
    return parser


def main(argv=None):
    """Entry point; returns the process exit code."""
    args = build_parser().parse_args(argv)
    try:
        if args.command == "search":
            return cmd_search(args)
        return cmd_get(args)
    except CslError as error:
        print("error: %s" % error, file=sys.stderr)
        return error.code
    except OSError as error:
        print("error: %s" % error, file=sys.stderr)
        return EXIT_FAILURE


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    sys.exit(main())
