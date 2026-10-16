# Method and field definitions

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
