from collections import Counter
from functools import lru_cache

import pytest

from dip_simulator.avro_io import load_schema
from dip_simulator.config import SimConfig
from dip_simulator.faults import MALFORMED_KINDS, FaultConfig, _corrupt, inject_faults
from dip_simulator.quality import validate_event
from dip_simulator.simulation import run_simulation

SCHEMA = load_schema()


@lru_cache(maxsize=None)
def clean():
    return tuple(run_simulation(SimConfig(seed=42, n_days=3)).events)


@lru_cache(maxsize=None)
def dirty():
    return inject_faults(list(clean()), FaultConfig(seed=42))


def test_clean_events_pass_quality_checks():
    assert all(not validate_event(e, SCHEMA) for e in clean())


def test_same_seed_gives_identical_faults():
    a = inject_faults(list(clean()), FaultConfig(seed=7))
    b = inject_faults(list(clean()), FaultConfig(seed=7))
    assert a == b


def test_different_seed_gives_different_faults():
    a = inject_faults(list(clean()), FaultConfig(seed=7))
    b = inject_faults(list(clean()), FaultConfig(seed=8))
    assert a[1] != b[1]


def test_fault_counts_are_close_to_configured_rates():
    n, cfg = len(clean()), FaultConfig()
    _, manifest = dirty()
    for key, rate in (
        ("duplicates", cfg.duplicate_rate),
        ("late", cfg.late_rate),
        ("malformed", cfg.malformed_rate),
    ):
        expected = n * rate
        assert 0.5 * expected <= len(manifest[key]) <= 1.5 * expected


def test_duplicates_appear_exactly_twice():
    events, manifest = dirty()
    counts = Counter(e["event_id"] for e in events)
    assert manifest["duplicates"]
    assert all(counts[event_id] == 2 for event_id in manifest["duplicates"])


def test_late_events_arrive_after_their_clean_position():
    events, manifest = dirty()
    clean_pos = {e["event_id"]: i for i, e in enumerate(clean())}
    dirty_pos = {e["event_id"]: i for i, e in enumerate(events) if e.get("event_id")}
    moved = sum(dirty_pos[x["event_id"]] > clean_pos[x["event_id"]] for x in manifest["late"])
    assert moved / len(manifest["late"]) > 0.95


def test_dirty_stream_is_out_of_order():
    events, _ = dirty()
    stamps = [e["event_ts"] for e in events if not validate_event(e, SCHEMA)]
    assert any(a > b for a, b in zip(stamps, stamps[1:]))


def test_only_malformed_records_fail_quality_checks():
    events, manifest = dirty()
    invalid = [e for e in events if validate_event(e, SCHEMA)]
    assert len(invalid) == len(manifest["malformed"])


@pytest.mark.parametrize("kind", MALFORMED_KINDS)
def test_every_corruption_kind_is_detected(kind):
    event = next(e for e in clean() if e["event_type"] == "donation_started")
    assert validate_event(_corrupt(event, kind), SCHEMA)


def test_dedupe_and_filter_recovers_the_clean_stream():
    events, manifest = dirty()
    malformed_ids = {m["event_id"] for m in manifest["malformed"]}

    seen, recovered = set(), []
    for event in events:
        if validate_event(event, SCHEMA) or event["event_id"] in seen:
            continue
        seen.add(event["event_id"])
        recovered.append(event)
    recovered.sort(key=lambda e: e["event_ts"])

    expected_ids = {e["event_id"] for e in clean()} - malformed_ids
    assert {e["event_id"] for e in recovered} == expected_ids
    assert len(recovered) == len(expected_ids)
    stamps = [e["event_ts"] for e in recovered]
    assert stamps == sorted(stamps)
