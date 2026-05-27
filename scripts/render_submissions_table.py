#!/usr/bin/env python3
"""Render ``docs/submissions.md`` from the canonical ``submissions/*.json``.

Produces a markdown page with one table per TA. Only submission ids, topics,
and timestamps are shown; participant names never appear in the repository.
CI runs this on every push so the public page stays in sync with the pools.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

PAGE_HEADER = """---
title: Submissions
nav_order: 4
---

# Live submissions

This page is generated automatically from the canonical submission pools in
`submissions/*.json`. It lists every confirmed submission by its assigned id
and topic. Participant names are never published here.
"""


def load_display_names(tas_file: Path) -> dict[str, str]:
    """Map TA slug -> display name from ``tas.yml`` (empty if unavailable)."""
    if not tas_file.exists():
        return {}
    with tas_file.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    names: dict[str, str] = {}
    for entry in data.get("tas", []):
        slug = entry.get("slug")
        if slug:
            names[slug] = entry.get("name", slug)
    return names


def render_table(entries: list[dict[str, Any]]) -> str:
    """Render one TA's pool as a markdown table."""
    if not entries:
        return "_No submissions yet._\n"
    lines = ["| ID | Topic | Submitted at |", "| --- | --- | --- |"]
    for entry in sorted(entries, key=lambda item: item.get("submitted_at", "")):
        topic = str(entry.get("topic", "")).replace("|", "\\|")
        lines.append(
            f"| `{entry['id']}` | {topic} | {entry.get('submitted_at', '')} |"
        )
    return "\n".join(lines) + "\n"


def render_page(submissions_dir: Path, tas_file: Path) -> str:
    """Render the full submissions markdown page."""
    display_names = load_display_names(tas_file)
    sections = [PAGE_HEADER]
    for path in sorted(submissions_dir.glob("*.json")):
        slug = path.stem
        with path.open(encoding="utf-8") as handle:
            entries = json.load(handle)
        heading = display_names.get(slug, slug)
        sections.append(f"\n## {heading}\n")
        sections.append(render_table(entries))
    return "\n".join(sections)


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description="Render docs/submissions.md from submissions/*.json."
    )
    parser.add_argument("--submissions", type=Path, default=Path("submissions"))
    parser.add_argument("--tas", type=Path, default=Path("tas.yml"))
    parser.add_argument("--output", type=Path, default=Path("docs/submissions.md"))
    args = parser.parse_args(argv)

    page = render_page(args.submissions, args.tas)
    args.output.write_text(page, encoding="utf-8")
    print(f"Wrote {args.output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
