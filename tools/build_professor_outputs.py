#!/usr/bin/env python3
"""Single-command build entrypoint for professor skill workspaces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import extract_materials
import generate_outputs
import material_manifest
import source_brief
import validate_professor


def run_or_raise(fn, *args, **kwargs) -> int:
    result = fn(*args, **kwargs)
    if result not in (0, None):
        raise SystemExit(result)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("professor_dir", help="Professor workspace directory")
    parser.add_argument("--strict", action="store_true", help="Fail if warnings are present during validation")
    parser.add_argument("--skip-validate", action="store_true", help="Skip final validation step")
    parser.add_argument("--refresh-extracts", action="store_true", help="Accepted for API stability; extraction refresh is default")
    args = parser.parse_args()

    root = Path(args.professor_dir).resolve()
    if not root.exists():
        raise SystemExit(f"professor workspace not found: {root}")

    run_or_raise(extract_materials.main, [str(root), "--update-meta"])
    run_or_raise(material_manifest.main, [str(root), "--output", str(root / "materials_manifest.md")])
    run_or_raise(source_brief.main, [str(root), "--update-meta"])
    run_or_raise(generate_outputs.main, [str(root)])

    if not args.skip_validate:
        validation_args = [str(root)]
        if args.strict:
            validation_args.append("--strict")
        run_or_raise(validate_professor.main, validation_args)

    summary = {
        "workspace": str(root),
        "manifest": str(root / "materials_manifest.md"),
        "brief": str(root / "source_brief.md"),
        "persona": str(root / "persona.md"),
        "course": str(root / "course.md"),
        "review": str(root / "review_guide.md"),
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
