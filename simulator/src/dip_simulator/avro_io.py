import json
from datetime import datetime
from pathlib import Path

import fastavro

# simulator/src/dip_simulator/avro_io.py -> parents[3] is the repo root
SCHEMA_PATH = Path(__file__).resolve().parents[3] / "kafka" / "schemas" / "app_event.avsc"

OPTIONAL_FIELDS = (
    "device_country",
    "campaign_id",
    "position_in_feed",
    "source",
    "amount_minor",
    "currency",
    "payment_id",
)

# Avro cannot say "required for this event type", so we enforce it here.
REQUIRED_BY_TYPE = {
    "app_open": ("device_country",),
    "campaign_view": ("campaign_id", "position_in_feed", "source"),
    "donation_started": ("campaign_id", "amount_minor", "currency"),
    "donation_completed": ("campaign_id", "payment_id", "amount_minor", "currency"),
}


def load_raw_schema(path=SCHEMA_PATH) -> dict:
    # utf-8-sig also reads files that start with a BOM (Windows PowerShell adds one)
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def load_schema(path=SCHEMA_PATH):
    return fastavro.parse_schema(load_raw_schema(path))


def to_record(event: dict) -> dict:
    """Turn a JSON event into an Avro record: parse the timestamp, fill optionals."""
    record = {name: None for name in OPTIONAL_FIELDS}
    record.update(event)
    record["event_ts"] = datetime.fromisoformat(event["event_ts"])
    return record


def check_contract(event: dict) -> None:
    required = REQUIRED_BY_TYPE.get(event["event_type"])
    if required is None:
        raise ValueError(f"unknown event_type: {event['event_type']}")
    missing = [name for name in required if event.get(name) is None]
    if missing:
        raise ValueError(f"{event['event_type']} is missing {missing}")


def validate_events(events, schema) -> int:
    count = 0
    for event in events:
        check_contract(event)
        fastavro.validate(to_record(event), schema, raise_errors=True)
        count += 1
    return count


def write_avro(path, schema, events) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        fastavro.writer(handle, schema, (to_record(e) for e in events))
