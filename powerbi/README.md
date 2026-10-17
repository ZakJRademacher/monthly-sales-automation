# The shape of sales / Power BI

A native four-page Power BI report over the validated Kaggle Superstore sample. The editable project is [SalesExplorer.pbip](SalesExplorer.pbip); its semantic model, native visual definitions, Power Query and DAX source are included. Desktop validation and delivery evidence are recorded in [NATIVE_QA.md](NATIVE_QA.md).

## Open and explore

Open `deliverables/Monthly Sales Explorer.pbix` from the repository root in Power BI Desktop. The PBIX contains the imported public sample so it can be explored before configuring a local refresh path. GitHub cannot execute a PBIX in its browser preview. The editable PBIP references its sibling Report and SemanticModel folders; keep them together.

- **01 The shape of sales:** month, category and region selectors; matched sales, orders and average order value; a responsive headline; a trailing 12-month category ribbon. Hover for values and rank movements. Colors identify categories, not favorable or unfavorable performance.
- **02 Where momentum changes:** click category or region bars to filter the other comparison and arithmetic bridge. Click the selected bar again to clear it. Category and region are overlapping views; never add their totals together.
- **03 Follow the signal:** select a product ID or click a product table row to filter the history and original source file/row references. Click the selected row again to clear it. This is an interactive detail page, not right-click drillthrough. Product history and source detail cover different periods, labeled on the page.
- **04 Data & refresh:** full-snapshot validation counts, monthly file coverage, operating steps and source limitations. Overview slicers do not hide historical coverage here.

The three common selectors synchronize between the first three pages. Without one selected month, calculations use the latest imported month. A chart selection is local to its page. Clear chart selections as well as slicers to return to overall totals. In Desktop edit mode, visual frames can appear on selection.

## Weekly or monthly refresh

1. Retain historical files in `data/incoming`. Add or replace `sales_YYYY-MM.csv` files using the same eight columns and day/month/year dates. The [input contract](../docs/REFRESH_GUIDE.md) explains stable IDs, corrected files and rejection behavior.
2. From the repository root run:

   ```sh
   python powerbi/export_data.py
   ```

3. In Desktop, use **Transform data > Edit parameters** to set `DataFolder` to your absolute `powerbi/sample-data` folder, without a trailing slash. Apply changes, then select **Home > Refresh**. Set this path once per computer or folder relocation.
4. Check Data & refresh and the comparison caption before saving. Clear the month selector to follow the newest delivery; an explicitly selected month remains selected.

Python 3.10+ and its standard library are sufficient for the export. No Node or spreadsheet authoring package is required for Power BI. Desktop Refresh reads prepared exports; it does not execute Python. No folder watcher, live feed, gateway or unattended schedule is configured. Excel/HTML/PDF generation remains independent through `refresh.py`.

For private client work:

```sh
python powerbi/export_data.py --input C:/private/client-deliveries --output C:/private/powerbi-data
```

Set DataFolder to that output. Map client exports into the documented contract first; arbitrary CSV labels are not automatically understood. Keep client data out of public repositories.

## Consistent snapshots and failures

Python and SQLite validate the complete delivery folder. The exporter writes four typed CSVs under `sample-data/snapshots/<content fingerprint>/`, then atomically replaces `latest.json` after all tables and export checks succeed. Identical input reuses its snapshot; repeated runs do not accumulate sales. Rejected input or failed pointer replacement leaves the previous published snapshot current.

**Do not run exports concurrently or change the pointer during a Desktop refresh:** separate table queries may read it at different times. Older snapshots remain until deliberately archived. Failed publication can leave an unused snapshot or temporary pointer; it does not become current.

Export-verification files record Python checks only and do not assert Desktop/DAX verification. Native checks are separate evidence and are not automatically inherited by later exports. Local `.pbi` caches and user settings are excluded from Git and the portfolio ZIP.

## Model and calculations

| Table | Grain and purpose |
|---|---|
| Sales | One accepted Row ID; text identifiers, integer SalesUnits, source file/row |
| Dates | One calendar day; one-to-many relationship to Sales[OrderDate], single-direction filtering |
| DeliveryCoverage | One calendar month, disconnected; imported versus missing files |
| Quality | One validation metric, disconnected; full-snapshot counts |

Amounts divide integer ten-thousandths by 10,000 once in DAX. No currency symbol is asserted. Average order value is sales / distinct order IDs in the filtered selection. Orders may contain multiple categories and are not additive across categories.

Matched KPIs use the selected month's global last order date and a common day-of-month cutoff in both years. Business filters change amounts, not the cutoff. Missing prior delivery leaves prior values and changes blank; an explicitly empty prior file is zero, with percentage change blank. File presence does not certify an accounting close.

The ribbon and product history use full observed monthly amounts for a trailing 12-month window ending at the report month. This differs from matched KPIs. Ribbon order encodes category rank, not transactions moving between categories. The order-count/order-value bridge is algebraic, not causal. Sales are not profit, cash receipts or forecasts.

## Maintain the report source

`tools/build_sales_powerbi.py` rebuilds PBIP definitions from the current export. It overwrites generated definitions; close Desktop and back up intentional manual design edits before running it. It is optional for routine data refresh. Queries are in `queries/`; [native-measures.dax](native-measures.dax) contains complete report calculations. The builder uses `measures.dax` as its base calculation source.

The sample contains 9,800 accepted lines, 4,922 distinct orders and 48 monthly files. It has zero skipped repeats; no cleanup savings or client engagement are claimed. [Source and license](../docs/SOURCES.md).

## References

- [Native ribbon charts](https://learn.microsoft.com/en-us/power-bi/visuals/desktop-ribbon-charts)
- [Power BI slicers](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-slicers)
- [Power BI project files](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
- [Visual inspiration: Spend Analytics Dashboard](https://www.informationisbeautifulawards.com/showcase/6585-spend-analytics-dashboard). Its restrained palette and exploratory hierarchy informed the direction; no assets were copied.
