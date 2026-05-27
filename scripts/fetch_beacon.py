#!/usr/bin/env python3
"""Fetch a single drand round and write it to ``beacon.json``.

This is the only script in the repository that needs network access. It
queries the public drand HTTP API for one round and stores the fields the
draw and verifier need: round number, randomness, signature, and previous
signature.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests

# League of Entropy mainnet, classic (chained, 30s period) chain.
# Override these if you target a different drand chain.
CHAIN_HASH = "8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce"
BASE_URL = "https://api.drand.sh"
TIMEOUT_SECONDS = 30


def fetch_round(round_number: int) -> dict:
    """Fetch *round_number* from the drand HTTP API and return the beacon dict."""
    url = f"{BASE_URL}/{CHAIN_HASH}/public/{round_number}"
    response = requests.get(url, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()
    return {
        "round": data["round"],
        "randomness": data["randomness"],
        "signature": data["signature"],
        "previous_signature": data["previous_signature"],
    }


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="Fetch a drand round.")
    parser.add_argument(
        "--round",
        type=int,
        required=True,
        help="The drand round number to fetch.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("beacon.json"),
        help="Where to write the beacon JSON file.",
    )
    args = parser.parse_args(argv)

    beacon = fetch_round(args.round)
    args.output.write_text(
        json.dumps(beacon, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Wrote {args.output} for round {beacon['round']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
