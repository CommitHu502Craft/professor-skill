#!/usr/bin/env python3
"""Create a scaffold for a professor skill workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from materials_lib import MATERIAL_DIRS


def slugify(value: str) -> str:
    cleaned = []
    last_dash = False
    for ch in value.strip().lower():
        if ch.isascii() and ch.isalnum():
            cleaned.append(ch)
            last_dash = False
        else:
            if not last_dash:
                cleaned.append("-")
                last_dash = True
    slug = "".join(cleaned).strip("-")
    if slug:
        return slug

    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    return f"professor-{digest}"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_meta(name: str, slug: str, school: str, department: str, course: str) -> dict:
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "name": name,
        "slug": slug,
        "created_at": timestamp,
        "updated_at": timestamp,
        "profile": {
            "school": school,
            "department": department,
            "course": course,
        },
        "sources": [],
        "notes": [],
        "artifacts": {
            "persona": "persona.md",
            "course": "course.md",
            "review_guide": "review_guide.md",
            "materials_manifest": "materials_manifest.md",
            "source_brief": "source_brief.md",
            "extraction_index": "exports/extracted/index.json",
            "build_status": "initialized",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Professor name")
    parser.add_argument("--course", required=True, help="Course name")
    parser.add_argument("--school", default="", help="School name")
    parser.add_argument("--department", default="", help="Department name")
    parser.add_argument("--slug", help="Optional directory slug")
    parser.add_argument(
        "--base-dir",
        default="professors",
        help="Output directory for professor folders",
    )
    args = parser.parse_args()

    slug = args.slug or slugify(f"{args.course}-{args.name}")
    root = Path(args.base_dir).resolve() / slug
    ensure_dir(root)
    materials_root = root / "materials"
    exports_root = root / "exports"
    for dirname in MATERIAL_DIRS:
        ensure_dir(materials_root / dirname)
    ensure_dir(exports_root)

    meta = build_meta(args.name, slug, args.school, args.department, args.course)
    write_file(root / "meta.json", json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    write_file(
        root / "persona.md",
        f"# {args.name} - Persona\n\n"
        "## Identity\n\n"
        f"- School: {args.school or '[fill me]'}\n"
        f"- Department: {args.department or '[fill me]'}\n"
        f"- Course: {args.course}\n\n"
        "## Catchphrases\n\n- [fill me]\n\n"
        "## Style\n\n- [fill me]\n",
    )
    write_file(
        root / "course.md",
        f"# {args.course} - Course Brain\n\n"
        "## Core Topics\n\n- [fill me]\n\n"
        "## Exam Signals\n\n- [fill me]\n\n"
        "## Common Traps\n\n- [fill me]\n",
    )
    write_file(
        root / "review_guide.md",
        f"# {args.course} - Review Guide\n\n"
        "## Must Know\n\n- [fill me]\n\n"
        "## Likely Questions\n\n- [fill me]\n\n"
        "## Last-Night Checklist\n\n- [fill me]\n",
    )
    write_file(
        root / "materials_manifest.md",
        "# Materials Manifest\n\n"
        "Run `python tools/material_manifest.py "
        f"\"{(root / 'materials').as_posix()}\" --output \"{(root / 'materials_manifest.md').as_posix()}\"`\n"
        "after placing source files into `materials/`.\n",
    )
    write_file(
        root / "source_brief.md",
        "# Source Brief\n\n"
        "Run `python tools/source_brief.py "
        f"\"{root.as_posix()}\" --update-meta`\n"
        "to generate a source evidence brief from imported materials.\n",
    )
    write_file(
        root / "workflow.md",
        f"# {args.name} - Workflow\n\n"
        "## 1. Put files into `materials/`\n\n"
        "- `materials/slides/`\n"
        "- `materials/syllabus/`\n"
        "- `materials/exams/`\n"
        "- `materials/assignments/`\n"
        "- `materials/transcripts/`\n"
        "- `materials/chats/`\n"
        "- `materials/notices/`\n"
        "- `materials/misc/`\n\n"
        "## 2. Generate machine-readable source maps\n\n"
        f"```bash\npython tools/build_professor_outputs.py \"{root.as_posix()}\"\n```\n\n"
        "## 3. Use the skill\n\n"
        "Ask the agent to read `meta.json`, `materials_manifest.md`, `source_brief.md`, and the most relevant raw materials before generating or updating `persona.md`, `course.md`, and `review_guide.md`.\n",
    )

    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
