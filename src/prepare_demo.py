"""Replay a frozen Kaggle snapshot as historical monthly deliveries, without fabricating sales."""

import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from sales import ROOT, FIELDS, digest, write_csv, write_json


def prepare(source, target):
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    groups = defaultdict(list)
    with Path(source).open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            month = datetime.strptime(row["Order Date"], "%d/%m/%Y").strftime("%Y-%m")
            groups[month].append({field: row[field] for field in FIELDS})
    for month, rows in sorted(groups.items()):
        write_csv(target / f"sales_{month}.csv", rows, FIELDS)
    provenance = {
        "dataset": "rohitsahoo/sales-forecasting",
        "source_file": Path(source).name,
        "source_sha256": digest(source),
        "source_rows": sum(map(len, groups.values())),
        "monthly_files": len(groups),
        "transformation": "Selected eight original columns and partitioned by parsed Order Date; original values retained.",
        "sample_data": True,
        "currency": "Unspecified by Kaggle data card; no currency conversion assumed.",
        "license_label": "GPL 2",
        "data_page": "https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting",
    }
    write_json(ROOT / "docs/source-provenance.json", provenance)
    return provenance


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, default=ROOT / "data/raw/train.csv")
    p.add_argument("--target", type=Path, default=ROOT / "data/incoming")
    a = p.parse_args()
    print(prepare(a.source, a.target))
