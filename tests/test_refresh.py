"""Synthetic edge cases for the real-data workflow; no invented sales enter published results."""

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from sales import FIELDS, NOTE_FIELDS, analyze, parse_row, read_notes, write_csv
from refresh import refresh
from import_notes import merge


class RefreshTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / "tmp/tests"
        parent.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=parent)
        self.root = Path(self.tmp.name)
        self.inputs = self.root / "incoming"
        self.inputs.mkdir()
        self.notes = self.root / "notes.csv"
        write_csv(self.notes, [], NOTE_FIELDS)

    def tearDown(self):
        self.tmp.cleanup()

    def row(self, key="1", month="2018-01", sales="10.1234", order=None):
        y, m = month.split("-")
        return dict(
            zip(
                FIELDS,
                [
                    key,
                    order or "Order-" + key,
                    f"05/{m}/{y}",
                    f"07/{m}/{y}",
                    "Technology",
                    "West",
                    "P1",
                    sales,
                ],
            )
        )

    def file(self, month="2018-01", rows=None):
        write_csv(
            self.inputs / f"sales_{month}.csv",
            rows if rows is not None else [self.row(month=month)],
            FIELDS,
        )

    def build(self):
        return analyze(
            self.inputs,
            self.notes,
            self.root / ("stage" + str(len(list(self.root.glob("stage*"))))),
        )

    @staticmethod
    def fake_writer(stage, render):
        a = json.loads((stage / "analysis.json").read_text())
        # Test double for publication protocol only; Excel is tested separately with the real engine.
        (stage / f"monthly-sales_{a['metrics']['last_month']}.xlsx").write_bytes(
            b"Publication protocol test double"
        )

    def test_day_first_date(self):
        self.assertEqual(parse_row(self.row(), "2018-01")[2], "2018-01-05")

    def test_amount_precision_preserved(self):
        self.assertEqual(parse_row(self.row(), "2018-01")[7], 101234)

    def test_zero_sales_valid(self):
        self.file(rows=[self.row(sales="0")])
        self.assertEqual(self.build()["metrics"]["sales_units"], 0)

    def test_invalid_amounts_rejected(self):
        for value in ["NaN", "Infinity", "-1", "1.23456", "junk"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_row(self.row(sales=value), "2018-01")

    def test_invalid_date_rejected(self):
        r = self.row()
        r["Order Date"] = "31/02/2018"
        with self.assertRaises(ValueError):
            parse_row(r, "2018-02")

    def test_wrong_month_rejected(self):
        self.file("2018-02", rows=[self.row()])
        with self.assertRaisesRegex(ValueError, "filename month"):
            self.build()

    def test_ship_before_order_rejected(self):
        r = self.row()
        r["Ship Date"] = "01/01/2018"
        with self.assertRaises(ValueError):
            parse_row(r, "2018-01")

    def test_identical_id_is_not_counted_twice(self):
        self.file(rows=[self.row(), self.row()])
        m = self.build()["metrics"]
        self.assertEqual(
            (m["input_rows"], m["lines"], m["repeated_rows"], m["sales_units"]),
            (2, 1, 1, 101234),
        )

    def test_conflicting_id_blocks_report(self):
        self.file(rows=[self.row(), self.row(sales="99")])
        with self.assertRaisesRegex(ValueError, "conflicting Row ID"):
            self.build()

    def test_order_count_distinct_from_line_count(self):
        self.file(rows=[self.row(order="A"), self.row("2", order="A")])
        m = self.build()["metrics"]
        self.assertEqual((m["lines"], m["orders"]), (2, 1))

    def test_inconsistent_order_dates_rejected(self):
        r = self.row("2", order="A")
        r["Order Date"] = "06/01/2018"
        self.file(rows=[self.row(order="A"), r])
        with self.assertRaisesRegex(ValueError, "inconsistent order dates"):
            self.build()

    def test_missing_month_is_unavailable(self):
        self.file()
        self.file("2018-03", [self.row("2", "2018-03")])
        a = self.build()
        feb = a["reports"]["monthly"][1]
        self.assertEqual(
            (feb["coverage"], feb["sales_units"], a["metrics"]["missing_months"]),
            ("Missing file", None, 1),
        )

    def test_explicit_empty_month_is_zero(self):
        self.file()
        self.file("2018-02", [])
        a = self.build()
        self.assertEqual(
            (a["reports"]["monthly"][1]["sales_units"], a["metrics"]["missing_months"]),
            (0, 0),
        )

    def test_missing_column_rejected(self):
        (self.inputs / "sales_2018-01.csv").write_text("Row ID,Sales\n1,5\n")
        with self.assertRaisesRegex(ValueError, "headers"):
            self.build()

    def test_bad_filename_rejected(self):
        write_csv(self.inputs / "arbitrary.csv", [self.row()], FIELDS)
        with self.assertRaisesRegex(ValueError, "filenames"):
            self.build()

    def test_notes_survive_refresh_and_sort(self):
        write_csv(
            self.notes,
            [
                dict(
                    zip(
                        NOTE_FIELDS,
                        [
                            "2018-01",
                            "Technology",
                            "Reviewer",
                            "In progress",
                            "Keep this note",
                        ],
                    )
                )
            ],
            NOTE_FIELDS,
        )
        before = self.notes.read_bytes()
        self.file()
        a = self.build()
        self.file("2018-02", [self.row("2", "2018-02")])
        b = self.build()
        for report in [a, b]:
            self.assertEqual(
                report["reports"]["category_month"][0]["note"], "Keep this note"
            )
        self.assertEqual(self.notes.read_bytes(), before)

    def test_unmatched_notes_not_discarded(self):
        write_csv(
            self.notes,
            [
                dict(
                    zip(
                        NOTE_FIELDS,
                        [
                            "2017-01",
                            "Technology",
                            "Reviewer",
                            "In progress",
                            "Older period",
                        ],
                    )
                )
            ],
            NOTE_FIELDS,
        )
        self.file()
        self.assertEqual(self.build()["metrics"]["unmatched_notes"], 1)
        self.assertEqual(len(read_notes(self.notes)), 1)

    def test_import_preface_and_untouched_rows(self):
        write_csv(
            self.notes,
            [
                dict(
                    zip(
                        NOTE_FIELDS,
                        ["2018-01", "Technology", "Old owner", "In progress", "Keep"],
                    )
                )
            ],
            NOTE_FIELDS,
        )
        exported = self.root / "review.csv"
        exported.write_text(
            "Category review\nMonth key,Category,Owner,Review status,Review note\n2018-01,Technology,,Not started,\n2018-02,Furniture,Sam,Reviewed,Source checked\n",
            encoding="utf-8",
        )
        self.assertEqual(merge(exported, self.notes), 2)
        self.assertEqual(
            read_notes(self.notes)[("2018-01", "Technology")]["note"], "Keep"
        )

    def test_invalid_review_import_is_atomic(self):
        exported = self.root / "review.csv"
        exported.write_text(
            "month,category,owner,status,note\n2018-01,Technology,,Reviewed,\n"
        )
        before = self.notes.read_bytes()
        with self.assertRaises(ValueError):
            merge(exported, self.notes)
        self.assertEqual(before, self.notes.read_bytes())

    def test_failed_refresh_keeps_last_good_report(self):
        self.file()
        runs = self.root / "runs"
        refresh(self.inputs, self.notes, runs, writer=self.fake_writer)
        previous = (runs / "latest.json").read_bytes()
        self.file(rows=[self.row(), self.row(sales="99")])
        with self.assertRaises(ValueError):
            refresh(self.inputs, self.notes, runs, writer=self.fake_writer)
        self.assertEqual(previous, (runs / "latest.json").read_bytes())
        self.assertFalse((runs / ".refresh.lock").exists())
        self.assertEqual(len(list(runs.glob("failed_*.json"))), 1)

    def test_excel_failure_does_not_publish(self):
        self.file()
        runs = self.root / "runs"

        def fail(stage, render):
            raise RuntimeError("Workbook unavailable")

        with self.assertRaises(RuntimeError):
            refresh(self.inputs, self.notes, runs, writer=fail)
        self.assertFalse((runs / "latest.json").exists())

    def test_overlapping_refresh_is_blocked(self):
        runs = self.root / "runs"
        runs.mkdir()
        (runs / ".refresh.lock").write_text("another worker")
        with self.assertRaisesRegex(RuntimeError, "output lock"):
            refresh(self.inputs, self.notes, runs, writer=self.fake_writer)

    def test_repeated_refresh_is_idempotent(self):
        self.file()
        runs = self.root / "runs"
        first = refresh(self.inputs, self.notes, runs, writer=self.fake_writer)
        second = refresh(self.inputs, self.notes, runs, writer=self.fake_writer)
        self.assertEqual(first["metrics"], second["metrics"])
        self.assertNotEqual(first["run_id"], second["run_id"])


if __name__ == "__main__":
    unittest.main()
