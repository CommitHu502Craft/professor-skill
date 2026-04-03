#!/usr/bin/env python3
"""Validate whether a professor workspace is ready for skill use."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from materials_lib import load_extract_index


REQUIRED_FILES = [
    "meta.json",
    "persona.md",
    "course.md",
    "review_guide.md",
    "materials_manifest.md",
    "source_brief.md",
]
MIN_LENGTHS = {
    "persona.md": 160,
    "course.md": 160,
    "review_guide.md": 180,
}
MATERIAL_DIRS = [
    "slides",
    "syllabus",
    "exams",
    "assignments",
    "transcripts",
    "chats",
    "notices",
    "misc",
]


def count_materials(materials_root: Path) -> int:
    return sum(1 for path in materials_root.rglob("*") if path.is_file() and not path.name.startswith("."))


def placeholder_count(path: Path) -> int:
    if not path.exists():
        return 0
    return path.read_text(encoding="utf-8").count("[fill me]")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("professor_dir", help="Professor workspace directory")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as validation failures")
    args = parser.parse_args(argv)

    root = Path(args.professor_dir).resolve()
    if not root.exists():
        raise SystemExit(f"professor workspace not found: {root}")
    materials_root = root / "materials"

    errors: list[str] = []
    warnings: list[str] = []

    for filename in REQUIRED_FILES:
        if not (root / filename).exists():
            errors.append(f"Missing required file: {filename}")

    for dirname in MATERIAL_DIRS:
        if not (materials_root / dirname).exists():
            errors.append(f"Missing materials directory: materials/{dirname}")

    material_count = count_materials(materials_root) if materials_root.exists() else 0
    if material_count == 0:
        warnings.append("No material files found under materials/.")

    placeholders = sum(
        placeholder_count(root / filename)
        for filename in ("persona.md", "course.md", "review_guide.md")
    )
    if placeholders:
        warnings.append(f"Output files still contain `{placeholders}` placeholder markers.")

    meta_path = root / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if not meta.get("sources"):
            errors.append("meta.json has no indexed sources. Run the build pipeline again.")

    for filename, min_length in MIN_LENGTHS.items():
        path = root / filename
        if path.exists() and len(path.read_text(encoding="utf-8").strip()) < min_length:
            errors.append(f"{filename} is too short to be considered generated output.")

    index_records = load_extract_index(root)
    if not index_records:
        errors.append("No extraction index found. Run extract_materials.py or build_professor_outputs.py.")
    unsupported = [record for record in index_records if record.get("extract_status") in {"unsupported", "error"}]
    if unsupported:
        warnings.append(f"{len(unsupported)} source files were not parsed into text.")

    categories = {str(record["category"]) for record in index_records if record.get("extract_status") == "ok"}
    if "exams" not in categories:
        warnings.append("No parsed exam materials found; review guidance is lower confidence.")
    if "transcripts" not in categories and "chats" not in categories:
        warnings.append("No parsed transcript/chat materials found; persona quality is lower confidence.")

    if errors:
        print("STATUS: invalid")
        for error in errors:
            print(f"ERROR: {error}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        return 1

    if args.strict and warnings:
        print("STATUS: invalid")
        for warning in warnings:
            print(f"ERROR: {warning}")
        return 1

    print("STATUS: valid")
    print(f"MATERIAL_FILES: {material_count}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
