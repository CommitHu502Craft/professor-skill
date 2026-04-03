#!/usr/bin/env python3
"""Build a source brief from imported professor materials."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from materials_lib import extract_keywords, load_extract_index, normalize_text

CATEGORY_ORDER = [
    "exams",
    "assignments",
    "transcripts",
    "slides",
    "syllabus",
    "chats",
    "notices",
    "misc",
]

def read_text_preview(path: Path, char_limit: int = 1200) -> str:
    if not path.exists():
        return ""
    text = normalize_text(path.read_text(encoding="utf-8"))
    return text[:char_limit].strip()


def update_meta(meta_path: Path, summary: dict[str, object]) -> None:
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["sources"] = summary["sources"]
    meta["notes"] = summary["notes"]
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("professor_dir", help="Professor workspace directory")
    parser.add_argument("--output", default="source_brief.md", help="Output markdown file")
    parser.add_argument("--update-meta", action="store_true", help="Write source summary into meta.json")
    args = parser.parse_args(argv)

    root = Path(args.professor_dir).resolve()
    materials_root = root / "materials"
    if not root.exists():
        raise SystemExit(f"professor workspace not found: {root}")
    if not materials_root.exists():
        raise SystemExit(f"materials directory not found: {materials_root}")
    grouped: dict[str, list[Path]] = defaultdict(list)
    text_samples: list[str] = []
    source_records: list[dict[str, object]] = []
    records = load_extract_index(root)

    for record in records:
        category = str(record["category"])
        grouped[category].append(Path(str(record["path"])))
        preview = ""
        extracted_path = record.get("extracted_path")
        if extracted_path and record.get("extract_status") == "ok":
            preview = read_text_preview(root / str(extracted_path))
            if preview:
                text_samples.append(preview)
        source_records.append(record)

    keywords = extract_keywords(text_samples)
    notes = []
    if grouped.get("exams"):
        notes.append("Exam materials are present and should dominate review and likely-question synthesis.")
    else:
        notes.append("No exam materials found; review guidance should be marked lower-confidence.")
    if grouped.get("transcripts") or grouped.get("chats"):
        notes.append("Persona evidence exists from conversational sources.")
    else:
        notes.append("Persona evidence is thin; rely more on user-supplied impressions and explicit caveats.")

    lines = [f"# Source Brief for `{root.name}`", ""]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total files: `{len(records)}`")
    lines.append(f"- Categories present: `{', '.join(category for category in CATEGORY_ORDER if grouped.get(category)) or 'none'}`")
    lines.append(f"- High-frequency keywords: `{', '.join(keywords) if keywords else 'none detected'}`")
    lines.append("")

    lines.append("## Notes")
    lines.append("")
    for note in notes:
        lines.append(f"- {note}")
    lines.append("")

    for category in CATEGORY_ORDER:
        category_files = [record for record in records if record["category"] == category]
        if not category_files:
            continue
        lines.append(f"## {category}")
        lines.append("")
        for record in category_files:
            relative = str(record["path"])
            lines.append(f"### `{relative}`")
            lines.append("")
            lines.append(f"- Size: `{max(1, round(int(record['bytes']) / 1024))} KB`")
            lines.append(f"- Extract status: `{record.get('extract_status')}`")
            if record.get("extracted_path"):
                preview = read_text_preview(root / str(record["extracted_path"]), char_limit=320)
                if preview:
                    condensed = re.sub(r"\s+", " ", preview)
                    lines.append(f"- Preview: `{condensed[:220]}`")
            lines.append("")

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = root / output_path
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    if args.update_meta:
        summary = {"sources": source_records, "notes": notes}
        update_meta(root / "meta.json", summary)

    print(output_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
