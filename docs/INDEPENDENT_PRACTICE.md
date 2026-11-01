# Independent monthly-sales practice

Use a disposable copy. Attempt this before consulting the [worked comparison definitions](METHOD.md) or finished report SQL.

## Your task

Review November 2018 instead of the default December example. In the Power BI explorer, select that month and check the comparison caption. For a Python-only attempt, copy the input CSVs through November 2018 into a separate input folder and use the documented `--input` and `--output` arguments with `--summary-only`; leave the original exports and saved notes untouched.

Write an independent SQL aggregation for one region: matched current/prior dates, distinct orders, recorded sales and sales per order. Reconcile the amounts to source records, then explain whether the category or regional breakdown accounts for the arithmetic change. Do not add overlapping breakdowns together or infer unit price, quantities, profit or causes that the source does not establish.

## Acceptance checks

- The comparison uses the same global day-of-month cutoff in both years; a business filter does not silently change it.
- Distinct order IDs, line counts and sales totals are different measures. Category order counts need not be additive.
- Your region total matches a separate source calculation and its source file/row references.
- Missing or zero baselines are explicit; an undefined percentage stays blank.
- Describe one plausible alternative explanation, the additional data required to investigate it and one failure you can diagnose.

Keep your query, actual results, reconciliation and a short explanation together. The Tableau decision brief is a fixed December historical analysis; changing a worksheet selection does not turn its written findings into a November analysis. The Power BI explorer and Python-generated review have their own documented controls. This exercise is provided for practice, not represented as already completed.
