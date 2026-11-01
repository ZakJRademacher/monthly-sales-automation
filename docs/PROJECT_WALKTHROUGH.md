# Five-minute walkthrough

## Lead with the useful result

Open the [Tableau brief](../deliverables/Monthly%20Sales%20Review.twbx). Compare December 1–30 in both years: sales fell 12.6%, orders rose 33.5%, and sales per order fell 34.6%. Explain why the East and Office Supplies declines overlap, then show the product IDs in `review_actions.csv` as follow-up leads.

## Trace the analysis

1. Open `data/incoming` and explain why Row ID identifies a sales line while Order ID can repeat. The 48 files replay a frozen historical source, rather than a live subscription.
2. Run `python refresh.py --summary-only`. Read `runs/latest.json` and open the HTML review in that run folder. The Python-only path needs no third-party packages.
3. Inspect the SQL comparison and trace one product back to its source file and row. Keep the shared date cutoff visible when comparing years.
4. Open `docs/refresh-demonstration.json`. Its recorded replay adds December to 47 earlier files, bringing in 459 lines. A note survives, and repeating the input doesn't add sales again.
5. Show the failed-conflict check: a rejected input leaves the previous successful report current.

## Show the companion reports

The [Power BI explorer](../deliverables/Monthly%20Sales%20Explorer.pbix) adds synchronized month, category, and region filters, plus product and source detail. Its PDF is a static export. [Power BI guide](../powerbi/README.md) · [Native checks](../powerbi/NATIVE_QA.md).

The Excel workflow uses `python refresh.py` and the optional authoring runtime in [setup](SETUP.md). Review notes must be exported as UTF-8 CSV and imported by month/category key before refreshing; edits to an old XLSX are not read automatically.

Finish by explaining one limitation: the source doesn't establish currency, quantities, prices, profit, or why sales changed. Run the 42 tests when checking the portable workflow. Keep their results separate from the documented native-application checks.
