"""Create the public project cover, case study and written handoff from verified refresh outputs."""

import json
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    Preformatted,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"
DOC = ROOT / "docs"
a = json.loads((ROOT / "evidence/analysis.json").read_text())
m = a["metrics"]
months = a["reports"]["monthly"]
demo = json.loads((DOC / "refresh-demonstration.json").read_text())
provenance = json.loads((DOC / "source-provenance.json").read_text())
navy = "#213047"
blue = "#3667AF"
muted = "#68798D"
amber = "#C88618"
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "text.color": navy,
        "axes.labelcolor": muted,
        "xtick.color": muted,
        "ytick.color": muted,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
    }
)
last = months[-12:]


def sales_chart(ax):
    values = [x["sales_units"] / 10000 for x in last]
    ax.plot(range(12), values, color=blue, linewidth=2.8, marker="o", markersize=4)
    ax.set_xticks(range(12), [x["month"][-2:] + "/18" for x in last])
    ax.set_ylabel("Sales · source monetary units")
    ax.set_ylim(0, max(values) * 1.18)
    ax.grid(axis="y", color="#DFE6EE")
    ax.set_axisbelow(True)


fig = plt.figure(figsize=(12, 9), facecolor="#F4F6F9")
fig.text(0.09, 0.91, "MONTHLY REPORT AUTOMATION", fontsize=23, weight="bold")
fig.text(
    0.09,
    0.86,
    "CSV deliveries → validation → refreshed Excel → dated report",
    fontsize=13,
    color=muted,
)
for x, value, label in [
    (0.09, "48", "MONTHLY FILES"),
    (0.39, "9,800", "SOURCE SALES LINES"),
    (0.70, "23", "AUTOMATED TESTS"),
]:
    fig.text(x, 0.73, value, fontsize=34, weight="bold")
    fig.text(x, 0.685, label, fontsize=10, weight="bold", color=muted)
ax = fig.add_axes([0.14, 0.33, 0.74, 0.26])
sales_chart(ax)
ax.set_title(
    "The report advances when the next monthly file arrives",
    loc="left",
    fontsize=12,
    pad=15,
    fontweight="bold",
)
fig.text(
    0.09,
    0.215,
    "Saved review notes survive the refresh.",
    fontsize=15,
    weight="bold",
    color=blue,
)
fig.text(
    0.09,
    0.165,
    "A failed import keeps the last successful report available.",
    fontsize=13,
    color=navy,
)
fig.text(
    0.09,
    0.09,
    "Python · SQLite · Excel | Kaggle Superstore sample | Source data: 2015–2018",
    fontsize=10,
    color=muted,
)
fig.savefig(OUT / "portfolio-cover.png", dpi=150, facecolor=fig.get_facecolor())
plt.close(fig)
fig, ax = plt.subplots(figsize=(10, 3))
sales_chart(ax)
fig.tight_layout()
fig.savefig(OUT / "monthly-sales-trend.png", dpi=150, facecolor="white")
plt.close(fig)

rl_config.useA85 = False
styles = getSampleStyleSheet()
styles["BodyText"].fontSize = 10
styles["BodyText"].leading = 14
styles["BodyText"].spaceAfter = 8
styles.add(
    ParagraphStyle(
        name="ProjectTitle",
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=colors.HexColor(navy),
        spaceAfter=12,
    )
)
styles.add(
    ParagraphStyle(
        name="Deck",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor(muted),
        spaceAfter=12,
    )
)
styles["Heading2"].fontSize = 13
styles["Heading2"].leading = 17
styles["Heading2"].spaceBefore = 12
styles["Heading2"].textColor = colors.HexColor(navy)
p = lambda text, style="BodyText": Paragraph(text, styles[style])
rows = [
    ["REFRESH STEP", "FILES", "LINES", "OBSERVED SALES"],
    ["Before December delivery", "47", "9,341", "2,178,506.3939"],
    ["After December delivery", "48", "9,800", "2,261,536.7827"],
    ["Repeat the same refresh", "48", "9,800", "2,261,536.7827"],
]
t = Table(rows, colWidths=[2.6 * inch, 0.6 * inch, 0.7 * inch, 1.9 * inch])
t.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(navy)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [colors.HexColor("#F1F4F8"), colors.white],
            ),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ]
    )
)
story = [
    p("Automated monthly sales reporting", "ProjectTitle"),
    p(
        "Portfolio case study | Python, SQLite and Excel | Kaggle Superstore sample",
        "Deck",
    ),
    p("The recurring task", "Heading2"),
    p(
        "A business receives a new sales CSV every month. It needs a consistent workbook, traceable totals and saved review notes, without rebuilding formulas or overwriting the last usable report when a file is malformed."
    ),
    p("The delivered workflow", "Heading2"),
    p(
        "Place files named sales_YYYY-MM.csv into the input folder and run <b>python refresh.py</b>. The program validates IDs, dates and amounts, builds SQL aggregates, generates the Excel workbook and writes a versioned run log. It updates latest.json only after the workbook has been generated successfully."
    ),
    p("Demonstrated with actual workbook refreshes", "Heading2"),
    t,
    Spacer(1, 10),
    p(
        "The December delivery adds 459 lines and 83,030.3888 source monetary units. A temporary, clearly labeled review note remains attached to its November/category key. Repeating the same input leaves totals unchanged. A conflicting Row ID then blocks publication while the previous pointer and workbook remain available."
    ),
    Image(str(OUT / "monthly-sales-trend.png"), width=6.8 * inch, height=2.04 * inch),
    p(
        "This replays 48 historical partitions from one downloaded sample dataset. It does not claim that Kaggle publishes a new monthly file or that the sample represents a current retailer.",
        "Deck",
    ),
    PageBreak(),
    p("Controls, handoff &amp; limitations", "ProjectTitle"),
    p(
        "A practical example for recurring spreadsheet and data-cleaning contracts",
        "Deck",
    ),
    p("What the workbook contains", "Heading2"),
    p(
        "<b>Monthly report:</b> the latest period, sales, distinct orders, average order amount, year-over-year comparison and a native trend chart. <b>Monthly detail:</b> all observed periods, imported counts, prior-period references and live ratio formulas. <b>Category review:</b> editable owner, status and note cells linked to stable month/category keys."
    ),
    p("Notes and refresh behavior", "Heading2"),
    p(
        "Export Category review as CSV UTF-8 and run <b>python src/import_notes.py exported-review.csv</b>. The importer merges annotations, keeps older keys and ignores untouched template rows. Reviewed requires both owner and note. Refreshing reads the separate notes input; it does not overwrite it. Keys absent from the current input appear in unmatched_notes.csv."
    ),
    p("Validation and publication", "Heading2"),
    p(
        "Identical repeated Row IDs are skipped; conflicting IDs, missing headers, invalid dates, dates in the wrong filename month, inconsistent order dates and unsupported amounts stop the run. Every accepted row retains its source filename and row number. A missing month is unavailable; an explicit header-only monthly file is known zero. Six controls reconcile source rows and SQL totals. Each successful version contains its input hashes, metrics and workbook checks."
    ),
    p("Evidence", "Heading2"),
    p(
        "Twenty-three automated tests cover the ingestion, note-import and publication rules. Ten real-engine replay checks cover a new month, note retention, a repeat run and a rejected conflict. Independent original-source and XLSX checks confirm the sales totals, typed dates, year-over-year formulas, chart bindings, dropdown and empty delivered notes."
    ),
    p("Source and operating limits", "Heading2"),
    p(
        "Downloaded Kaggle dataset: rohitsahoo/sales-forecasting. The data card labels the dataset GPL 2. The project records the exact source SHA-256 and supplies selected original columns as reproducible monthly inputs. The source is a Superstore sample covering Jan 3, 2015–Dec 30, 2018. Currency is unspecified by the mirror, so the report preserves source monetary units and four-decimal precision. Displayed amounts use two decimals."
    ),
    p("Runtime and review", "Heading2"),
    p(
        "Core ingestion, SQL reporting and tests use standard-library Python. Excel generation requires Node.js and the compatible artifact-tool authoring runtime documented in SETUP.md. The delivered workbook is ready to inspect. Formula recalculation was tested in that engine; native desktop Excel was not available. Worksheet edits require CSV note import before refresh; there is no background watcher or automatic workbook write-back."
    ),
    p(
        '<link href="https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting" color="#3667AF">Kaggle dataset and license label</link> | Complete source, test evidence and refresh guide accompany this briefing.'
    ),
]


def footer(canvas, doc):
    canvas.setFillColor(colors.HexColor(muted))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(
        42, 27, "Zak Rademacher | Monthly sales automation | Portfolio demonstration"
    )
    canvas.drawRightString(570, 27, str(doc.page))


SimpleDocTemplate(
    str(OUT / "case-study.pdf"),
    pagesize=(612, 792),
    leftMargin=42,
    rightMargin=42,
    topMargin=35,
    bottomMargin=42,
    title="Automated monthly sales reporting",
    author="Zak Rademacher",
).build(story, onFirstPage=footer, onLaterPages=footer)


def write(name, text):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


write(
    "README.md",
    f"""# Monthly Sales Report Automation

**Drop monthly CSVs into a folder. Run one command. Receive a refreshed, dated Excel report.**

A working Python/SQL/Excel portfolio project built from a downloaded Kaggle Superstore sample: **9,800 sales lines, 4,922 distinct orders and 48 historical monthly files**. It demonstrates recurring reporting, saved reviewer notes and failure-safe publication.

![Workflow overview](deliverables/portfolio-cover.png)

## Inspect the deliverables

- [Ready-to-open workbook](deliverables/monthly-sales_2018-12.xlsx)
- [Two-page case study](deliverables/case-study.pdf)
- [Actual refresh replay evidence](docs/refresh-demonstration.json)
- [Independent verification](docs/independent-verification.json)
- [Excel preview](deliverables/excel-monthly-report.png)
- [Refresh guide](docs/REFRESH_GUIDE.md), [setup](docs/SETUP.md), [method](docs/METHOD.md), [source and license](docs/SOURCES.md)

## Run the example

The 48 selected-column CSV inputs are included, so a fresh download is not required. No customer names or addresses are bundled. With Python 3.10+, Node.js and the documented compatible spreadsheet runtime:

```sh
python refresh.py
```

The program creates a unique folder in `runs/` containing `monthly-sales_YYYY-MM.xlsx`, a SQLite database, SQL extracts, input hashes, processing log and formula-verification evidence. `runs/latest.json` points to the last fully generated workbook. Older successful runs remain available. See [SETUP.md](docs/SETUP.md) for the actual authoring dependency and environment variables; this is a local workflow, not a hosted service.

## What is automated

1. Validate required columns, stable Row IDs, day/month/year dates, filename months and supported amounts.
2. Skip identical repeat IDs; reject conflicts rather than silently choosing a record.
3. Rebuild SQLite and SQL aggregates from the current delivery-folder snapshot. Repeated runs do not accumulate prior totals.
4. Build a three-sheet workbook with live formulas, a native chart, typed period dates and a review-status dropdown.
5. Rejoin saved review notes by **month + category**, regardless of row position.
6. Publish a new version only after workbook generation succeeds. A rejected import keeps the previous successful pointer and workbook.

## Proof that a new month works

| Replay step | Monthly files | Sales lines | Observed sales, source units |
|---|---:|---:|---:|
| Through November 2018 | 47 | 9,341 | 2,178,506.3939 |
| Add December 2018 | 48 | 9,800 | 2,261,536.7827 |
| Run the same input again | 48 | 9,800 | 2,261,536.7827 |

The real spreadsheet engine ran all three refreshes. A temporary demonstration note survived. A conflicting-row test then preserved the last successful version. [Ten replay assertions passed](docs/refresh-demonstration.json). The delivered workbook starts with blank review annotations; it contains no invented completed reviews.

## Review notes

Edit the yellow Owner, Review status and Review note cells in **Category review**. Save that sheet as CSV UTF-8, then import it before refreshing:

```sh
python src/import_notes.py exported-review.csv
python refresh.py
```

Saved notes live in the separate, Git-ignored `data/notes/review_notes.csv`. Untouched template rows do not erase notes, and old keys remain stored. Reviewed requires an owner and note. Refresh does not read edits from a prior XLSX automatically. Detailed instructions and a troubleshooting table are in the [refresh guide](docs/REFRESH_GUIDE.md).

## Tests and verification

```sh
python -m unittest discover -s tests -v
pip install -r requirements-qa.txt
python tools/demo_refresh.py
python tools/verify_outputs.py
```

The 23 standard-library tests run without Node or the authoring package; publication tests use a clearly identified writer test double. The separate replay uses actual Excel generation, and independent QA inspects the delivered workbook. Six full-data reconciliations check row partitions and SQL totals. Native desktop Excel recalculation was not tested.

To reproduce the visual briefing and compact bundle:

```sh
pip install -r requirements-visuals.txt
python tools/build_presentation.py
python tools/package_project.py
```

## Relevant remote work

Recurring spreadsheet updates; CSV cleanup and merging; SQL summaries; exception handling; lightweight Python automation; clear refresh documentation. This is a personal portfolio demonstration, not a claimed client engagement or production deployment.

## Data context

Kaggle [Superstore Sales Dataset](https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting), uploader Rohit Sahoo, downloaded October 15, 2026. The data card labels it **GPL 2**. It is a historical sample, not verified transactions from a current retailer. The input CSVs replay one frozen source file as monthly deliveries; Kaggle lists its update frequency as Never. Dates span Jan 3, 2015–Dec 30, 2018. File presence does not prove a complete calendar month's business activity.

Currency is unspecified by the mirror. Sales remain in source monetary units, with four-decimal precision preserved in integer ten-thousandths; Excel displays two decimals. Sales are not profit, cash receipts or a forecast.

Original project code and documentation: MIT, [LICENSE](LICENSE). Included dataset values and data-derived reports retain the Kaggle source's GPL 2 label; see [data/LICENSE](data/LICENSE) and [NOTICE](NOTICE). Original file SHA-256: `{provenance['source_sha256']}`.
""",
)
write(
    "docs/SETUP.md",
    """# Setup and reproducibility

## Core workflow
Python 3.10+ runs ingestion, SQLite, note import and the 23 tests with the standard library. Selected monthly source files are already included. Run from this repository's root.

## Excel generation
`refresh.py` invokes `tools/build_workbook.mjs`. It requires Node.js and **@oai/artifact-tool**, supplied by a compatible Codex desktop dependency runtime. This dependency is not bundled in the repository and is not assumed to be publicly installable from npm. The ready-made XLSX can be opened independently; generating new workbooks requires that runtime or a separately implemented replacement writer.

The wrapper first uses `SALES_NODE`, then Node on PATH, then the documented runtime binary path. `ARTIFACT_RUNTIME_ROOT` points to the runtime's Node dependency root (the directory containing node_modules). On a standard Codex desktop setup, the default is `~/.cache/codex-runtimes/codex-primary-runtime/dependencies/node`. Set the variables explicitly if installed elsewhere:

```powershell
$env:SALES_NODE='C:/path/to/dependencies/node/bin/node.exe'
$env:ARTIFACT_RUNTIME_ROOT='C:/path/to/dependencies/node'
python refresh.py --render
```

These are task-specific paths to an installed authoring runtime, not credentials. Without the runtime the refresh fails clearly and leaves the last published version intact. The Python/SQL code, included source files and tests remain inspectable and usable.

## Recreate the monthly source deliveries
Optional: `python src/download_data.py` downloads the Kaggle snapshot into ignored `data/raw/`. `python src/prepare_demo.py` selects the documented eight columns and partitions by parsed Order Date. Original source values are retained. The source hash is in `docs/source-provenance.json`. If the public endpoint changes, download train.csv manually from the linked Kaggle page.

## QA and presentation dependencies
`pip install -r requirements-qa.txt` supplies read-only XLSX/PDF inspection. `pip install -r requirements-visuals.txt` supplies the optional chart and PDF builder. `python tools/demo_refresh.py` also needs the real spreadsheet runtime. `tools/verify_outputs.py` needs the original downloaded train.csv and delivered evidence. `tools/build_presentation.py` needs the verified evidence, while packaging uses only the standard library.

GitHub Actions runs the 23 core tests on Python 3.10 and 3.12. It does not pretend to install the optional private authoring runtime or recalculate in native desktop Excel.
""",
)
write(
    "docs/REFRESH_GUIDE.md",
    """# Operating and refresh guide

## Routine monthly refresh
1. Keep existing monthly delivery files in `data/incoming/`. Add the next file as `sales_YYYY-MM.csv` with the same eight required columns.
2. Run `python refresh.py`. Optional: `--input`, `--notes` and `--output` select other local locations. `--render` also writes three visual previews.
3. Open `runs/latest.json`, then the referenced run folder and workbook. The file is named for the latest delivered month; its parent run folder provides a unique UTC timestamp and run suffix.
4. Inspect coverage and any unmatched notes before using comparisons. Imported means the monthly file was present, not that every business transaction or calendar day is represented.

The input folder is the authoritative snapshot for each run. This is a full rebuild, not a hidden incremental append. Keep older files if historical results should remain included. An identical rerun creates a new audit version with unchanged data totals. Removing files deliberately changes the observed population; previous versions remain available.

## Save review notes
In Category review, edit the yellow Owner, Review status and Review note fields. Use Not started, In progress or Reviewed. Reviewed needs an owner and a note. The Next action formula prompts for missing prerequisites; the sheet is not password-protected.

Export **only Category review** as CSV UTF-8, preserving Month key text in YYYY-MM form. Run `python src/import_notes.py exported-review.csv`. Then rerun `python refresh.py`. The importer locates headers below title rows, validates the entire merge before replacing the notes file, preserves old keys not in the import and skips untouched rows. It cannot delete a saved note via blank fields; edit the notes CSV deliberately to clear an annotation and keep a backup.

Notes stay outside the generated workbook, keyed by month + category. Cases absent from the source appear in unmatched_notes.csv. The public note example is empty. Real notes and run folders are Git-ignored; keep client source files outside a public repository.

## Troubleshooting

| Message or symptom | Action |
|---|---|
| Missing/repeated column headers | Restore the documented export schema. |
| Order date does not match filename month | Move the row to its correct monthly delivery or fix the filename. Dates are day/month/year. |
| Conflicting Row ID | Verify the upstream export and replace the affected monthly file deliberately; the program never picks a conflicting version silently. |
| Identical repeated ID | The duplicate is skipped and logged in repeated_rows.csv; verify whether the upstream export repeats rows. |
| Missing file coverage | Add the missing delivery. A gap stays unavailable; it is not invented zero sales. |
| Reviewed needs owner and note | Supply both fields, or use In progress. |
| Excel generation failed | Inspect workbook-build.log in the staging directory and verify SETUP.md runtime paths. |
| Another refresh owns the lock | Let the running refresh finish. If it crashed, inspect `.refresh.lock` and its process ID before manually removing a stale lock. |

## Recovery and retention
The wrapper creates an isolated staging folder, then renames it into a successful version and atomically replaces latest.json. A malformed input or failed workbook build leaves the old pointer untouched and writes a failed-run JSON log. Failed staging directories are retained for diagnosis. Run cleanup and archival are manual; there is no unattended scheduler, watcher or retention policy. Do not edit files while a refresh is running. A lock serializes refreshes to the same output folder; it does not lock external source or notes editing.

The notes input is copied into the run before ingestion. Each accepted line carries source filename and row number; input hashes and the notes hash identify the version used. Renaming latest.json does not make every filesystem operation a database transaction. If a crash occurs between run-folder publication and pointer replacement, the older pointer remains valid and a complete, unreferenced version may be present.
""",
)
write(
    "docs/METHOD.md",
    """# Method and field definitions

## Required delivery fields
Row ID (text, unique line key); Order ID (text, multiple lines per order permitted); Order Date and Ship Date (day/month/year); Category, Region and Product ID (nonblank text); Sales (nonnegative finite decimal with at most four fractional places). Original column labels are preserved in the supplied CSVs. Dates must parse, order dates must match the filename month, shipping cannot precede ordering, and all lines for an Order ID must use one order date.

Missing/repeated headers and extra CSV fields fail the run. Row IDs must contain decimal digits. Identical repeated selected values for an ID keep the first deterministic file/row occurrence; differing selected values block publication. There is no auto-correction of conflicting identifiers. For a real client, establish the meaning and uniqueness of the export's line key before adaptation.

## Precision and measures
Sales are recorded amounts in unspecified source monetary units, not a calculated quantity × price because those factors are absent. Decimal values are stored as integer ten-thousandths in SQLite; more than four decimal places, nonfinite values, negatives and unsupported magnitudes are rejected. Total scaled values must fit the exact integer range used by the spreadsheet. Excel stores numeric amounts in original units and formats them to two decimals. The underlying four-decimal input precision is retained. A displayed sum of individually rounded figures can differ from the rounded precise total.

SQL owns accepted line, distinct order, monthly, region and month/category aggregates. An order's consistent order date makes monthly order counts additive; region order counts are not assumed additive. Average order amount divides sales by distinct orders for the same month. Workbook MoM = current / prior calendar month - 1; YoY = current / same month one year earlier - 1. Missing or zero bases produce n.a., not zero growth or a hidden formula error.

## Missing months
A calendar registry spans the first through last filename month. No file means unavailable counts and sales; an explicit header-only monthly file is known zero. True blanks are used for missing chart observations. A month/category absent from the source is not invented as a zero-review row. File coverage does not establish complete business activity; this sample's final recorded order is December 30, 2018.

## Notes
Separate CSV input: month, category, owner, status, note. Keys are month + category; duplicate note keys and unsupported states fail validation. Reviewed requires an owner and note. Imports retain unmatched keys and old notes that untouched template rows would otherwise erase. The workbook's status prompt mirrors those prerequisites. Empty delivered notes do not imply that any review was performed.

## Lineage and evidence
SQLite lines retain source_file and source_row (first data row = 2). Input SHA-256 values, notes-input SHA-256, row counts, repeat counts, six reconciliations and the generated workbook name appear in run-log.json. The analysis JSON includes all aggregate reports. A successful run is a distinct immutable version by convention; files are not access-protected against a user deliberately editing them.
""",
)
write(
    "docs/SOURCES.md",
    f"""# Source, provenance and licensing

- [Superstore Sales Dataset on Kaggle](https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting), uploader Rohit Sahoo. The data card describes a four-year retail sample and labels its license **GPL 2**, with update frequency Never.
- Download endpoint: https://www.kaggle.com/api/v1/datasets/download/rohitsahoo/sales-forecasting
- Downloaded October 15, 2026. Original file `train.csv`, 9,800 lines, 18 columns. SHA-256: `{provenance['source_sha256']}`.
- Original Order Date range: January 3, 2015–December 30, 2018, parsed as day/month/year.
- This project selects eight original fields and splits by received order month. No sales records are fabricated, extended or relabeled as current activity. The source itself is a Superstore sample; no real client or retailer engagement is claimed.
- The mirror does not define a currency. Monetary values are retained in source units; no dollar label or exchange rate is invented.
- Customer Name, Customer ID, address-related fields and other unused columns are omitted from the included selected-column deliveries.

Original project code and documentation are MIT licensed, see root LICENSE. The source dataset and data-derived reports retain the Kaggle GPL 2 label; its license text is in data/LICENSE. The transformation and source fingerprint are documented in source-provenance.json. Upstream licensing and provenance are described as the mirror presents them; no authorship of the source dataset is claimed.
""",
)
write(
    "docs/QA_REPORT.md",
    """# Verification report

Validated October 15, 2026, using all 9,800 original source lines and all 48 monthly input partitions.

- **23 automated tests:** day-first dates; four-decimal precision; zero/invalid amounts; invalid/wrong-month dates; shipping before order; repeated/conflicting IDs; distinct order counts; inconsistent order dates; missing versus explicit-zero months; malformed headers/filenames; stable note keys; unmatched notes; CSV preface; atomic invalid-note import; failed refresh preserving prior output; workbook failure; overlap lock; idempotent rerun.
- **Six full-data reconciliations:** source row partition, monthly sales, monthly order count, category sales, region sales and SQLite integrity.
- **Ten real-engine refresh checks:** 47 files to 48, added lines, month advancement, changed current-period value, retained demonstration annotation, identical rerun, rejected conflicting ID and retained last successful pointer/workbook. See refresh-demonstration.json. Core publication unit tests separately use an explicitly identified test double; they are not presented as spreadsheet-engine verification.
- **Independent output verification:** recomputation from the original train.csv, selected-column equality, typed dates, formula caches, YoY, chart binding/color, review dropdown and blank delivered notes. See independent-verification.json.
- **Workbook checks:** temporary imported amount change and restoration; source-total equality; review owner/note prerequisites; no formula error matches; all three sheets visually reviewed.
- **PDF and package:** both briefing pages visually reviewed, strict PDF parse and ZIP integrity checks. Per-file hashes accompany the bundle.

The optional spreadsheet authoring runtime is explicitly documented. Native desktop Excel recalculation was not tested. The source is historical sample data, currency is unspecified, and file presence does not prove a complete business month. There is no claimed time saving, client engagement or production deployment without evidence.
""",
)
write(
    "docs/PROJECT_WALKTHROUGH.md",
    """# Five-minute walkthrough

1. Show the brief and explain the client task: refresh a recurring sales workbook without rebuilding it manually.
2. Show data/incoming and the stable source Row ID. Explain that 48 files are historical replay partitions, not a live Kaggle subscription.
3. Run `python refresh.py`. Open latest.json and the new versioned workbook. Show current-period metrics, live formula references, the native chart and the yellow review-note inputs.
4. Open refresh-demonstration.json: 47 monthly inputs become 48, 459 lines arrive, a note survives and a repeat run does not add sales again.
5. Show the failed-conflict assertion and publication code: the old workbook stays available because latest.json changes only after successful generation.
6. Explain the handoff: export review notes as UTF-8 CSV, import by month/category key and refresh again. No automatic write-back from edited XLSX is claimed.
7. Run the 23 tests. Show the original-source verification and discuss the documented authoring-runtime and native-Excel limits.

Relevant tasks: recurring report refreshes, CSV cleanup/merging, SQL aggregation, spreadsheet formulas, exception handling and written operating guides. Adapt a client's real schema, line key, currency, return rules, reporting calendar and access constraints before using this example with private data.
""",
)
write(
    "docs/UPWORK_LISTING.md",
    """# Portfolio listing

Title: Automated Monthly Sales Reports | Python, SQL & Excel

Role: Portfolio project owner | CSV validation, report automation and Excel handoff

Description: Built a repeatable sales-reporting workflow using 9,800 Kaggle Superstore sample lines across 48 monthly CSVs. One command validates inputs, runs SQL reports and generates a dated Excel workbook with formulas and a chart. Saved notes rejoin by month/category. Conflicting imports preserve the last successful report. Includes 23 tests, real refresh-replay evidence, source attribution and a full operating guide. Historical sample data; compatible authoring runtime required for new workbook generation.

Skills: Python; SQL; Microsoft Excel; Data Cleaning; Automation.

Cover caption: One-command monthly refresh: CSV validation, SQL reports, live Excel formulas and preserved reviewer notes.

PDF caption: Two-page case study with actual refresh replay, failure recovery, operating instructions and verification.
""",
)
write(
    "NOTICE",
    """Monthly Sales Report Automation
Original project code and documentation: Copyright (c) 2026 Zak Rademacher, MIT licensed.

Dataset: Superstore Sales Dataset, Kaggle uploader Rohit Sahoo.
https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting
Kaggle license label: GPL 2. License text: data/LICENSE.
Selected-column monthly inputs and data-derived reports retain that source license label.
Transformation: original values in eight columns, partitioned by parsed Order Date.
No authorship of the source dataset is claimed. Historical sample, not client data.
""",
)
write(
    "deliverables/README.md",
    """# Ready-to-review deliverables

`monthly-sales_2018-12.xlsx` is the latest demonstrated workbook: report, all-month calculations and editable category-review notes. `case-study.pdf` is the two-page workflow briefing. The cover, trend graphic and three sheet previews show the public portfolio example. New report versions are produced by refresh.py; preserve notes through the documented CSV import before refresh. No macros or background watcher are used.
""",
)
print("Cover, two-page briefing and complete handoff documentation generated.")
