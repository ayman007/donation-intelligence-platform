import csv
from dataclasses import asdict, fields
from datetime import date, datetime
from pathlib import Path


def _format(value):
    if isinstance(value, datetime):  # check first: datetime is a subclass of date
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value


def write_csv(path, rows) -> None:
    if not rows:
        raise ValueError("no rows to write")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    names = [f.name for f in fields(rows[0])]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=names)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _format(v) for k, v in asdict(row).items()})
