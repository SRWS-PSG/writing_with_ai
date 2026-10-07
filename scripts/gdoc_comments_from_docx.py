#!/usr/bin/env python3
"""Google ドキュメントを docx で書き出したファイルから、コメントと返信スレッドを JSON にする。

出力は Drive API comments.list と同じ形なので、そのまま md_to_gdoc_review.py の -c に渡せる。
各コメントに "reply" を書き足すと、それが新しい返信になる。

使い方:
    python3 scripts/gdoc_comments_from_docx.py exported.docx -o comments.json
"""

import argparse
import json
import sys
import zipfile

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
W15 = "http://schemas.microsoft.com/office/word/2012/wordml"


def text_of(el):
    return "".join(t.text or "" for t in el.iter(f"{{{W}}}t"))


def anchors(document):
    """commentRangeStart〜End の間の本文（コメントされた文字列）を、v1 の本文に合わせて集める。"""
    root = etree.fromstring(document)
    quoted, open_ids = {}, set()
    tags = ("commentRangeStart", "commentRangeEnd", "t", "delText", "p")
    for el in root.iter(*(f"{{{W}}}{t}" for t in tags)):
        tag = etree.QName(el).localname
        if tag == "t" and any(etree.QName(a).localname == "ins" for a in el.iterancestors()):
            continue  # 未処理の提案で挿入された文字は v1 の本文にないので除く
        if tag == "delText":
            tag = "t"  # 提案で削除された文字は v1 の本文にある
        cid = el.get(f"{{{W}}}id")
        if tag == "commentRangeStart":
            open_ids.add(cid)
            quoted.setdefault(cid, "")
        elif tag == "commentRangeEnd":
            open_ids.discard(cid)
        elif tag == "t":
            for i in open_ids:
                quoted[i] += el.text or ""
        elif tag == "p":
            # 段落の始まり＝前の段落の終わり。範囲が段落をまたぐときは改行を入れる
            for i in open_ids:
                if quoted[i]:
                    quoted[i] += "\n"
    return {k: v.strip() for k, v in quoted.items()}


def extract(path):
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        if "word/comments.xml" not in names:
            return []
        comments = etree.fromstring(z.read("word/comments.xml"))
        document = z.read("word/document.xml")
        ext = etree.fromstring(z.read("word/commentsExtended.xml")) if "word/commentsExtended.xml" in names else None

    parent_of, done_of = {}, {}
    if ext is not None:
        for e in ext.iter(f"{{{W15}}}commentEx"):
            pid = e.get(f"{{{W15}}}paraId")
            parent_of[pid] = e.get(f"{{{W15}}}paraIdParent")
            done_of[pid] = e.get(f"{{{W15}}}done") == "1"

    quoted = anchors(document)
    threads, by_para = [], {}
    for cm in comments.iter(f"{{{W}}}comment"):
        cid = cm.get(f"{{{W}}}id")
        paras = cm.findall(f"{{{W}}}p")
        pid = paras[-1].get(f"{{{W14}}}paraId") if paras else None
        item = {
            "id": cid,
            "content": "\n".join(text_of(p) for p in paras).strip(),
            "author": {"displayName": cm.get(f"{{{W}}}author", "")},
            "createdTime": cm.get(f"{{{W}}}date", ""),
        }
        parent = parent_of.get(pid)
        if parent and parent in by_para:
            by_para[parent].setdefault("replies", []).append(item)
            continue
        item["quotedFileContent"] = {"value": quoted.get(cid, "")}
        item["resolved"] = done_of.get(pid, False)
        item["replies"] = []
        item["reply"] = ""
        threads.append(item)
        if pid:
            by_para[pid] = item
    return threads


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("docx", help="Google ドキュメントを docx で書き出したファイル")
    p.add_argument("-o", "--output", help="出力先（省略時は標準出力）")
    args = p.parse_args()

    data = json.dumps({"comments": extract(args.docx)}, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(data + "\n")
    else:
        sys.stdout.write(data + "\n")


if __name__ == "__main__":
    main()
