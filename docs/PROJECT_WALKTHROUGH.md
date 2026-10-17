# Five-minute walkthrough

## Lead with the useful result
Open deliverables/sales-review.html: sales −12.6%, orders +33.5%, average order value −34.6% for matched December 1–30 periods. Show East and Office Supplies, then the product IDs in review_actions.csv. Explain why this guides investigation but does not prove a cause. Run `python refresh.py --summary-only` without any third-party packages to reproduce the review. Show the first Sales review Excel sheet if discussing spreadsheet work. The underlying replay and controls below support this result.

1. Show the brief and explain the client task: refresh a recurring sales workbook without rebuilding it manually.
2. Show data/incoming and the stable source Row ID. Explain that 48 files are historical replay partitions, not a live Kaggle subscription.
3. Run `python refresh.py`. Open latest.json and the new versioned workbook. Show current-period metrics, live formula references, the native chart and the yellow review-note inputs.
4. Open refresh-demonstration.json: 47 monthly inputs become 48, 459 lines arrive, a note survives and a repeat run does not add sales again.
5. Show the failed-conflict assertion and publication code: the old workbook stays available because latest.json changes only after successful generation.
6. Explain the handoff: export review notes as UTF-8 CSV, import by month/category key and refresh again. No automatic write-back from edited XLSX is claimed.
7. Run the 34 tests. Show the original-source verification and discuss the documented authoring-runtime and native-Excel limits.

Relevant tasks: recurring report refreshes, CSV cleanup/merging, SQL aggregation, spreadsheet formulas, exception handling and written operating guides. Adapt a client's real schema, line key, currency, return rules, reporting calendar and access constraints before using this example with private data.
