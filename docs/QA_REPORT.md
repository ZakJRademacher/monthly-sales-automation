# Verification report

Validated October 15, 2026, using all 9,800 original source lines and all 48 monthly input partitions.

- **23 automated tests:** day-first dates; four-decimal precision; zero/invalid amounts; invalid/wrong-month dates; shipping before order; repeated/conflicting IDs; distinct order counts; inconsistent order dates; missing versus explicit-zero months; malformed headers/filenames; stable note keys; unmatched notes; CSV preface; atomic invalid-note import; failed refresh preserving prior output; workbook failure; overlap lock; idempotent rerun.
- **Six full-data reconciliations:** source row partition, monthly sales, monthly order count, category sales, region sales and SQLite integrity.
- **Ten real-engine refresh checks:** 47 files to 48, added lines, month advancement, changed current-period value, retained demonstration annotation, identical rerun, rejected conflicting ID and retained last successful pointer/workbook. See refresh-demonstration.json. Core publication unit tests separately use an explicitly identified test double; they are not presented as spreadsheet-engine verification.
- **Independent output verification:** recomputation from the original train.csv, selected-column equality, typed dates, formula caches, YoY, chart binding/color, review dropdown and blank delivered notes. See independent-verification.json.
- **Workbook checks:** temporary imported amount change and restoration; source-total equality; review owner/note prerequisites; no formula error matches; all three sheets visually reviewed.
- **PDF and package:** both briefing pages visually reviewed, strict PDF parse and ZIP integrity checks. Per-file hashes accompany the bundle.

The optional spreadsheet authoring runtime is explicitly documented. Native desktop Excel recalculation was not tested. The source is historical sample data, currency is unspecified, and file presence does not prove a complete business month. There is no claimed time saving, client engagement or production deployment without evidence.
