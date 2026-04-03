#!/usr/bin/env python3
"""Generate a markdown inventory for imported teaching materials."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from materials_lib import infer_category, load_extract_index


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_dir", help="Professor workspace or materials directory")
    parser.add_argument(
        "--output",
        default="materials_manifest.md",
        help="Markdown output file",
    )
    args = parser.parse_args(argv)

    target = Path(args.target_dir).resolve()
    if not target.exists():
        raise SystemExit(f"path not found: {target}")
    root = target / "materials" if (target / "materials").exists() else target
    workspace = target if (target / "materials").exists() else target.parent
    if not root.is_dir():
        raise SystemExit(f"materials path is not a directory: {root}")

    extract_index = {record["path"]: record for record in load_extract_index(workspace)}
    files = sorted(path for path in root.rglob("*") if path.is_file() and not path.name.startswith("."))
    grouped: dict[str, list[Path]] = defaultdict(list)
    for file_path in files:
        grouped[infer_category(file_path)].append(file_path)

    lines = [f"# Materials Manifest for `{root.name}`", ""]
    for category in sorted(grouped):
        lines.append(f"## {category}")
        lines.append("")
        for file_path in grouped[category]:
            relative = file_path.relative_to(root)
            relative_posix = str(relative).replace("\\", "/")
            size_kb = max(1, round(file_path.stat().st_size / 1024))
            record = extract_index.get((root.name + "/" + relative_posix).replace("materials/materials", "materials"))
            if not record and workspace != root:
                record = extract_index.get(f"materials/{relative_posix}")
            extra = ""
            if record:
                extra = f", extract={record.get('extract_status')}"
                if record.get("extracted_path"):
                    extra += f", text={record.get('text_length', 0)} chars"
            lines.append(f"- `{relative}` ({size_kb} KB{extra})")
        lines.append("")

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = workspace / output_path if workspace != root else root / output_path
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(output_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
