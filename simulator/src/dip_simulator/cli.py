import argparse
import random
from pathlib import Path

from dip_simulator.config import SimConfig
from dip_simulator.generators import generate_campaigns, generate_donors
from dip_simulator.ids import IdFactory
from dip_simulator.writers import write_csv


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="dip-simulator")
    sub = parser.add_subparsers(dest="command", required=True)

    batch = sub.add_parser("batch", help="Generate campaigns and donors as CSV files")
    batch.add_argument("--seed", type=int, default=42)
    batch.add_argument("--out", default="output")

    args = parser.parse_args(argv)

    if args.command == "batch":
        cfg = SimConfig(seed=args.seed)
        rng = random.Random(cfg.seed)
        ids = IdFactory(rng)

        campaigns = generate_campaigns(cfg, rng, ids)
        donors = generate_donors(cfg, rng, ids)

        out = Path(args.out)
        write_csv(out / "campaigns.csv", campaigns)
        write_csv(out / "donors.csv", donors)
        print(f"Wrote {len(campaigns)} campaigns and {len(donors)} donors to {out}")


if __name__ == "__main__":
    main()
