"""Standard-library ingestion and SQL reporting for monthly sales CSV deliveries."""

import calendar
import csv
import hashlib
import json
import re
import sqlite3
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = [
    "Row ID",
    "Order ID",
    "Order Date",
    "Ship Date",
    "Category",
    "Region",
    "Product ID",
    "Sales",
]
NOTE_FIELDS = ["month", "category", "owner", "status", "note"]
STATUSES = {"Not started", "In progress", "Reviewed"}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_csv(path, rows, headers):
    with Path(path).open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def month_range(first, last):
    current = first
    while current <= last:
        yield current
        year, month = map(int, current.split("-"))
        current = f"{year+(month==12):04d}-{month%12+1:02d}"


def parse_row(row, month):
    values = {name: (row.get(name) or "").strip() for name in FIELDS}
    if not values["Row ID"].isdecimal():
        raise ValueError("Row ID must be nonempty decimal text")
    if any(
        not values[field] for field in ["Order ID", "Category", "Region", "Product ID"]
    ):
        raise ValueError("Required order, category, region or product value is blank")
    try:
        received = datetime.strptime(values["Order Date"], "%d/%m/%Y").date()
        shipped = datetime.strptime(values["Ship Date"], "%d/%m/%Y").date()
    except ValueError as exc:
        raise ValueError("Dates must be valid day/month/year values") from exc
    if received.isoformat()[:7] != month:
        raise ValueError("Order date does not match the filename month")
    if shipped < received:
        raise ValueError("Ship date precedes order date")
    try:
        amount = Decimal(values["Sales"])
        if (
            not amount.is_finite()
            or amount < 0
            or amount * 10000 != (amount * 10000).to_integral_value()
        ):
            raise ValueError(
                "Sales must be nonnegative, finite and have at most four decimal places"
            )
        if amount > Decimal("1000000000"):
            raise ValueError("Sales exceeds supported per-line range")
    except InvalidOperation as exc:
        raise ValueError("Sales must be a decimal number") from exc
    # Source monetary units, exactly 1/10,000. No currency or profit assumption.
    return (
        values["Row ID"],
        values["Order ID"],
        received.isoformat(),
        shipped.isoformat(),
        values["Category"],
        values["Region"],
        values["Product ID"],
        int(amount * 10000),
    )


def read_notes(path):
    result = {}
    if not Path(path).exists():
        return result
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not set(NOTE_FIELDS) <= set(reader.fieldnames or []):
            raise ValueError("Missing review-note headers")
        for row in reader:
            month, category = (row["month"] or "").strip(), (
                row["category"] or ""
            ).strip()
            try:
                datetime.strptime(month + "-01", "%Y-%m-%d")
            except ValueError as exc:
                raise ValueError("Invalid note month") from exc
            if not re.fullmatch(r"\d{4}-\d{2}", month) or not category:
                raise ValueError("Invalid note key")
            key = (month, category)
            if key in result:
                raise ValueError("Duplicate note key: " + str(key))
            owner, status, note = (
                (row.get(x) or "").strip() for x in ["owner", "status", "note"]
            )
            status = status or "Not started"
            if status not in STATUSES or (
                status == "Reviewed" and (not owner or not note)
            ):
                raise ValueError(
                    "Reviewed notes require owner and note; use a supported status"
                )
            result[key] = {
                "month": month,
                "category": category,
                "owner": owner,
                "status": status,
                "note": note,
            }
    return result


def analyze(input_dir, notes_path, output_dir):
    """Build an isolated report snapshot. Reject invalid deliveries as a unit."""
    input_dir, output_dir = Path(input_dir), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = sorted(input_dir.glob("*.csv"))
    if not paths:
        raise ValueError("No monthly CSV files found")
    notes = read_notes(notes_path)
    files = []
    seen = {}
    order_dates = {}
    accepted = []
    repeats = []
    for path in paths:
        match = re.fullmatch(r"sales_(\d{4}-\d{2})\.csv", path.name)
        if not match:
            raise ValueError("Use monthly filenames sales_YYYY-MM.csv: " + path.name)
        month = match[1]
        try:
            datetime.strptime(month + "-01", "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("Invalid filename month: " + path.name) from exc
        file_count = 0
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if len(reader.fieldnames or []) != len(
                set(reader.fieldnames or [])
            ) or not set(FIELDS) <= set(reader.fieldnames or []):
                raise ValueError("Missing or repeated column headers: " + path.name)
            for number, row in enumerate(reader, start=2):
                if None in row:
                    raise ValueError(f"{path.name}:{number}: extra CSV fields")
                try:
                    record = parse_row(row, month)
                except ValueError as exc:
                    raise ValueError(f"{path.name}:{number}: {exc}") from exc
                file_count += 1
                if record[0] in seen:
                    if seen[record[0]] != record:
                        raise ValueError(
                            f"{path.name}:{number}: conflicting Row ID {record[0]}"
                        )
                    repeats.append(
                        {
                            "source_file": path.name,
                            "source_row": number,
                            "row_id": record[0],
                        }
                    )
                    continue
                if record[1] in order_dates and order_dates[record[1]] != record[2]:
                    raise ValueError(
                        "An Order ID has inconsistent order dates: " + record[1]
                    )
                order_dates[record[1]] = record[2]
                seen[record[0]] = record
                accepted.append((*record, path.name, number))
        files.append(
            {
                "file": path.name,
                "month": month,
                "source_rows": file_count,
                "sha256": digest(path),
            }
        )
    if not accepted:
        raise ValueError("No sales lines in the supplied deliveries")
    if sum(row[7] for row in accepted) >= 2**53:
        raise ValueError(
            "Total exceeds exact-integer spreadsheet precision at the 1/10,000 scale"
        )
    db = sqlite3.connect(output_dir / "sales.sqlite")
    db.row_factory = sqlite3.Row
    db.executescript(
        """CREATE TABLE lines(row_id TEXT PRIMARY KEY,order_id TEXT,order_date TEXT,
      ship_date TEXT,category TEXT,region TEXT,product_id TEXT,sales_units INTEGER,
      source_file TEXT,source_row INTEGER);
      CREATE TABLE periods(month TEXT PRIMARY KEY,coverage TEXT);
      CREATE TABLE notes(month TEXT,category TEXT,owner TEXT,status TEXT,note TEXT,PRIMARY KEY(month,category));"""
    )
    db.executemany("INSERT INTO lines VALUES (?,?,?,?,?,?,?,?,?,?)", accepted)
    present = {f["month"] for f in files}
    periods = list(month_range(min(present), max(present)))
    db.executemany(
        "INSERT INTO periods VALUES (?,?)",
        [(p, "Imported" if p in present else "Missing file") for p in periods],
    )
    db.executemany(
        "INSERT INTO notes VALUES (?,?,?,?,?)",
        [[n[k] for k in NOTE_FIELDS] for n in notes.values()],
    )
    reports = {}
    for name in ["monthly", "category_month", "regions", "unmatched_notes"]:
        cursor = db.execute((ROOT / "sql" / f"{name}.sql").read_text())
        report = [dict(row) for row in cursor]
        write_csv(
            output_dir / f"{name}.csv", report, [c[0] for c in cursor.description]
        )
        reports[name] = report
    write_csv(
        output_dir / "repeated_rows.csv",
        repeats,
        ["source_file", "source_row", "row_id"],
    )
    m = dict(
        db.execute(
            "SELECT COUNT(*) lines,COUNT(DISTINCT order_id) orders,SUM(sales_units) sales_units,MIN(order_date) first_date,MAX(order_date) last_date FROM lines"
        ).fetchone()
    )
    m.update(
        input_files=len(files),
        input_rows=sum(f["source_rows"] for f in files),
        repeated_rows=len(repeats),
        months=len(periods),
        missing_months=len(periods) - len(present),
        last_month=max(present),
        saved_note_keys=len(notes),
        unmatched_notes=len(reports["unmatched_notes"]),
    )
    checks = {
        "source_row_partition": m["input_rows"] == m["lines"] + m["repeated_rows"],
        "monthly_sales_reconcile": sum(
            x["sales_units"] or 0 for x in reports["monthly"]
        )
        == m["sales_units"],
        "monthly_order_count_reconcile": sum(
            x["orders"] or 0 for x in reports["monthly"]
        )
        == m["orders"],
        "category_sales_reconcile": sum(
            x["sales_units"] for x in reports["category_month"]
        )
        == m["sales_units"],
        "region_sales_reconcile": sum(x["sales_units"] for x in reports["regions"])
        == m["sales_units"],
        "sqlite_integrity": db.execute("PRAGMA integrity_check").fetchone()[0] == "ok",
    }
    from business_review import build_review, render_html

    business_review = build_review(db, m)
    render_html(business_review, output_dir / "sales-review.html")
    action_headers = [
        "priority",
        "scope",
        "segment",
        "current_sales",
        "prior_sales",
        "sales_change",
        "change_pct",
        "reason",
        "product_ids_to_check",
        "next_step",
    ]
    write_csv(
        output_dir / "review_actions.csv", business_review["actions"], action_headers
    )
    for scope, rows in business_review["drivers"].items():
        write_csv(
            output_dir / f"review_{scope}.csv",
            rows,
            [
                "member",
                "current_sales_units",
                "prior_sales_units",
                "current_orders",
                "prior_orders",
                "change_units",
                "change_pct",
            ],
        )
    write_json(output_dir / "business-review.json", business_review)
    db.commit()
    db.close()
    result = {
        "metrics": m,
        "files": files,
        "reports": reports,
        "checks": checks,
        "units": "Sales are source monetary units. Currency is not specified by this mirror; no conversion is made.",
        "date_format": "day/month/year",
        "amount_scale": 10000,
        "business_review": business_review,
    }
    if not all(checks.values()):
        raise AssertionError(checks)
    write_json(output_dir / "analysis.json", result)
    return result
