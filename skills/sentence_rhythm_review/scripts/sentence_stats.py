#!/usr/bin/env python3
"""Sentence-length distribution and rhythm diagnostics for Markdown prose.

Measures the per-sentence word count of every body paragraph in a Markdown
file, so an author can see (a) which sentences are split candidates and
(b) whether any paragraph's rhythm is an outlier (uniformly choppy / uniformly
long) versus its siblings.

This tool MEASURES only. It does not rewrite prose and it does not own the
sentence-length RULE: the "<= 25 words, hard cap 25" rule lives in
writing_with_AI/skills/case_report_workflow/style_discipline.md (R2). The
`--cap` flag defaults to that value only to flag candidates, not to enforce it.

Usage:
    python sentence_stats.py MANUSCRIPT.md
    python sentence_stats.py MANUSCRIPT.md --cap 25 --min-words 40
    python sentence_stats.py MANUSCRIPT.md --lines 18,20,22   # explicit blocks
    python sentence_stats.py MANUSCRIPT.md --json             # machine output
    python sentence_stats.py MANUSCRIPT.md --top 5            # longest-N table
"""

import argparse
import json
import re
import statistics
import sys

# Abbreviations whose trailing "." must NOT end a sentence.
_ABBREV = [
    "et al", "e.g", "i.e", "vs", "cf", "etc", "Fig", "Figs", "Eq", "No",
    "Dr", "Mr", "Ms", "Mrs", "Prof", "St", "approx", "ca", "al",
]


def strip_markup(text):
    """Remove citation keys, inline markdown, and links for counting."""
    text = re.sub(r"\[@[^\]]*\]", "", text)            # pandoc citation keys
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)  # md links/images
    text = re.sub(r"[*_`~]+", "", text)                 # emphasis / code marks
    return text


def split_sentences(text):
    """Split into sentences, protecting abbreviations and decimals."""
    protected = text
    for ab in _ABBREV:
        protected = re.sub(
            r"\b" + re.escape(ab) + r"\.", ab + "<DOT>", protected
        )
    protected = re.sub(r"(\d)\.(\d)", r"\1<DEC>\2", protected)  # 0.4
    parts = re.split(r"(?<=[.!?])[\"')\]]?\s+", protected.strip())
    out = []
    for p in parts:
        p = p.replace("<DOT>", ".").replace("<DEC>", ".").strip()
        if p:
            out.append(p)
    return out


def word_count(sentence):
    cleaned = re.sub(r"[^\w\s'-]", " ", strip_markup(sentence))
    return len([w for w in cleaned.split() if w.strip()])


# Non-prose sections whose paragraphs should be skipped in auto mode.
_SKIP_HEADINGS = re.compile(
    r"^#+\s*(acknowledg|reference|bibliograph|funding|conflict|competing|"
    r"disclosure|declaration|data availab|appendix|supplement|author "
    r"contribution|ethic|consent)", re.IGNORECASE)


def iter_paragraphs(md_text, min_words, only_lines=None):
    """Yield (start_line, raw_text) for each prose paragraph.

    A paragraph is a blank-line-delimited block. In auto mode it must be
    prose: not a heading, not under a non-prose section (Acknowledgments,
    References, etc.), carrying at least `min_words` words. The n>=2 sentence
    filter (which drops punctuation-free title/affiliation blocks) is applied
    later in analyze(). only_lines bypasses every auto filter.
    """
    lines = md_text.split("\n")
    block_lines, block_start = [], None
    blocks = []
    for i, line in enumerate(lines, 1):
        if line.strip() == "":
            if block_lines:
                blocks.append((block_start, " ".join(block_lines)))
                block_lines, block_start = [], None
            continue
        if block_start is None:
            block_start = i
        block_lines.append(line.rstrip())
    if block_lines:
        blocks.append((block_start, " ".join(block_lines)))

    skipping = False
    for start, text in blocks:
        stripped = text.lstrip()
        is_heading = stripped.startswith("#")
        if only_lines is not None:
            if start in only_lines:
                yield start, text
            continue
        if is_heading:
            skipping = bool(_SKIP_HEADINGS.match(stripped))
            continue
        if skipping:                                      # non-prose section
            continue
        if stripped.startswith(("- ", "* ", "> ", "|")):  # list/quote/table
            continue
        if word_count(text) < min_words:                  # metadata / short line
            continue
        yield start, text


def analyze(md_text, cap, min_words, only_lines=None):
    paragraphs = []
    for start, text in iter_paragraphs(md_text, min_words, only_lines):
        sents = split_sentences(strip_markup(text))
        counts = [word_count(s) for s in sents]
        if not counts:
            continue
        # Auto mode: a real prose paragraph has >= 2 sentences. This drops
        # punctuation-free title/affiliation blocks that read as one long
        # "sentence". Explicit --lines selection keeps single-sentence blocks.
        if only_lines is None and len(counts) < 2:
            continue
        paragraphs.append({
            "index": len(paragraphs) + 1,
            "line": start,
            "n": len(counts),
            "mean": round(statistics.mean(counts), 1),
            "sd": round(statistics.pstdev(counts), 1),
            "min": min(counts),
            "max": max(counts),
            "over_cap": sum(1 for c in counts if c > cap),
            "counts": counts,
            "sentences": sents,
        })
    return paragraphs


def rhythm_flags(paragraphs):
    """Flag paragraphs whose mean is an outlier versus the sibling paragraphs."""
    if len(paragraphs) < 3:
        return {}
    means = [p["mean"] for p in paragraphs]
    grand = statistics.mean(means)
    spread = statistics.pstdev(means) or 1.0
    flags = {}
    for p in paragraphs:
        z = (p["mean"] - grand) / spread
        if z <= -1.0:
            flags[p["index"]] = f"uniformly short (mean {p['mean']} vs {grand:.1f} avg; possible choppiness)"
        elif z >= 1.0:
            flags[p["index"]] = f"uniformly long (mean {p['mean']} vs {grand:.1f} avg; possible heaviness)"
    return flags


def longest(paragraphs, top):
    ranked = []
    for p in paragraphs:
        for c, s in zip(p["counts"], p["sentences"]):
            ranked.append((c, p["index"], p["line"], s))
    ranked.sort(key=lambda t: t[0], reverse=True)
    return ranked[:top]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="Markdown manuscript")
    ap.add_argument("--cap", type=int, default=25,
                    help="word-count cap for flagging split candidates (default 25, per style_discipline R2)")
    ap.add_argument("--min-words", type=int, default=40,
                    help="min words for a block to count as a prose paragraph (default 40)")
    ap.add_argument("--lines", default=None,
                    help="comma-separated start line numbers to analyze explicitly (overrides auto-detect)")
    ap.add_argument("--top", type=int, default=5,
                    help="how many longest sentences to list (default 5)")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)

    # Prose snippets may contain non-ASCII (e.g. U+2011); force UTF-8 output so
    # a legacy Windows code page (cp932) cannot crash the run.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    with open(args.file, encoding="utf-8") as fh:
        md_text = fh.read()
    # Drop HTML comments (e.g. editorial notes) so they are never counted,
    # preserving line numbers by keeping the comment's newlines.
    md_text = re.sub(r"<!--.*?-->",
                     lambda m: "\n" * m.group(0).count("\n"),
                     md_text, flags=re.DOTALL)

    only = None
    if args.lines:
        only = {int(x) for x in args.lines.split(",") if x.strip()}

    paragraphs = analyze(md_text, args.cap, args.min_words, only)
    if not paragraphs:
        print("No prose paragraphs found. Try --min-words lower or --lines.",
              file=sys.stderr)
        return 1

    flags = rhythm_flags(paragraphs)
    tops = longest(paragraphs, args.top)
    allc = [c for p in paragraphs for c in p["counts"]]

    if args.json:
        for p in paragraphs:
            p.pop("sentences", None)
        print(json.dumps({
            "cap": args.cap,
            "paragraphs": paragraphs,
            "rhythm_flags": flags,
            "overall": {
                "n": len(allc),
                "mean": round(statistics.mean(allc), 1),
                "sd": round(statistics.pstdev(allc), 1),
            },
        }, ensure_ascii=False, indent=2))
        return 0

    print(f"# Sentence-length distribution  (cap={args.cap})\n")
    print(f"{'Para':<6}{'Line':<6}{'n':<4}{'mean':<6}{'sd':<6}{'min':<5}{'max':<5}{'>cap':<5} counts")
    for p in paragraphs:
        print(f"P{p['index']:<5}{p['line']:<6}{p['n']:<4}{p['mean']:<6}{p['sd']:<6}"
              f"{p['min']:<5}{p['max']:<5}{p['over_cap']:<5} {p['counts']}")
    print(f"\nOVERALL: n={len(allc)} sentences  "
          f"mean={statistics.mean(allc):.1f}  sd={statistics.pstdev(allc):.1f}")

    print(f"\n## Longest {len(tops)} sentences (split candidates)")
    for c, pi, ln, s in tops:
        mark = "  <-- over cap" if c > args.cap else ""
        snippet = (s[:90] + "...") if len(s) > 90 else s
        print(f"  {c:>3}w  P{pi} L{ln}{mark}\n        {snippet}")

    print("\n## Rhythm outliers (paragraph mean vs siblings)")
    if flags:
        for idx, msg in flags.items():
            print(f"  P{idx}: {msg}")
    else:
        print("  none - paragraph rhythms are balanced.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
