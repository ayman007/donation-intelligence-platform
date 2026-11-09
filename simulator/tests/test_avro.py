import io

import fastavro
import pytest
from fastavro.validation import ValidationError

from dip_simulator.avro_io import (
    check_contract,
    load_raw_schema,
    load_schema,
    to_record,
    validate_events,
)
from dip_simulator.config import SimConfig
from dip_simulator.simulation import run_simulation


@pytest.fixture(scope="module")
def events():
    return run_simulation(SimConfig(seed=42, n_days=2)).events


def _first(events, event_type):
    return dict(next(e for e in events if e["event_type"] == event_type))


def _old_data(events, schema, n=50):
    buffer = io.BytesIO()
    fastavro.writer(buffer, schema, [to_record(e) for e in events[:n]])
    buffer.seek(0)
    return buffer


def _schema_with(extra_field):
    raw = load_raw_schema()
    raw["fields"].append(extra_field)
    return fastavro.parse_schema(raw)


def test_schema_parses():
    assert load_schema()["name"] == "com.dip.events.AppEvent"


def test_all_simulated_events_are_valid(events):
    assert validate_events(events, load_schema()) == len(events)


def test_avro_roundtrip_preserves_data(events):
    schema = load_schema()
    rows = list(fastavro.reader(_old_data(events, schema, n=200)))
    assert len(rows) == 200
    for row, event in zip(rows, events):
        assert row["event_id"] == event["event_id"]
        assert row["event_ts"].isoformat() == event["event_ts"]
        assert row["amount_minor"] == event.get("amount_minor")


def test_missing_event_id_is_rejected(events):
    event = _first(events, "app_open")
    del event["event_id"]
    with pytest.raises(ValidationError):
        fastavro.validate(to_record(event), load_schema(), raise_errors=True)


def test_float_money_is_rejected(events):
    event = _first(events, "donation_started")
    event["amount_minor"] = 12.5
    with pytest.raises(ValidationError):
        fastavro.validate(to_record(event), load_schema(), raise_errors=True)


def test_contract_catches_missing_type_specific_field(events):
    event = _first(events, "donation_completed")
    event["payment_id"] = None
    with pytest.raises(ValueError):
        check_contract(event)


def test_unknown_event_type_is_rejected(events):
    event = _first(events, "app_open")
    event["event_type"] = "mystery"
    with pytest.raises(ValueError):
        check_contract(event)


def test_adding_optional_field_is_backward_compatible(events):
    old = load_schema()
    new = _schema_with({"name": "experiment_id", "type": ["null", "string"], "default": None})
    rows = list(fastavro.reader(_old_data(events, old), reader_schema=new))
    assert len(rows) == 50
    assert all(row["experiment_id"] is None for row in rows)


def test_adding_required_field_without_default_breaks_old_data(events):
    old = load_schema()
    new = _schema_with({"name": "experiment_id", "type": "string"})
    with pytest.raises(Exception):  # fastavro raises a schema resolution error
        list(fastavro.reader(_old_data(events, old), reader_schema=new))
