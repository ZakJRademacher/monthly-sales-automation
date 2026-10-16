# Monthly Sales Report Automation

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

Original project code and documentation: MIT, [LICENSE](LICENSE). Included dataset values and data-derived reports retain the Kaggle source's GPL 2 label; see [data/LICENSE](data/LICENSE) and [NOTICE](NOTICE). Original file SHA-256: `dbb0f167b27ccf02d7ff8cb0446a9abc6dbc3522e83cf9daa6939801acfdd196`.
