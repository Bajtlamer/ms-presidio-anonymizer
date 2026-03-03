#!/usr/bin/env python3
"""
CLI tool for anonymizing and deanonymizing Markdown files.

Usage:
  python cli.py anonymize report.md
    -> creates report.anon.md  and  report.anon.map

  python cli.py deanonymize report.anon.md --map report.anon.map
    -> creates report.anon.deanon.md  (or prints to stdout with --stdout)

  python cli.py anonymize report.md --stdout
    -> prints anonymized content to stdout (pipe directly to claude)
"""

import argparse
import json
import sys
from pathlib import Path
from core import anonymize_markdown, deanonymize_markdown, ReplacementMap


def cmd_anonymize(args):
    src = Path(args.file)
    if not src.exists():
        print(f"Error: file not found: {src}", file=sys.stderr)
        sys.exit(1)

    text = src.read_text(encoding="utf-8")
    anonymized, rmap = anonymize_markdown(text)

    if args.stdout:
        print(anonymized)
        return

    out_md  = src.with_suffix("").with_suffix(".anon.md")
    out_map = src.with_suffix("").with_suffix(".anon.map")

    out_md.write_text(anonymized, encoding="utf-8")
    out_map.write_text(json.dumps(rmap.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Anonymized : {out_md}")
    print(f"Map saved  : {out_map}")
    print(f"Entities replaced: {len(rmap.to_dict())}")


def cmd_deanonymize(args):
    src = Path(args.file)
    if not src.exists():
        print(f"Error: file not found: {src}", file=sys.stderr)
        sys.exit(1)

    map_path = Path(args.map) if args.map else src.with_suffix("").with_suffix(".anon.map")
    if not map_path.exists():
        print(f"Error: map file not found: {map_path}", file=sys.stderr)
        sys.exit(1)

    text     = src.read_text(encoding="utf-8")
    map_data = json.loads(map_path.read_text(encoding="utf-8"))
    rmap     = ReplacementMap.from_dict(map_data)

    restored = deanonymize_markdown(text, rmap)

    if args.stdout:
        print(restored)
        return

    out = src.with_name(src.stem + ".deanon.md")
    out.write_text(restored, encoding="utf-8")
    print(f"Deanonymized: {out}")


def main():
    parser = argparse.ArgumentParser(description="Markdown PII anonymizer for Obsidian + Claude CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_anon = sub.add_parser("anonymize", aliases=["anon"], help="Anonymize a Markdown file")
    p_anon.add_argument("file", help="Input .md file")
    p_anon.add_argument("--stdout", action="store_true", help="Print to stdout instead of writing files")

    p_deanon = sub.add_parser("deanonymize", aliases=["deanon"], help="Restore original values")
    p_deanon.add_argument("file", help="Anonymized .md file")
    p_deanon.add_argument("--map", help="Path to .map file (default: same name as file)")
    p_deanon.add_argument("--stdout", action="store_true")

    args = parser.parse_args()
    if args.command in ("anonymize", "anon"):
        cmd_anonymize(args)
    else:
        cmd_deanonymize(args)


if __name__ == "__main__":
    main()