"""Extract w:ins / w:del tracked changes and comments from a DOCX."""
from __future__ import annotations
import json, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

def gather_text(parent):
    out = []
    for el in parent.iter():
        if el.tag in (f"{W}t", f"{W}delText") and el.text:
            out.append(el.text)
        elif el.tag == f"{W}tab":
            out.append("\t")
        elif el.tag == f"{W}br":
            out.append("\n")
    return "".join(out)

def main(docx_path: Path, report_dir: Path | None = None):
    report_dir = report_dir or docx_path.parent
    report_dir.mkdir(parents=True, exist_ok=True)

    # zip から document.xml / comments.xml を直接読む。中間フォルダに展開すると、
    # 前回実行時の comments.xml が残ったまま次の docx (コメント無し) を読んでしまう
    # ことがあるため、再利用可能な展開フォルダは作らない (A7)。
    with zipfile.ZipFile(docx_path) as z:
        names = set(z.namelist())
        doc = ET.fromstring(z.read("word/document.xml"))
        comments_xml = z.read("word/comments.xml") if "word/comments.xml" in names else None

    paragraphs = list(doc.iter(f"{W}p"))
    p_index = {id(p): i + 1 for i, p in enumerate(paragraphs)}

    changes = []
    for p in paragraphs:
        ctx = gather_text(p)
        for child in p.iter():
            if child.tag in (f"{W}ins", f"{W}del"):
                changes.append({
                    "kind": "insert" if child.tag == f"{W}ins" else "delete",
                    "author": child.attrib.get(f"{W}author", ""),
                    "date": child.attrib.get(f"{W}date", ""),
                    "text": gather_text(child),
                    "paragraph_index": p_index[id(p)],
                    "paragraph_context": ctx,
                })

    comments = []
    if comments_xml is not None:
        for c in ET.fromstring(comments_xml).findall(f"{W}comment"):
            comments.append({
                "id": c.attrib.get(f"{W}id", ""),
                "author": c.attrib.get(f"{W}author", ""),
                "date": c.attrib.get(f"{W}date", ""),
                "text": gather_text(c),
            })

    # commentRangeStart/End でアンカーテキストと、アンカーを含む段落の全文を拾う
    flat = list(doc.iter())
    anchors, contexts = {}, {}
    for p in paragraphs:
        for el in p.iter(f"{W}commentRangeStart"):
            contexts.setdefault(el.attrib.get(f"{W}id", ""), gather_text(p))
    for i, el in enumerate(flat):
        if el.tag == f"{W}commentRangeStart":
            cid = el.attrib.get(f"{W}id", "")
            for j in range(i + 1, len(flat)):
                e = flat[j]
                if e.tag == f"{W}commentRangeEnd" and e.attrib.get(f"{W}id") == cid:
                    anchors[cid] = "".join(
                        (x.text or "") for x in flat[i:j] if x.tag == f"{W}t"
                    )
                    break
    for c in comments:
        c["anchor_text"] = anchors.get(c["id"], "")
        c["paragraph_context"] = contexts.get(c["id"], "")

    report = {"tracked_changes": changes, "comments": comments}
    (report_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [f"# {docx_path.name} — track changes / comments\n",
          f"- 変更追跡: {len(changes)} 件",
          f"- コメント: {len(comments)} 件\n",
          "## トラック変更\n"]
    for i, c in enumerate(changes, 1):
        sign = "＋" if c["kind"] == "insert" else "−"
        md += [f"### {i}. {sign} {c['kind']} — {c['author']} @ {c['date']}",
               f"段落 #{c['paragraph_index']}", "",
               "**変更テキスト:**", "```", c["text"], "```",
               "**段落コンテキスト:**", "```", c["paragraph_context"], "```", ""]
    md.append("## コメント\n")
    for c in comments:
        md += [f"### コメント {c['id']} — {c['author']} @ {c['date']}",
               f"**アンカー:** `{c['anchor_text']}`", "", c["text"], ""]
    (report_dir / "report.md").write_text("\n".join(md), encoding="utf-8")
    print(f"changes={len(changes)} comments={len(comments)}")

if __name__ == "__main__":
    # 使い方: parse_docx_changes.py <docx> [<report_dir>]
    # report_dir を省略すると docx と同じフォルダに report.md / report.json を書く。
    # 生成した tracked docx を検証するときは、入力の report.json を上書きしないよう
    # 別フォルダ (例: output/) を指定する。
    main(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) > 2 else None)
