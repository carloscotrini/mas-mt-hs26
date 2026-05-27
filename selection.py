#!/usr/bin/env python3
"""Deterministic verifiable random draw for the master thesis selection.

Reads every submission pool in ``submissions/*.json`` together with a drand
beacon (``beacon.json``) and produces a full per-TA ranking in ``result.json``.

The draw is deterministic: given the same beacon value and the same
submissions it always produces byte-identical output, so anyone can recompute
it to audit the result. See ``verify_draw.py`` for the one-command auditor.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def score(beacon_value: str, ta: str, submission_id: str) -> str:
    """Return the SHA-256 draw score for a single submission.

    The score is a deterministic function of the public beacon randomness,
    the TA slug, and the submission id. Sorting a TA's submissions by this
    score (ascending) yields a uniformly random, publicly verifiable order.
    """
    payload = f"{beacon_value}|{ta}|{submission_id}".encode()
    return hashlib.sha256(payload).hexdigest()


def load_submissions(submissions_dir: Path) -> dict[str, list[dict[str, Any]]]:
    """Load every ``<ta_slug>.json`` pool found in *submissions_dir*.

    The TA slug is taken from the file name (its stem). Each file must contain
    a JSON array of submission objects.
    """
    pools: dict[str, list[dict[str, Any]]] = {}
    for path in sorted(submissions_dir.glob("*.json")):
        ta = path.stem
        with path.open(encoding="utf-8") as handle:
            entries = json.load(handle)
        if not isinstance(entries, list):
            raise ValueError(
                f"{path}: expected a JSON array, got {type(entries).__name__}"
            )
        pools[ta] = entries
    return pools


def rank_pool(
    beacon_value: str, ta: str, entries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Rank one TA's pool by ascending score (rank 1 is the selected entry)."""
    scored = [
        {
            "id": entry["id"],
            "topic": entry.get("topic", ""),
            "score": score(beacon_value, ta, entry["id"]),
        }
        for entry in entries
    ]
    scored.sort(key=lambda item: item["score"])
    return [
        {
            "rank": index + 1,
            "id": item["id"],
            "topic": item["topic"],
            "score": item["score"],
        }
        for index, item in enumerate(scored)
    ]


def run_draw(submissions_dir: Path, beacon: dict[str, Any]) -> dict[str, Any]:
    """Compute the full draw result from the submissions and a loaded beacon."""
    beacon_value = beacon["randomness"]
    pools = load_submissions(submissions_dir)
    selections = {
        ta: rank_pool(beacon_value, ta, entries) for ta, entries in pools.items()
    }
    return {
        "beacon_round": beacon["round"],
        "beacon_randomness": beacon_value,
        "selections": selections,
    }


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point for the draw."""
    parser = argparse.ArgumentParser(
        description="Run the deterministic thesis-selection draw."
    )
    parser.add_argument(
        "--submissions",
        type=Path,
        default=Path("submissions"),
        help="Directory holding one <ta_slug>.json pool per TA.",
    )
    parser.add_argument(
        "--beacon",
        type=Path,
        default=Path("beacon.json"),
        help="Path to the drand beacon JSON file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("result.json"),
        help="Where to write the computed result.",
    )
    args = parser.parse_args(argv)

    with args.beacon.open(encoding="utf-8") as handle:
        beacon = json.load(handle)
    if beacon.get("placeholder"):
        parser.error(
            f"{args.beacon} is still a placeholder; fetch a real beacon first."
        )

    result = run_draw(args.submissions, beacon)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    ranked = sum(len(entries) for entries in result["selections"].values())
    print(f"Wrote {args.output} ({ranked} ranked entries across "
          f"{len(result['selections'])} TAs).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
