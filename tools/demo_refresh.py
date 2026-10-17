"""Exercise actual Excel refreshes: 47 files, add the 48th, rerun, then reject a conflicting row."""

import csv
import json
import shutil
import sys
import tempfile
from decimal import Decimal
from pathlib import Path
from openpyxl import load_workbook
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from refresh import refresh
from sales import FIELDS, NOTE_FIELDS, write_csv, write_json

parent = ROOT / "tmp/demonstration"
parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(dir=parent) as directory:
    work = Path(directory)
    incoming = work / "incoming"
    incoming.mkdir()
    runs = work / "runs"
    sources = sorted((ROOT / "data/incoming").glob("sales_*.csv"))
    for source in sources[:-1]:
        shutil.copy2(source, incoming / source.name)
    key = (sources[-2].stem[-7:], "Office Supplies")
    notes = work / "review_notes.csv"
    note = "Demonstration note only; no client review performed."
    write_csv(
        notes,
        [dict(zip(NOTE_FIELDS, [*key, "Demo reviewer", "In progress", note]))],
        NOTE_FIELDS,
    )
    first = refresh(incoming, notes, runs, generate_pdf=True)
    shutil.copy2(sources[-1], incoming / sources[-1].name)
    second = refresh(incoming, notes, runs, generate_pdf=True)
    third = refresh(incoming, notes, runs, generate_pdf=True)

    def workbook(run):
        return load_workbook(Path(run["directory"]) / run["workbook"], data_only=True)

    b1, b2 = workbook(first), workbook(second)
    business_before = json.loads(
        (Path(first["directory"]) / "business-review.json").read_text()
    )
    business_after = json.loads(
        (Path(second["directory"]) / "business-review.json").read_text()
    )
    matched = [
        row
        for row in b2["Category review"].iter_rows(min_row=6, values_only=True)
        if row[:2] == key
    ]
    pointer = (runs / "latest.json").read_bytes()
    with (incoming / sources[-1].name).open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    conflict = dict(rows[0])
    conflict["Sales"] = str(Decimal(conflict["Sales"]) + 1)
    rows.append(conflict)
    write_csv(incoming / sources[-1].name, rows, FIELDS)
    blocked = False
    try:
        refresh(incoming, notes, runs)
    except ValueError as exc:
        blocked = "conflicting Row ID" in str(exc)
    checks = {
        "pdf_rebuilt_for_new_month": all(
            run["metrics"]["last_month"]
            in PdfReader(Path(run["directory"]) / "case-study.pdf")
            .pages[0]
            .extract_text()
            for run in [first, second, third]
        ),
        "pdf_has_two_pages_each_run": all(
            len(PdfReader(Path(run["directory"]) / "case-study.pdf").pages) == 2
            for run in [first, second, third]
        ),
        "real_engine_used_for_three_refreshes": all(
            (Path(run["directory"]) / "workbook-verification.json").exists()
            for run in [first, second, third]
        ),
        "next_month_added": first["metrics"]["input_files"] == 47
        and second["metrics"]["input_files"] == 48,
        "new_lines_added": second["metrics"]["lines"] - first["metrics"]["lines"]
        == 459,
        "month_label_advanced": b1["Monthly report"]["B6"].value.month == 11
        and b2["Monthly report"]["B6"].value.month == 12,
        "latest_month_value_changed": b1["Monthly report"]["B7"].value
        != b2["Monthly report"]["B7"].value,
        "business_review_advanced_with_delivery": business_before["summary"]["month"]
        == "2018-11"
        and business_after["summary"]["month"] == "2018-12",
        "new_review_returns_actual_sales_finding": abs(
            business_after["summary"]["sales_change_pct"] - (83030.3888 / 95007.353 - 1)
        )
        < 1e-10
        and len(business_after["actions"]) == 5,
        "useful_html_and_csv_generated": all(
            (Path(run["directory"]) / filename).is_file()
            for run in [first, second, third]
            for filename in ["sales-review.html", "review_actions.csv"]
        ),
        "saved_note_preserved": len(matched) == 1
        and matched[0][3:6] == ("Demo reviewer", "In progress", note),
        "identical_rerun_did_not_double_count": second["metrics"] == third["metrics"],
        "conflicting_delivery_rejected": blocked,
        "failed_refresh_kept_last_good_pointer": pointer
        == (runs / "latest.json").read_bytes(),
        "last_good_workbook_retained": (
            Path(third["directory"]) / third["workbook"]
        ).exists(),
    }
    result = {
        "scenario": "Replay historical Kaggle monthly partitions; no fabricated sales enter delivered workbook.",
        "test_annotation": "A clearly labeled temporary demonstration note; delivered workbook has no invented completed reviews.",
        "before": first["metrics"],
        "after": second["metrics"],
        "checks": checks,
        "all_passed": all(checks.values()),
        "nativeExcelRecalculationTested": False,
    }
    write_json(ROOT / "docs/refresh-demonstration.json", result)
    print(json.dumps(result, indent=2))
    if not result["all_passed"]:
        raise SystemExit(1)
