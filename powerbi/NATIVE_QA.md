# Native Power BI validation

Validated in Power BI Desktop on October 16–17, 2026. This is a historical public-data portfolio demonstration, not a client engagement.

## Calculations

The [native DAX query](../evidence/powerbi/native-checks.dax) ran in Desktop's DAX query view and returned **13 True checks**. [Actual result screenshot](../evidence/powerbi/native-dax-checks.png).

Checks cover 9,800 sales lines; 1,461 calendar dates; 4,922 distinct orders; total sales of 2,261,536.7827; matched December sales of 83,030.3888 versus 95,007.3530; matched orders of 223 versus 167; the arithmetic bridge; regional/category filters; a stable global cutoff under a product filter; and unavailable prior delivery in January 2015. Floating-point comparisons use tolerances recorded in the query.

## Interactions observed in Desktop

- Category Office Supplies changed sales to 29,638.01 and orders to 170, and focused the category ribbon.
- Selecting East on the drivers page filtered category bars, headline and bridge. Bridge effects of 9,453.06 and −17,414.65 reconciled to −7,961.58. Selecting it again cleared the selection.
- Selecting product OFF-BI-10000545 filtered its history and original source-file/row references. Product IDs remain source identifiers; names were not invented.
- Selecting January 2015 displayed unavailable prior-year comparisons. Quality-page coverage continued to show the full imported snapshot.

## Actual refresh replay

The same DataFolder was first exported from 47 historical delivery files, excluding December 2018. Home > Refresh in Desktop showed November 2018: sales **117,938.16**, **259** orders and average order **455.36**. [November export metrics](../evidence/powerbi/november-export.json); [actual November screenshot](../evidence/powerbi/november-refresh.png).

After adding the original December file and exporting all 48 files, Home > Refresh moved the unselected report month to December: sales **83,030.39**, **223** orders and average order **372.33**. The ribbon moved to January–December 2018 without layout edits. [Actual December screenshot](../evidence/powerbi/december-refresh.png). Final published snapshot: `aa9c70b67f36a2be`.

## Export and delivery checks

The October 16–17 native validation used a standard-library suite with **38 passing tests**, including exact integer sales units/source lineage, repeat export reuse, rejected-input preservation and failed-pointer-publication preservation. These Python tests do not execute DAX. Snapshot export-verification JSON records exporter checks only; this document records the separate native observations.

All four pages were exported through Desktop to `deliverables/Monthly Sales Explorer.pdf`, rendered and visually inspected for clipping and legibility. PDF and PNG previews are static representations; the PBIX provides interaction.

## Limits

Power BI Service publication, a gateway and unattended scheduling are not configured or tested. Concurrent exports or pointer changes during Desktop refresh are unsupported. An explicitly empty prior-month delivery was covered by core logic tests, but was not separately exercised through the native UI. A comprehensive keyboard/screen-reader audit and native Microsoft Excel recalculation were not performed.

The final PBIX was saved, closed and reopened in Desktop on October 17. The custom category palette, typography, imported December totals and all four page tabs persisted. [Reopened Desktop screenshot](../evidence/powerbi/reopened-desktop.png).

## October 21 code update

The local reliability update adds regression tests for damaged or missing snapshot files, annotation-import structure and bundle contents. The full suite now has 42 tests. This update does not repeat or extend the historical Desktop/DAX observations above.
