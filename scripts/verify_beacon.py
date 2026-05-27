#!/usr/bin/env python3
"""Verify the BLS signature in ``beacon.json`` against the drand group key.

The draw is seeded by a randomness value from the drand beacon run by the
League of Entropy. This script checks two things about a fetched beacon:

1. The BLS signature is valid under the chain's public group key. drand's
   classic (chained) mainnet signs the message ``SHA-256(prev_sig || round)``
   on curve G2 using the IETF "basic" ciphersuite
   (``BLS_SIG_BLS12381G2_XMD:SHA-256_SSWU_RO_NUL_``), which matches
   ``py_ecc.bls.G2Basic``.
2. The published randomness equals ``SHA-256(signature)``.

Exits 0 if both checks pass, non-zero otherwise.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from py_ecc.bls import G2Basic

# League of Entropy mainnet, classic (chained, 30s period) chain.
# Override these if you target a different drand chain.
CHAIN_HASH = "8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce"
CHAIN_PUBLIC_KEY = (
    "868f005eb8e6e4ca0a47c8a77ceaa5309a47978a7c71bc5cce96366b5d7a569937c"
    "529eeda66c7293784a9402801af31"
)


def beacon_message(round_number: int, previous_signature_hex: str) -> bytes:
    """Return the message that drand's classic chain signs for a round."""
    previous_signature = bytes.fromhex(previous_signature_hex)
    return hashlib.sha256(
        previous_signature + round_number.to_bytes(8, "big")
    ).digest()


def verify(beacon: dict) -> None:
    """Raise ``ValueError`` if the beacon's signature or randomness is wrong."""
    if beacon.get("placeholder"):
        raise ValueError("beacon is a placeholder; nothing to verify yet")

    round_number = int(beacon["round"])
    signature = bytes.fromhex(beacon["signature"])
    public_key = bytes.fromhex(CHAIN_PUBLIC_KEY)
    message = beacon_message(round_number, beacon["previous_signature"])

    if not G2Basic.Verify(public_key, message, signature):
        raise ValueError(f"BLS signature verification failed for round {round_number}")

    expected_randomness = hashlib.sha256(signature).hexdigest()
    if beacon["randomness"] != expected_randomness:
        raise ValueError(
            "randomness does not match SHA-256(signature): "
            f"expected {expected_randomness}, got {beacon['randomness']}"
        )


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="Verify a drand beacon signature.")
    parser.add_argument(
        "--beacon",
        type=Path,
        default=Path("beacon.json"),
        help="Path to the beacon JSON file to verify.",
    )
    args = parser.parse_args(argv)

    with args.beacon.open(encoding="utf-8") as handle:
        beacon = json.load(handle)

    try:
        verify(beacon)
    except (ValueError, KeyError) as error:
        print(f"BEACON INVALID: {error}")
        return 1

    print(f"Beacon round {beacon['round']} verified against chain {CHAIN_HASH}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
