"""Merge annotations exported from Excel's Category review sheet by month and category."""

import argparse
import csv
import os
import uuid
from pathlib import Path
from sales import ROOT, NOTE_FIELDS, STATUSES, read_notes, write_csv

ALIASES = {
    "Month key": "month",
    "Category": "category",
    "Owner": "owner",
    "Review status": "status",
    "Review note": "note",
}


def merge(source, destination):
    notes = read_notes(destination)
    seen = set()
    with Path(source).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        for row in reader:
            headers = [ALIASES.get(x.strip(), x.strip()) for x in row]
            if set(NOTE_FIELDS) <= set(headers):
                break
        else:
            raise ValueError(
                "Expected Month key, Category, Owner, Review status, Review note columns"
            )
        for row in reader:
            record = dict(zip(headers, row))
            if not any(str(v).strip() for v in record.values()):
                continue
            value = {k: record.get(k, "").strip() for k in NOTE_FIELDS}
            key = (value["month"], value["category"])
            if key in seen:
                raise ValueError("Duplicate imported note key")
            seen.add(key)
            value["status"] = value["status"] or "Not started"
            if (
                not value["owner"]
                and not value["note"]
                and value["status"] == "Not started"
            ):
                continue
            notes[key] = value
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_name(destination.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        write_csv(temp, [notes[key] for key in sorted(notes)], NOTE_FIELDS)
        read_notes(
            temp
        )  # Validate the entire merge before replacing the persistent input.
        os.replace(temp, destination)
    finally:
        if temp.exists():
            temp.unlink()
    return len(notes)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    p.add_argument("--notes", type=Path, default=ROOT / "data/notes/review_notes.csv")
    a = p.parse_args()
    print(f"{merge(a.source,a.notes)} saved review-note keys")
