#!/usr/bin/env python3
"""Generate a unique submission id and a ready-to-paste JSON snippet.

A TA runs this when confirming a submission. It produces a 16-character hex id
that is guaranteed not to collide with any id already present in
``submissions/*.json``, then prints a JSON object the TA can append to their
own pool file.
"""
from __future__ import annotations

import argparse
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path


def existing_ids(submissions_dir: Path) -> set[str]:
    """Collect every submission id already present across all TA pools."""
    ids: set[str] = set()
    for path in sorted(submissions_dir.glob("*.json")):
        with path.open(encoding="utf-8") as handle:
            entries = json.load(handle)
        for entry in entries:
            ids.add(entry["id"])
    return ids


def new_id(taken: set[str]) -> str:
    """Return a fresh 16-character hex id not contained in *taken*."""
    while True:
        candidate = secrets.token_hex(8)
        if candidate not in taken:
            return candidate


def now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string ending in 'Z'."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description="Assign a unique submission id and print a JSON snippet."
    )
    parser.add_argument(
        "--topic",
        required=True,
        help="The thesis topic title for this submission.",
    )
    parser.add_argument(
        "--submissions",
        type=Path,
        default=Path("submissions"),
        help="Directory holding the existing TA pools (for collision checks).",
    )
    args = parser.parse_args(argv)

    taken = existing_ids(args.submissions) if args.submissions.exists() else set()
    submission_id = new_id(taken)
    snippet = {
        "id": submission_id,
        "topic": args.topic,
        "submitted_at": now_iso(),
    }

    print(f"Assigned id: {submission_id}")
    print("Append this object to the TA's submissions/<ta_slug>.json array:")
    print(json.dumps(snippet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
