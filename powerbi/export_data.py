"""Prepare typed CSV tables for a Power BI import model; Python standard library only."""

import argparse
import csv
import json
import hashlib
import os
import uuid
import sqlite3
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sales import analyze, write_csv, write_json


def export(input_folder, output_folder):
    output_folder = Path(output_folder).resolve()
    temp_parent = ROOT / "tmp/powerbi"
    temp_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=temp_parent) as temporary:
        stage = Path(temporary)
        # Notes are deliberately absent from this public analytics dataset.
        report = analyze(input_folder, stage / "no-review-notes.csv", stage)
        connection = sqlite3.connect(stage / "sales.sqlite")
        connection.row_factory = sqlite3.Row
        try:
            sales = [dict(row) for row in connection.execute("""
                SELECT row_id LineID,order_id OrderID,order_date OrderDate,
                ship_date ShipDate,category Category,region Region,product_id ProductID,
                sales_units SalesUnits,source_file SourceFile,source_row SourceRow
                FROM lines ORDER BY order_date,row_id
            """)]
        finally:
            connection.close()
        metrics = report["metrics"]
        periods = report["reports"]["monthly"]
        start = date.fromisoformat(periods[0]["month"] + "-01")
        last = date.fromisoformat(periods[-1]["month"] + "-01")
        finish = date(
            last.year + (last.month == 12), last.month % 12 + 1, 1
        ) - timedelta(days=1)
        calendar = []
        current = start
        while current <= finish:
            calendar.append(
                {
                    "Date": current.isoformat(),
                    "Year": current.year,
                    "MonthNumber": current.month,
                    "MonthLabel": current.strftime("%b"),
                    "YearMonth": current.strftime("%Y-%m"),
                }
            )
            current += timedelta(days=1)
        coverage = [
            {"Month": row["month"] + "-01", "Coverage": row["coverage"]}
            for row in periods
        ]
        quality = [
            {"Metric": label, "Value": metrics[key]}
            for label, key in [
                ("Input rows", "input_rows"),
                ("Accepted rows", "lines"),
                ("Skipped identical repeats", "repeated_rows"),
                ("Missing monthly files", "missing_months"),
                ("Input files", "input_files"),
            ]
        ]
        tables = {
            "Sales": sales,
            "Dates": calendar,
            "DeliveryCoverage": coverage,
            "Quality": quality,
        }
        headers = {
            "Sales": [
                "LineID",
                "OrderID",
                "OrderDate",
                "ShipDate",
                "Category",
                "Region",
                "ProductID",
                "SalesUnits",
                "SourceFile",
                "SourceRow",
            ],
            "Dates": ["Date", "Year", "MonthNumber", "MonthLabel", "YearMonth"],
            "DeliveryCoverage": ["Month", "Coverage"],
            "Quality": ["Metric", "Value"],
        }
        assert sum(row["SalesUnits"] for row in sales) == metrics["sales_units"]
        assert len({row["OrderID"] for row in sales}) == metrics["orders"]
        assert len(sales) == metrics["lines"]
        assert all(row["OrderDate"] in {d["Date"] for d in calendar} for row in sales)
        output_folder.mkdir(parents=True, exist_ok=True)
        snapshot_stage = output_folder / ("staging_" + uuid.uuid4().hex)
        snapshot_stage.mkdir()
        for name, rows in tables.items():
            write_csv(snapshot_stage / (name + ".csv"), rows, headers[name])
        write_json(
            snapshot_stage / "export-verification.json",
            {
                "metrics": metrics,
                "checks": {
                    "sales_units_reconcile": True,
                    "distinct_orders_reconcile": True,
                    "accepted_rows_reconcile": True,
                    "calendar_covers_sales": True,
                },
                "power_bi_desktop_tested": False,
                "power_query_tested": False,
                "dax_tested": False,
                "files": report["files"],
                "note": "Export-only validation; native Power BI model and visual QA remain required.",
            },
        )
        fingerprint = hashlib.sha256(
            b"".join((snapshot_stage / (name + ".csv")).read_bytes() for name in tables)
        ).hexdigest()[:16]
        snapshot = output_folder / "snapshots" / fingerprint
        snapshot.parent.mkdir(exist_ok=True)
        if snapshot.exists():
            import shutil

            snapshot_stage.resolve().relative_to(output_folder)
            shutil.rmtree(snapshot_stage)
        else:
            snapshot_stage.rename(snapshot)
        pointer = output_folder / ("latest_" + uuid.uuid4().hex + ".tmp")
        write_json(
            pointer,
            {"contract_version": 1, "snapshot": fingerprint, "metrics": metrics},
        )
        os.replace(pointer, output_folder / "latest.json")
    print(
        json.dumps(
            {
                "output": str(output_folder),
                "tables": {k: len(v) for k, v in tables.items()},
                "native_power_bi_verified": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/incoming")
    parser.add_argument(
        "--output", type=Path, default=Path(__file__).resolve().parent / "sample-data"
    )
    arguments = parser.parse_args()
    export(arguments.input, arguments.output)
