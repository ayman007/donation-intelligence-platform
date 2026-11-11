import bisect
import random
from dataclasses import dataclass
from datetime import datetime, timedelta

MALFORMED_KINDS = (
    "missing_user_id",
    "string_amount",
    "negative_amount",
    "unknown_event_type",
    "bad_timestamp",
    "empty_event_id",
)
_ALWAYS_APPLICABLE = ("missing_user_id", "unknown_event_type", "bad_timestamp", "empty_event_id")


@dataclass(frozen=True)
class FaultConfig:
    seed: int = 42
    duplicate_rate: float = 0.01
    late_rate: float = 0.02
    malformed_rate: float = 0.005
    late_min_minutes: int = 5
    late_max_minutes: int = 360
    duplicate_max_delay_seconds: int = 300


def _corrupt(event: dict, kind: str) -> dict:
    bad = dict(event)
    if kind == "missing_user_id":
        bad.pop("user_id", None)
    elif kind == "string_amount":
        bad["amount_minor"] = str(bad["amount_minor"])
    elif kind == "negative_amount":
        bad["amount_minor"] = -abs(bad["amount_minor"])
    elif kind == "unknown_event_type":
        bad["event_type"] = "page_scroll"
    elif kind == "bad_timestamp":
        bad["event_ts"] = "not-a-timestamp"
    elif kind == "empty_event_id":
        bad["event_id"] = ""
    else:
        raise ValueError(f"unknown kind: {kind}")
    return bad


def inject_faults(events: list, cfg: FaultConfig) -> tuple[list, dict]:
    """Return (dirty_events in arrival order, manifest of what was injected).

    Each event gets at most one fault. The input must be sorted by event_ts.
    """
    rng = random.Random(cfg.seed * 1000 + 17)  # separate stream: clean data is untouched
    times = [datetime.fromisoformat(e["event_ts"]) for e in events]
    n = len(events)

    keyed = []  # (arrival_key, sequence, event); sorting by key gives arrival order
    manifest = {"duplicates": [], "late": [], "malformed": []}

    def add(key: float, event: dict) -> None:
        keyed.append((key, len(keyed), event))

    def key_after(pos: int, offset: float) -> float:
        # arrive just before the first event whose timestamp is >= the target time
        return pos - offset if pos < n else n + offset

    dup_end = cfg.duplicate_rate
    late_end = dup_end + cfg.late_rate
    bad_end = late_end + cfg.malformed_rate

    for i, event in enumerate(events):
        r = rng.random()
        if r < dup_end:
            add(i, event)
            delay = rng.randint(1, cfg.duplicate_max_delay_seconds)
            pos = bisect.bisect_left(times, times[i] + timedelta(seconds=delay))
            add(key_after(pos, 0.25), dict(event))
            manifest["duplicates"].append(event["event_id"])
        elif r < late_end:
            delay = rng.randint(cfg.late_min_minutes, cfg.late_max_minutes)
            pos = bisect.bisect_left(times, times[i] + timedelta(minutes=delay))
            add(key_after(pos, 0.5), event)
            manifest["late"].append({"event_id": event["event_id"], "delay_minutes": delay})
        elif r < bad_end:
            kinds = list(_ALWAYS_APPLICABLE)
            if event.get("amount_minor") is not None:
                kinds += ["string_amount", "negative_amount"]
            kind = rng.choice(kinds)
            add(i, _corrupt(event, kind))
            manifest["malformed"].append({"event_id": event["event_id"], "kind": kind})
        else:
            add(i, event)

    keyed.sort(key=lambda item: (item[0], item[1]))
    return [item[2] for item in keyed], manifest
