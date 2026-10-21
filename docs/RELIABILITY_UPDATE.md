# Reliability update October 21 2026

The note importer rejects truncated and extra CSV fields, duplicate mapped headers and invalid quoting before replacing the persistent file. Structurally complete, valid edits and untouched-row preservation remain supported. The Power BI exporter compares all four typed CSV files and export-verification.json before reusing an existing snapshot. A missing or changed file is rejected before latest.json is replaced. The packager excludes older archives and private notes, includes current docs, and verifies exact archived bytes.

## Validation

The updated local suite passes 42 tests on Python 3.12.14. Regression tests exercise the affected failure scenarios and package freshness, repeated builds and archived-byte hashes. Full historical input was reprocessed with unchanged headline figures. Native Excel/Power BI refresh and optional presentation regeneration were not repeated.

## Release provenance

This release is based on the GitHub commit recorded in release.json. The October 21 regression and full-data checks verify the reliability changes described above. Native desktop verification remains limited to the earlier observations documented in this project.
