# Monthly Sales Review

Sales fell even though more orders came in. I compared the same December dates in both years, then looked at the categories, regions, and products behind the change.

The main report is a **Tableau brief**, backed by Python and SQLite analysis of **9,800 sales lines across 48 monthly exports**. It gives a reader the finding, the comparison, and a sensible place to investigate next.

[View the Tableau report](deliverables/tableau-sales-preview.png) · [Download the workbook](deliverables/Monthly%20Sales%20Review.twbx) · [Read the analysis](docs/METHOD.md)

![Tableau sales review comparing December 1–30 in 2018 and 2017](deliverables/tableau-sales-preview.png)

## What I found

For **December 1–30, 2018 versus the same dates in 2017**, sales fell **12.6%**, distinct orders rose **33.5%**, and sales per order fell **34.6%**. The full source contains **4,922 distinct orders**.

The East region had the largest regional decline, at **7,961.58 source monetary units**. Office Supplies had the largest category decline, at **7,265.53**. These are two views of overlapping sales, so adding them would double-count part of the change.

That tells us where to look, but it doesn't explain why customers spent less per order. The next step is to check source coverage and product mix in those segments. Quantity and unit-price data would be needed to separate price changes from volume changes. This source doesn't establish either field, a currency, or profit.

[SQL comparisons](sql/review_drivers.sql) · [Ranked product follow-ups](deliverables/review_actions.csv) · [Tableau definitions](docs/TABLEAU_REVIEW.md)

## Open or explore the work

**Tableau:** open the packaged workbook in Tableau Desktop. Reporting data is included. This is a fixed December brief: its written findings do not change when an individual worksheet is filtered. [Opening and editing guide](tableau/README.md).

**Power BI companion:** the [Monthly Sales Explorer](deliverables/Monthly%20Sales%20Explorer.pbix) provides four pages of interactive exploration, with month, category, and region filters and product-level source detail. It uses the same validated input, with its own documented calculations. [Open and refresh](powerbi/README.md) · [Static PDF](deliverables/Monthly%20Sales%20Explorer.pdf).

**Excel companion:** the [sales workbook](deliverables/monthly-sales_2018-12.xlsx) includes a monthly review and editable review-note inputs. [Preview](deliverables/excel-sales-review.png) · [Refresh guide](docs/REFRESH_GUIDE.md).

The [browser companion](deliverables/Monthly%20Sales%20Interactive.html) can be downloaded and opened locally. The generated [two-page briefing](deliverables/case-study.pdf) summarizes the same validated run.

## Explore or reproduce

From the repository root, using Python 3.10+ and the standard library:

```sh
python refresh.py --summary-only
```

Read `runs/latest.json`, then open the HTML review in the referenced run folder. The same folder contains SQL extracts, a SQLite database, input hashes, and the follow-up CSV. Excel generation uses the optional authoring runtime described in [setup](docs/SETUP.md).

Monthly CSVs pass through Python validation before SQLite builds the comparisons. Conflicting Row IDs stop publication; repeating the same inputs doesn't add sales again. Review notes are saved separately and rejoined by month and category.

## Methods and verification

- [Method and definitions](docs/METHOD.md) · [Source and licensing](docs/SOURCES.md) · [Operating guide](docs/PROJECT_GUIDE.md)
- [Tests](tests) · [Independent verification](docs/independent-verification.json) · [Power BI checks](powerbi/NATIVE_QA.md)
- [Editable Power BI model](powerbi/SalesExplorer.pbip) · [DAX](powerbi/native-measures.dax) · [Design maintenance](docs/VISUAL_DESIGN.md)

This independent project replays historical Kaggle Superstore data from 2015–2018 as monthly deliveries. Matching dates makes the comparison more useful, but doesn't prove the original source is complete. Refresh runs locally on demand.

Original code and documentation: [MIT](LICENSE). Data-derived files retain the source's GPL 2 label: [data license](data/LICENSE) and [NOTICE](NOTICE).
