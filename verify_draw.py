#!/usr/bin/env python3
"""One-command auditor for the thesis-selection draw.

Anyone can run this against the committed inputs to confirm the published
result is correct. It:

1. Recomputes the draw from ``submissions/*.json`` and ``beacon.json`` and
   compares it byte-for-byte to the committed ``result.json``.
2. Verifies the beacon's BLS signature against the drand group key.

Exits 0 only if every check passes. It works fully offline once ``beacon.json``
exists; only ``scripts/fetch_beacon.py`` needs network access.

Usage::

    python verify_draw.py
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import selection

REPO_ROOT = Path(__file__).resolve().parent


def is_placeholder(data: dict) -> bool:
    """Return True if a beacon/result file is still an unfilled placeholder."""
    return bool(data.get("placeholder"))


def load_json(path: Path) -> dict:
    """Load a JSON object from *path*."""
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def verify(
    submissions_dir: Path,
    beacon_path: Path,
    result_path: Path,
    check_beacon: bool,
) -> int:
    """Run every audit step. Returns a process exit code."""
    beacon = load_json(beacon_path)
    if is_placeholder(beacon):
        print(
            "Beacon is still a placeholder: the draw has not happened yet. "
            "Nothing to verify."
        )
        return 0

    recomputed = selection.run_draw(submissions_dir, beacon)
    recomputed_text = json.dumps(recomputed, indent=2, sort_keys=True)

    committed = load_json(result_path)
    if is_placeholder(committed):
        print("Result is a placeholder but the beacon is filled. Inconsistent state.")
        return 1
    committed_text = json.dumps(committed, indent=2, sort_keys=True)

    if recomputed_text != committed_text:
        print("MISMATCH: recomputed result does not match the committed result.json.")
        return 1
    print("OK: recomputed result matches the committed result.json.")

    if check_beacon:
        verifier = REPO_ROOT / "scripts" / "verify_beacon.py"
        proc = subprocess.run(
            [sys.executable, str(verifier), "--beacon", str(beacon_path)],
            check=False,
        )
        if proc.returncode != 0:
            print("FAILED: beacon signature verification did not pass.")
            return 1
    else:
        print("SKIPPED: beacon signature verification (--no-beacon-verify).")

    print("All checks passed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="Audit the thesis-selection draw.")
    parser.add_argument("--submissions", type=Path, default=REPO_ROOT / "submissions")
    parser.add_argument("--beacon", type=Path, default=REPO_ROOT / "beacon.json")
    parser.add_argument("--result", type=Path, default=REPO_ROOT / "result.json")
    parser.add_argument(
        "--no-beacon-verify",
        action="store_true",
        help="Skip BLS verification (e.g. for synthetic test fixtures).",
    )
    args = parser.parse_args(argv)
    return verify(
        args.submissions, args.beacon, args.result, check_beacon=not args.no_beacon_verify
    )


if __name__ == "__main__":
    raise SystemExit(main())
