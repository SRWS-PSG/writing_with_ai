"""versions_ledger.py — バージョン台帳 (versions.md) の管理と、内容ハッシュによる
アップロード事故防止。

`rclone copy` で同じファイル名の docx を同じ Drive フォルダに入れると、既存の
Google Doc が同じファイル ID のまま上書きされ、共著者が付けたコメントスレッドが
docx の内容から作り直されて消える (2026-09-13 実測)。これを防ぐため、

- アップロードするファイル名には docx の内容ハッシュを埋め込む (`name` サブコマンド)
- アップロード前に、同じ内容の docx を過去にアップロード済みでないか確認する (`check`)
- アップロード後、新しい Doc ID が発行されたことを台帳に記録する (`record`)。
  doc_id が既存行と重複していれば、それは新規 Doc ではなく上書きが起きた徴候。

台帳ファイル: `projects/<name>/versions/versions.md` (Markdown 表、標準ライブラリのみ)。

    python versions_ledger.py name --docx v2.docx --stem draft_v2_tracked
    python versions_ledger.py check --ledger versions/versions.md --docx v2.docx
    python versions_ledger.py record --ledger versions/versions.md --version v2 \
        --md draft.md --docx v2.docx --doc-id <FILE_ID>
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import re
import shutil
import sys
from pathlib import Path

HEADER = ["version", "date_utc", "doc_id", "md_sha256", "docx_sha256", "docx_name", "md_snapshot"]
SEP_ROW_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- table parsing
def parse_ledger(path: Path) -> list[dict]:
    """台帳を読む。ファイルが無ければ空リスト (空の台帳として扱う)。
    表の前後に地の文があっても、ヘッダー行 (列名が完全一致) を見つけてそこから読む。"""
    if not path.exists():
        return []
    rows: list[dict] = []
    header_seen = False
    for raw_line in path.read_text(encoding="utf-8").split("\n"):
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not header_seen:
            if cells == HEADER:
                header_seen = True
            continue
        if SEP_ROW_RE.match(line):
            continue
        if len(cells) != len(HEADER):
            continue
        rows.append(dict(zip(HEADER, cells)))
    return rows


def append_row(path: Path, row: dict) -> None:
    row_line = "| " + " | ".join(row[h] for h in HEADER) + " |"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        header_line = "| " + " | ".join(HEADER) + " |"
        sep_line = "|" + "|".join(" --- " for _ in HEADER) + "|"
        content = "\n".join([header_line, sep_line, row_line]) + "\n"
        path.write_text(content, encoding="utf-8", newline="\n")
        return

    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # 台帳の表 (ヘッダー行が完全一致する表) を見つける。ファイル内に他の Markdown
    # 表が前後にあっても、それらの行を巻き込まないよう、ヘッダーから始まる
    # 連続した行の範囲だけを「この表」とみなす。
    header_idx = None
    for idx, l in enumerate(lines):
        ls = l.strip()
        if not ls.startswith("|"):
            continue
        cells = [c.strip() for c in ls.strip("|").split("|")]
        if cells == HEADER:
            header_idx = idx
            break

    if header_idx is not None:
        last_row_idx = header_idx
        i = header_idx + 1
        if i < len(lines) and SEP_ROW_RE.match(lines[i].strip()):
            last_row_idx = i
            i += 1
        while i < len(lines) and lines[i].strip().startswith("|"):
            last_row_idx = i
            i += 1
        lines.insert(last_row_idx + 1, row_line)
        new_text = "\n".join(lines)
        if not new_text.endswith("\n"):
            new_text += "\n"
        path.write_text(new_text, encoding="utf-8", newline="\n")
        return

    # 表が見つからない (壊れた台帳など): 末尾に新しい表を追加する
    if text and not text.endswith("\n"):
        text += "\n"
    if text and not text.endswith("\n\n"):
        text += "\n"
    header_line = "| " + " | ".join(HEADER) + " |"
    sep_line = "|" + "|".join(" --- " for _ in HEADER) + "|"
    text += "\n".join([header_line, sep_line, row_line]) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def format_row(row: dict) -> str:
    return ", ".join(f"{k}={row.get(k, '')}" for k in HEADER)


# ---------------------------------------------------------------- subcommands
def cmd_name(args: argparse.Namespace) -> int:
    docx = Path(args.docx)
    digest = sha256_of(docx)[:8]
    print(f"{args.stem}_{digest}.docx")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    ledger = Path(args.ledger)
    docx = Path(args.docx)
    digest = sha256_of(docx)
    rows = parse_ledger(ledger)
    for row in rows:
        if row.get("docx_sha256") == digest:
            print(
                "このdocxは既に台帳に記録済みです。再アップロードしないでください。\n"
                f"該当行: {format_row(row)}"
            )
            return 3
    print("未アップロードの内容です。")
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    ledger = Path(args.ledger)
    md = Path(args.md)
    docx = Path(args.docx)
    version = args.version
    doc_id = args.doc_id

    rows = parse_ledger(ledger)
    for row in rows:
        if row.get("doc_id") == doc_id:
            print(
                "エラー: この doc_id は既に台帳にあります。アップロードが既存の Google Doc を"
                "上書きした可能性があります。Drive 上のファイル (コメントが残っているか) を確認してください。\n"
                f"該当行: {format_row(row)}"
            )
            return 3

    docx_digest = sha256_of(docx)
    for row in rows:
        if row.get("docx_sha256") == docx_digest:
            print(
                "エラー: 同じ内容の docx が既に台帳にあります。再アップロードしないでください。\n"
                f"該当行: {format_row(row)}"
            )
            return 3

    for row in rows:
        if row.get("version") == version:
            print(
                f"エラー: バージョン {version} は既に台帳にあります。\n"
                f"該当行: {format_row(row)}"
            )
            return 3

    md_digest = sha256_of(md)
    date_utc = args.date or _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    snapshot_name = f"{md.stem}.{version}.md"
    snapshot_path = ledger.parent / snapshot_name
    if snapshot_path.exists():
        existing = snapshot_path.read_bytes()
        new_bytes = md.read_bytes()
        if existing != new_bytes:
            print(
                "エラー: スナップショット "
                f"{snapshot_path} が既に存在し、内容が異なります。上書きしません。"
            )
            return 3
        # 内容が同じなら何もしない (再実行に耐える)
    else:
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(md, snapshot_path)

    row = {
        "version": version,
        "date_utc": date_utc,
        "doc_id": doc_id,
        "md_sha256": md_digest,
        "docx_sha256": docx_digest,
        "docx_name": docx.name,
        "md_snapshot": snapshot_name,
    }
    append_row(ledger, row)
    print(f"記録しました: {format_row(row)}")
    return 0


# ---------------------------------------------------------------- main
def main() -> int:
    try:  # Windows の cp932 コンソールで日本語メッセージが落ちないように
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)

    p_name = sub.add_parser("name", help="内容ハッシュ付きのアップロード用ファイル名を作る")
    p_name.add_argument("--docx", required=True, type=Path)
    p_name.add_argument("--stem", required=True)
    p_name.set_defaults(func=cmd_name)

    p_check = sub.add_parser("check", help="この docx が台帳に無いか確認する")
    p_check.add_argument("--ledger", required=True, type=Path)
    p_check.add_argument("--docx", required=True, type=Path)
    p_check.set_defaults(func=cmd_check)

    p_record = sub.add_parser("record", help="アップロード結果を台帳に記録する")
    p_record.add_argument("--ledger", required=True, type=Path)
    p_record.add_argument("--version", required=True)
    p_record.add_argument("--md", required=True, type=Path)
    p_record.add_argument("--docx", required=True, type=Path)
    p_record.add_argument("--doc-id", required=True, dest="doc_id")
    p_record.add_argument("--date", help="ISO 8601 UTC。省略時は現在時刻")
    p_record.set_defaults(func=cmd_record)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
