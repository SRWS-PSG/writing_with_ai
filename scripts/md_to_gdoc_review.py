#!/usr/bin/env python3
"""v1/v2 の Markdown と Google Docs のコメントから「変更履歴＋コメント返信」入りの docx を作る。

できあがった docx を Google ドライブに「Google ドキュメントに変換」してアップロードすると、
変更履歴は「提案」、コメントは返信付きのスレッドとして取り込まれる。

使い方:
    python3 scripts/md_to_gdoc_review.py v1.md v2.md -c comments.json -o review.docx \
        --author "Yuki Kataoka" -- --citeproc

    v1.md          : 前回 Google Docs にした時点の Markdown（git show <commit>:paper.md > v1.md など）
    v2.md          : 修正後の Markdown
    comments.json  : Drive API comments.list の結果（各コメントに "reply" を書き足すと返信になる）
    -- 以降        : pandoc にそのまま渡す追加オプション（--citeproc, --reference-doc など）

詳しくは tutorials/gdoc_review_roundtrip.md を参照。
"""

import argparse
import copy
import difflib
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone

from lxml import etree

# ---------------------------------------------------------------------------
# pandoc AST helpers
# ---------------------------------------------------------------------------

QUOTE_CHARS = {"Single": ("‘", "’"), "Double": ("“", "”")}


def pandoc_json(path, extra_args):
    out = subprocess.run(
        ["pandoc", path, "-t", "json"] + extra_args,
        check=True, capture_output=True, text=True,
    )
    return json.loads(out.stdout)


def stringify(node):
    """inline 要素を Google Docs 上で見えるのに近いプレーンテキストにする。"""
    if isinstance(node, list):
        return "".join(stringify(n) for n in node)
    t, c = node.get("t"), node.get("c")
    if t == "Str":
        return c
    if t in ("Space", "SoftBreak", "LineBreak"):
        return " "
    if t in ("Code", "Math", "RawInline"):
        return c[1]
    if t == "Quoted":
        o, e = QUOTE_CHARS[c[0]["t"].replace("Quote", "")]
        return o + stringify(c[1]) + e
    if t in ("Emph", "Strong", "Underline", "Strikeout", "Superscript", "Subscript", "SmallCaps"):
        return stringify(c)
    if t in ("Span", "Link"):
        return stringify(c[1])
    if t == "Cite":
        return stringify(c[1])
    return ""  # Note, Image など


def key(node):
    return json.dumps(node, sort_keys=True, ensure_ascii=False)


# ---------------------------------------------------------------------------
# 差分: inline リストを「ストリーム」（(状態, inline) の列）に置き換える
#   状態: "eq" 変更なし / "ins" 挿入 / "del" 削除 / "mark" コメント位置マーカー
# ---------------------------------------------------------------------------

STREAM = "__stream__"


def to_stream(inlines, status):
    return {STREAM: [(status, i) for i in inlines]}


def split_str(inlines):
    """日本語は空白で区切られないので、Str を英数字の単語と 1 文字ずつに分けて差分を細かくする。"""
    out = []
    for i in inlines:
        if i.get("t") == "Str":
            out += [{"t": "Str", "c": p} for p in re.findall(r"[A-Za-z0-9]+|.", i["c"], re.S)]
        else:
            out.append(i)
    return out


def diff_inlines(old, new):
    old, new = split_str(old), split_str(new)
    sm = difflib.SequenceMatcher(None, [key(i) for i in old], [key(i) for i in new], autojunk=False)
    segs = [[op == "equal", old[i1:i2], new[j1:j2]] for op, i1, i2, j1, j2 in sm.get_opcodes()]
    # 変更に挟まれた 1〜2 トークンの一致（「効[果的]→[有]」のような細切れ）は変更に含めて読みやすくする
    for k in range(1, len(segs) - 1):
        if segs[k][0] and len(segs[k][1]) <= 2 and not segs[k - 1][0] and not segs[k + 1][0]:
            segs[k][0] = False
    merged = []
    for seg in segs:
        if merged and not seg[0] and not merged[-1][0]:
            merged[-1][1] += seg[1]
            merged[-1][2] += seg[2]
        else:
            merged.append(seg)
    out = []
    for equal, olds, news in merged:
        if equal:
            out += [("eq", i) for i in news]
        else:
            out += [("del", i) for i in olds] + [("ins", i) for i in news]
    return {STREAM: out}


def mark_blocks(node, status):
    """ブロック（またはその中身）の inline リストをすべて status のストリームにする。"""
    if isinstance(node, list):
        return [mark_blocks(n, status) for n in node]
    if not isinstance(node, dict):
        return node
    t = node.get("t")
    if t in ("Para", "Plain"):
        return {"t": t, "c": to_stream(node["c"], status)}
    if t == "Header":
        lvl, attr, inl = node["c"]
        return {"t": t, "c": [lvl, attr, to_stream(inl, status)]}
    if t == "LineBlock":
        return {"t": t, "c": [to_stream(l, status) for l in node["c"]]}
    if "c" in node:
        return {**node, "c": mark_blocks(node["c"], status)}
    return node


def diff_pair(old, new):
    """同じ位置にあると見なした 2 ブロックの差分。構造が違えば削除＋挿入にする。"""
    t = new.get("t")
    if old.get("t") != t:
        return [mark_blocks(old, "del"), mark_blocks(new, "ins")]
    if t in ("Para", "Plain"):
        # ほとんど書き直した段落は、単語単位で細切れにせず段落ごと置き換える
        if difflib.SequenceMatcher(None, stringify(old["c"]), stringify(new["c"]), autojunk=False).ratio() < 0.5:
            return [mark_blocks(old, "del"), mark_blocks(new, "ins")]
        return [{"t": t, "c": diff_inlines(old["c"], new["c"])}]
    if t == "Header" and old["c"][0] == new["c"][0]:
        return [{"t": t, "c": [new["c"][0], new["c"][1], diff_inlines(old["c"][2], new["c"][2])]}]
    if t in ("BlockQuote", "Div") or (t in ("BulletList", "OrderedList")):
        if t == "BlockQuote":
            return [{"t": t, "c": diff_blocks(old["c"], new["c"])}]
        if t == "Div":
            return [{"t": t, "c": [new["c"][0], diff_blocks(old["c"][1], new["c"][1])]}]
        if t == "BulletList":
            return [{"t": t, "c": diff_items(old["c"], new["c"])}]
        return [{"t": t, "c": [new["c"][0], diff_items(old["c"][1], new["c"][1])]}]
    return [mark_blocks(old, "del"), mark_blocks(new, "ins")]


def diff_items(old_items, new_items):
    """リスト項目（ブロック列の列）の差分。削除された項目は項目ごと削除表示にする。"""
    sm = difflib.SequenceMatcher(None, [key(i) for i in old_items], [key(i) for i in new_items], autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            out += [mark_blocks(i, "eq") for i in new_items[j1:j2]]
            continue
        olds, news = old_items[i1:i2], new_items[j1:j2]
        for k in range(max(len(olds), len(news))):
            if k < len(olds) and k < len(news):
                out.append(diff_blocks(olds[k], news[k]))
            elif k < len(olds):
                out.append(mark_blocks(olds[k], "del"))
            else:
                out.append(mark_blocks(news[k], "ins"))
    return out


def diff_blocks(old, new):
    sm = difflib.SequenceMatcher(None, [key(b) for b in old], [key(b) for b in new], autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            out += mark_blocks(new[j1:j2], "eq")
            continue
        olds, news = old[i1:i2], new[j1:j2]
        for k in range(max(len(olds), len(news))):
            if k < len(olds) and k < len(news):
                out += diff_pair(olds[k], news[k])
            elif k < len(olds):
                out.append(mark_blocks(olds[k], "del"))
            else:
                out.append(mark_blocks(news[k], "ins"))
    return out


def iter_streams(node):
    """文書順にストリームを列挙する。"""
    if isinstance(node, list):
        for n in node:
            yield from iter_streams(n)
    elif isinstance(node, dict):
        if STREAM in node:
            yield node
        else:
            for v in node.values():
                yield from iter_streams(v)


# ---------------------------------------------------------------------------
# コメントの位置合わせ
# ---------------------------------------------------------------------------

NORMALIZE = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"',
                           " ": " ", "\t": " ", "\n": " ", "\r": " "})


def norm(s):
    return s.translate(NORMALIZE)


def stream_text(stream, statuses):
    """statuses に含まれるトークンだけを連結した文字列と、各文字が属するトークン番号。"""
    text, owner = [], []
    for idx, (st, inl) in enumerate(stream[STREAM]):
        if st in statuses:
            s = norm(stringify(inl))
            text.append(s)
            owner += [idx] * len(s)
    return "".join(text), owner


def find_anchor(streams, quote):
    """コメントされた文字列を探す。v1 側（eq+del）→ v2 側（eq+ins）→ 先頭 40 文字の順で試す。"""
    def clean(s):
        return re.sub(r" +", " ", norm(s)).strip()

    whole, first_line = clean(quote), clean(quote.split("\n")[0])
    if not whole:
        return None
    candidates = [whole]
    if first_line != whole:
        candidates.append(first_line)  # 複数段落にまたがるコメントは最初の段落で探す
    if len(first_line) > 40:
        candidates.append(first_line[:40])
    for cand in candidates:
        for statuses in ({"eq", "del"}, {"eq", "ins"}):
            for s in streams:
                text, owner = stream_text(s, statuses)
                pos = text.find(cand)
                if pos >= 0:
                    return s, owner[pos], owner[pos + len(cand) - 1]
    return None


def comment_span(cid, author, date, text, start=True):
    if not start:
        return {"t": "Span", "c": [["", ["comment-end"], [["id", str(cid)]]], []]}
    inlines = []
    for n, line in enumerate(text.splitlines() or [""]):
        if n:
            inlines.append({"t": "LineBreak"})
        words = line.split(" ")
        for m, w in enumerate(words):
            if m:
                inlines.append({"t": "Space"})
            if w:
                inlines.append({"t": "Str", "c": w})
    attrs = [["id", str(cid)], ["author", author], ["date", date]]
    return {"t": "Span", "c": [["", ["comment-start"], attrs], inlines]}


def gdate(s):
    """Drive API の createdTime（ミリ秒付き）を Word 形式の日時にする。"""
    if not s:
        return NOW
    return re.sub(r"\.\d+Z$", "Z", s)


NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def place_comments(doc_blocks, comments, args):
    """各コメントスレッドを comment-start/end スパンとしてストリームに差し込む。返信の親子関係を返す。"""
    streams = [s for s in iter_streams(doc_blocks) if any(st != "mark" for st, _ in s[STREAM])]
    inserts = {}  # id(stream) -> {pos: [("end"|"start", span)]}
    parents = {}  # 返信の comment id -> 親の comment id
    next_id = 1000
    unanchored = []

    for c in comments:
        if c.get("deleted") or (c.get("resolved") and not args.include_resolved):
            continue
        quote = (c.get("quotedFileContent") or {}).get("value", "")
        hit = find_anchor(streams, quote)
        body = c.get("content", "")
        if hit is None:
            unanchored.append(quote)
            hit = (streams[0], 0, 0)
            if quote:
                body = f"[元の箇所が見つかりません:「{quote[:80]}」]\n{body}"
        stream, s_idx, e_idx = hit

        thread = [((c.get("author") or {}).get("displayName", "Reviewer"), gdate(c.get("createdTime")), body)]
        for r in c.get("replies", []):
            if r.get("deleted") or not r.get("content"):
                continue  # 「解決」などの操作だけの返信は本文がない
            thread.append(((r.get("author") or {}).get("displayName", "Reviewer"), gdate(r.get("createdTime")), r["content"]))
        if c.get("reply"):
            thread.append((args.author, NOW, c["reply"]))

        root_id = next_id
        slot = inserts.setdefault(id(stream), {})
        for n, (author, date, text) in enumerate(thread):
            cid = next_id
            next_id += 1
            if n:
                parents[cid] = root_id
            slot.setdefault(s_idx, []).append(("start", comment_span(cid, author, date, text)))
            slot.setdefault(e_idx + 1, []).insert(0, ("end", comment_span(cid, None, None, None, start=False)))

    for s in streams:
        slot = inserts.get(id(s))
        if not slot:
            continue
        toks = s[STREAM]
        for pos in sorted(slot, reverse=True):
            # 同じ位置では先に end、後に start（前のコメントを閉じてから次を開く）
            marks = [m for m in slot[pos] if m[0] == "end"] + [m for m in slot[pos] if m[0] == "start"]
            toks[pos:pos] = [("mark", span) for _, span in marks]

    return parents, unanchored


# ---------------------------------------------------------------------------
# ストリームを pandoc の insertion / deletion スパンに戻す
# ---------------------------------------------------------------------------

def render(node, author):
    if isinstance(node, list):
        return [render(n, author) for n in node]
    if not isinstance(node, dict):
        return node
    if STREAM in node:
        out, group, gst = [], [], None

        def flush():
            if not group:
                return
            if gst == "eq":
                out.extend(group)
            else:
                cls = "insertion" if gst == "ins" else "deletion"
                out.append({"t": "Span", "c": [["", [cls], [["author", author], ["date", NOW]]], list(group)]})
            group.clear()

        for st, inl in node[STREAM]:
            if st == "mark":
                flush()
                gst = None
                out.append(inl)
                continue
            if st != gst:
                flush()
                gst = st
            group.append(inl)
        flush()
        return out
    return {k: render(v, author) for k, v in node.items()}


# ---------------------------------------------------------------------------
# docx 後処理: 返信スレッド（commentsExtended.xml）と変更履歴 ID の振り直し
# ---------------------------------------------------------------------------

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
W15 = "http://schemas.microsoft.com/office/word/2012/wordml"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"
CT_EXT = "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml"
REL_EXT = "http://schemas.microsoft.com/office/2011/relationships/commentsExtended"


def postprocess(docx_path, parents):
    with zipfile.ZipFile(docx_path) as z:
        files = {n: z.read(n) for n in z.namelist()}

    # pandoc は w:ins と w:del に同じ ID を振ることがあるので、コメントと重ならない連番にする
    doc = files["word/document.xml"].decode("utf-8")
    counter = iter(range(100000, 10**7))
    doc = re.sub(r"(<w:(?:ins|del) w:id=\")\d+(\")", lambda m: f"{m.group(1)}{next(counter)}{m.group(2)}", doc)
    files["word/document.xml"] = doc.encode("utf-8")

    if "word/comments.xml" in files:
        root = etree.fromstring(files["word/comments.xml"])
        # w14:paraId を使うので名前空間を宣言し直す
        nsmap = dict(root.nsmap)
        nsmap.update({"w14": W14, "mc": MC})
        new_root = etree.Element(root.tag, nsmap=nsmap)
        new_root.set(f"{{{MC}}}Ignorable", "w14")
        for child in root:
            new_root.append(child)
        root = new_root

        para_of = {}
        used = set()
        for cm in root.findall(f"{{{W}}}comment"):
            ps = cm.findall(f"{{{W}}}p")
            if not ps:
                continue
            while True:
                pid = f"{random.randint(1, 0x7FFFFFFF):08X}"
                if pid not in used:
                    used.add(pid)
                    break
            ps[-1].set(f"{{{W14}}}paraId", pid)
            para_of[cm.get(f"{{{W}}}id")] = pid
        files["word/comments.xml"] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

        ext = etree.Element(f"{{{W15}}}commentsEx", nsmap={"w15": W15, "mc": MC})
        ext.set(f"{{{MC}}}Ignorable", "w15")
        for cid, pid in para_of.items():
            e = etree.SubElement(ext, f"{{{W15}}}commentEx")
            e.set(f"{{{W15}}}paraId", pid)
            parent = parents.get(int(cid)) if cid.isdigit() else None
            if parent is not None and str(parent) in para_of:
                e.set(f"{{{W15}}}paraIdParent", para_of[str(parent)])
            e.set(f"{{{W15}}}done", "0")
        files["word/commentsExtended.xml"] = etree.tostring(ext, xml_declaration=True, encoding="UTF-8", standalone=True)

        ct = files["[Content_Types].xml"].decode("utf-8")
        if "commentsExtended" not in ct:
            ct = ct.replace("</Types>", f'<Override PartName="/word/commentsExtended.xml" ContentType="{CT_EXT}" /></Types>')
            files["[Content_Types].xml"] = ct.encode("utf-8")
        rels = files["word/_rels/document.xml.rels"].decode("utf-8")
        if "commentsExtended" not in rels:
            rels = rels.replace("</Relationships>", f'<Relationship Type="{REL_EXT}" Id="rIdCommentsEx" Target="commentsExtended.xml" /></Relationships>')
            files["word/_rels/document.xml.rels"] = rels.encode("utf-8")

    with zipfile.ZipFile(docx_path, "w", zipfile.ZIP_DEFLATED) as z:
        for n, data in files.items():
            z.writestr(n, data)


# ---------------------------------------------------------------------------

def load_comments(path):
    if not path:
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("comments", []) if isinstance(data, dict) else data


def main():
    argv = sys.argv[1:]
    pandoc_args = []
    if "--" in argv:
        i = argv.index("--")
        argv, pandoc_args = argv[:i], argv[i + 1:]

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("v1", help="前回 Google Docs にした Markdown")
    p.add_argument("v2", help="修正後の Markdown")
    p.add_argument("-c", "--comments", help="Drive API comments.list の JSON（\"reply\" を書き足すと返信になる）")
    p.add_argument("-o", "--output", default="review.docx")
    p.add_argument("--author", default="Author", help="変更履歴と返信の作成者名")
    p.add_argument("--include-resolved", action="store_true", help="解決済みコメントも入れる")
    args = p.parse_args(argv)

    old = pandoc_json(args.v1, [])
    new = pandoc_json(args.v2, [])
    blocks = diff_blocks(old["blocks"], new["blocks"])
    parents, unanchored = place_comments(blocks, load_comments(args.comments), args)
    new["blocks"] = render(blocks, args.author)

    resource_path = os.pathsep.join([os.path.dirname(os.path.abspath(args.v2)), "."])
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(new, f, ensure_ascii=False)
        tmp = f.name
    try:
        subprocess.run(["pandoc", tmp, "-f", "json", "--resource-path", resource_path, "-o", args.output] + pandoc_args,
                       check=True)
    finally:
        os.unlink(tmp)
    postprocess(args.output, parents)

    print(f"✅ {args.output} を作成しました（返信 {len(parents)} 件）")
    for q in unanchored:
        print(f"⚠️  コメント位置が見つからず文書の先頭に付けました: {q[:60]!r}", file=sys.stderr)


if __name__ == "__main__":
    main()
