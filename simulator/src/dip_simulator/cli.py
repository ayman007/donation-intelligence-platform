import argparse
import json
import random
from collections import Counter
from pathlib import Path

from dip_simulator.avro_io import load_schema, validate_events, write_avro
from dip_simulator.config import SimConfig
from dip_simulator.generators import generate_campaigns, generate_donors
from dip_simulator.ids import IdFactory
from dip_simulator.simulation import run_simulation
from dip_simulator.writers import write_csv, write_jsonl


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="dip-simulator")
    sub = parser.add_subparsers(dest="command", required=True)

    batch = sub.add_parser("batch", help="Generate campaigns and donors as CSV files")
    batch.add_argument("--seed", type=int, default=42)
    batch.add_argument("--out", default="output")

    events = sub.add_parser("events", help="Simulate days of app activity")
    events.add_argument("--seed", type=int, default=42)
    events.add_argument("--days", type=int, default=7)
    events.add_argument("--out", default="output")

    validate = sub.add_parser("validate", help="Validate events.jsonl and write events.avro")
    validate.add_argument("--events", default="output/events.jsonl")
    validate.add_argument("--out", default="output")

    args = parser.parse_args(argv)
    out = Path(args.out)

    if args.command == "batch":
        cfg = SimConfig(seed=args.seed)
        rng = random.Random(cfg.seed)
        ids = IdFactory(rng)
        campaigns = generate_campaigns(cfg, rng, ids)
        donors = generate_donors(cfg, rng, ids)
        write_csv(out / "campaigns.csv", campaigns)
        write_csv(out / "donors.csv", donors)
        print(f"Wrote {len(campaigns)} campaigns and {len(donors)} donors to {out}")

    elif args.command == "events":
        cfg = SimConfig(seed=args.seed, n_days=args.days)
        result = run_simulation(cfg)
        write_csv(out / "campaigns.csv", result.campaigns)
        write_csv(out / "donors.csv", result.donors)
        write_csv(out / "payments.csv", result.payments)
        write_jsonl(out / "events.jsonl", result.events)
        counts = Counter(e["event_type"] for e in result.events)
        print(f"Wrote {len(result.events)} events, {len(result.payments)} payments to {out}")
        for event_type, n in sorted(counts.items()):
            print(f"  {event_type}: {n}")

    elif args.command == "validate":
        source = Path(args.events)
        with source.open(encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle]
        schema = load_schema()
        n = validate_events(rows, schema)
        avro_path = out / "events.avro"
        write_avro(avro_path, schema, rows)
        print(f"{n} events are valid against app_event.avsc")
        print(f"events.jsonl: {source.stat().st_size:,} bytes")
        print(f"events.avro:  {avro_path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
