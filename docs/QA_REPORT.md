# Verification report

## Business-output checks
Nine additional tests cover equal day cutoffs, leap-year handling, zero and missing baselines, the exact arithmetic bridge, ranked segment declines, source product IDs, HTML escaping and the Python-only refresh. The suite now has 34 tests. Seven full-data business reconciliations check category/region current, prior and change totals and the arithmetic bridge. Independent verification recomputes the matched comparison from the original source CSV and inspects cached workbook results.

Redesigned and revalidated October 16, 2026, using all 9,800 original source lines and all 48 monthly input partitions.

- **34 automated tests:** day-first dates; four-decimal precision; zero/invalid amounts; invalid/wrong-month dates; shipping before order; repeated/conflicting IDs; distinct order counts; inconsistent order dates; missing versus explicit-zero months; malformed headers/filenames; stable note keys; unmatched notes; CSV preface; atomic invalid-note import; failed refresh preserving prior output; workbook failure; overlap lock; idempotent rerun.
- **Six full-data reconciliations:** source row partition, monthly sales, monthly order count, category sales, region sales and SQLite integrity.
- **Fifteen real-engine refresh checks:** 47 files to 48, added lines, month advancement, changed current-period value, retained demonstration annotation, identical rerun, rejected conflicting ID and retained last successful pointer/workbook. See refresh-demonstration.json. Core publication unit tests separately use an explicitly identified test double; they are not presented as spreadsheet-engine verification.
- **Independent output verification:** recomputation from the original train.csv, selected-column equality, typed dates, formula caches, YoY, chart binding/color, review dropdown and blank delivered notes. See independent-verification.json.
- **Workbook checks:** temporary imported amount change and restoration; source-total equality; review owner/note prerequisites; no formula error matches; all four sheets visually reviewed.
- **PDF and package:** both briefing pages visually reviewed, strict PDF parse and ZIP integrity checks. Per-file hashes accompany the bundle.

The optional spreadsheet authoring runtime is explicitly documented. Native desktop Excel recalculation was not tested. The source is historical sample data, currency is unspecified, and file presence does not prove a complete business month. There is no claimed time saving, client engagement or production deployment without evidence.

## Redesigned presentation
The two added tests reject failed or missing requested PDFs before publication. Actual-engine replay still passes all 15 checks. The final artifact includes three native chart objects; the first-sheet cards link to matched-period calculations, with dynamic sign formatting. Both PDF pages and all workbook views were rendered and visually checked. A fresh PDF is generated within each requested run; static portfolio PNGs are rendered from that PDF separately. See DESIGN.md.
