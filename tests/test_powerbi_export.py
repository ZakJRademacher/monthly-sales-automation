"""Exercise refresh publication failures and data lineage for the Power BI handoff."""

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from powerbi.export_data import export
from sales import FIELDS, write_csv


class PowerBIExportTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / "tmp/tests"
        parent.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=parent)
        self.root = Path(self.tmp.name)
        self.inputs = self.root / "incoming"
        self.inputs.mkdir()
        self.output = self.root / "export"
        self.row = dict(
            zip(
                FIELDS,
                [
                    "1",
                    "O1",
                    "05/01/2018",
                    "07/01/2018",
                    "Technology",
                    "West",
                    "P1",
                    "10.1234",
                ],
            )
        )
        self.write()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self):
        write_csv(self.inputs / "sales_2018-01.csv", [self.row], FIELDS)

    def pointer(self):
        return (self.output / "latest.json").read_bytes()

    def test_exact_units_and_source_lineage(self):
        export(self.inputs, self.output)
        pointer = json.loads(self.pointer())
        snapshot = self.output / "snapshots" / pointer["snapshot"]
        with (snapshot / "Sales.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["SalesUnits"], "101234")
        self.assertEqual(rows[0]["SourceFile"], "sales_2018-01.csv")
        self.assertEqual(rows[0]["SourceRow"], "2")
        self.assertEqual(len(list(snapshot.glob("*.csv"))), 4)

    def test_replay_reuses_identical_snapshot(self):
        export(self.inputs, self.output)
        before = self.pointer()
        export(self.inputs, self.output)
        self.assertEqual(before, self.pointer())
        self.assertEqual(len(list((self.output / "snapshots").iterdir())), 1)

    def test_changed_or_missing_snapshot_file_is_rejected(self):
        for name in ["Sales.csv", "Dates.csv", "DeliveryCoverage.csv", "Quality.csv", "export-verification.json"]:
            for missing in [False, True]:
                with self.subTest(file=name, missing=missing):
                    export(self.inputs, self.output)
                    before = self.pointer()
                    snapshot = self.output / "snapshots" / json.loads(before)["snapshot"]
                    path = snapshot / name
                    original = path.read_bytes()
                    if missing:
                        path.unlink()
                    else:
                        path.write_bytes(b"damaged contents")
                    try:
                        with self.assertRaisesRegex(ValueError, "Existing snapshot"):
                            export(self.inputs, self.output)
                        self.assertEqual(before, self.pointer())
                        self.assertFalse(list(self.output.glob("staging_*")))
                    finally:
                        path.write_bytes(original)

    def test_invalid_input_preserves_last_good(self):
        export(self.inputs, self.output)
        before = self.pointer()
        self.row["Sales"] = "invalid"
        self.write()
        with self.assertRaises(ValueError):
            export(self.inputs, self.output)
        self.assertEqual(before, self.pointer())

    def test_failed_pointer_replace_keeps_previous_snapshot(self):
        export(self.inputs, self.output)
        before = self.pointer()
        self.row["Sales"] = "20.0000"
        self.write()
        with patch(
            "powerbi.export_data.os.replace",
            side_effect=OSError("simulated disk error"),
        ):
            with self.assertRaises(OSError):
                export(self.inputs, self.output)
        self.assertEqual(before, self.pointer())
        original = json.loads(before)["snapshot"]
        self.assertTrue((self.output / "snapshots" / original / "Sales.csv").exists())
