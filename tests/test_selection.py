"""Unit tests for the deterministic thesis-selection draw."""
from __future__ import annotations

import json
import secrets
from collections import Counter
from pathlib import Path

import pytest

import selection

FIXTURES = Path(__file__).parent / "fixtures"
FIXTURE_SUBMISSIONS = FIXTURES / "submissions"
FIXTURE_BEACON = FIXTURES / "beacon.json"
FIXTURE_RESULT = FIXTURES / "result.json"


@pytest.fixture()
def beacon() -> dict:
    """Load the synthetic fixture beacon."""
    with FIXTURE_BEACON.open(encoding="utf-8") as handle:
        return json.load(handle)


def test_matches_committed_fixture_result(beacon: dict) -> None:
    """The fixtures' result.json reproduces exactly from the inputs."""
    recomputed = selection.run_draw(FIXTURE_SUBMISSIONS, beacon)
    with FIXTURE_RESULT.open(encoding="utf-8") as handle:
        committed = json.load(handle)
    assert recomputed == committed


def test_determinism(beacon: dict) -> None:
    """Repeated runs over the same inputs produce identical output."""
    first = selection.run_draw(FIXTURE_SUBMISSIONS, beacon)
    second = selection.run_draw(FIXTURE_SUBMISSIONS, beacon)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_independence_of_ta_order(beacon: dict) -> None:
    """A TA's ranking does not depend on which other TAs are present."""
    full = selection.run_draw(FIXTURE_SUBMISSIONS, beacon)
    winston_entries = json.loads(
        (FIXTURE_SUBMISSIONS / "winston.json").read_text(encoding="utf-8")
    )
    isolated = selection.rank_pool(beacon["randomness"], "winston", winston_entries)
    assert isolated == full["selections"]["winston"]


def test_schema(beacon: dict) -> None:
    """Output validates against the expected JSON shape."""
    result = selection.run_draw(FIXTURE_SUBMISSIONS, beacon)
    assert set(result) == {"beacon_round", "beacon_randomness", "selections"}
    assert isinstance(result["beacon_round"], int)
    assert isinstance(result["beacon_randomness"], str)
    for ranking in result["selections"].values():
        assert [entry["rank"] for entry in ranking] == list(
            range(1, len(ranking) + 1)
        )
        for entry in ranking:
            assert set(entry) == {"rank", "id", "topic", "score"}
            assert len(entry["score"]) == 64
            int(entry["score"], 16)  # score is valid hex


def test_fairness() -> None:
    """Across many random beacons each entry reaches rank 1 about 1/n of the time."""
    n = 6
    ta = "winston"
    entries = [{"id": secrets.token_hex(8), "topic": f"t{i}"} for i in range(n)]
    trials = 12000
    rank1 = Counter()
    for _ in range(trials):
        beacon_value = secrets.token_hex(32)
        ranking = selection.rank_pool(beacon_value, ta, entries)
        rank1[ranking[0]["id"]] += 1

    expected = trials / n
    tolerance = 0.25 * expected  # generous band for a probabilistic test
    for entry in entries:
        assert abs(rank1[entry["id"]] - expected) < tolerance, (
            f"{entry['id']} won {rank1[entry['id']]} times; expected ~{expected:.0f}"
        )


def test_empty_pool_is_allowed(beacon: dict, tmp_path: Path) -> None:
    """An empty pool (pre-submission state) ranks to an empty list."""
    (tmp_path / "newbie.json").write_text("[]", encoding="utf-8")
    result = selection.run_draw(tmp_path, beacon)
    assert result["selections"]["newbie"] == []
