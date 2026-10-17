# Operating and refresh guide

## Start with the business review
Use `python refresh.py --summary-only` for an ordinary Python-only refresh, or `python refresh.py` to include Excel. In the latest run folder, open sales-review.html and review_actions.csv. Inspect the headline, matched periods and category/region drivers, then trace the ranked product IDs back to orders before acting. Adding the next monthly CSV advances the review automatically. The script reads local deliveries; it does not claim a live Kaggle feed.

## Routine monthly refresh
1. Keep existing monthly delivery files in `data/incoming/`. Add the next file as `sales_YYYY-MM.csv` with the same eight required columns.
2. Run `python refresh.py --render --pdf` for Excel, HTML, CSV, previews and a matching PDF. Install the dependencies in SETUP.md first. Omit the flags for just Excel/HTML/CSV. Optional: `--input`, `--notes` and `--output` select other local locations. `--render` also writes six visual previews.
3. Open `runs/latest.json`, then the referenced run folder and workbook. The file is named for the latest delivered month; its parent run folder provides a unique UTC timestamp and run suffix.
4. Inspect coverage and any unmatched notes before using comparisons. Imported means the monthly file was present, not that every business transaction or calendar day is represented.

The input folder is the authoritative snapshot for each run. This is a full rebuild, not a hidden incremental append. Keep older files if historical results should remain included. An identical rerun creates a new audit version with unchanged data totals. Removing files deliberately changes the observed population; previous versions remain available.

## Save review notes
In Category review, edit the yellow Owner, Review status and Review note fields. Use Not started, In progress or Reviewed. Reviewed needs an owner and a note. The Next action formula prompts for missing prerequisites; the sheet is not password-protected.

Export **only Category review** as CSV UTF-8, preserving Month key text in YYYY-MM form. Run `python src/import_notes.py exported-review.csv`. Then rerun `python refresh.py`. The importer locates headers below title rows, validates the entire merge before replacing the notes file, preserves old keys not in the import and skips untouched rows. It cannot delete a saved note via blank fields; edit the notes CSV deliberately to clear an annotation and keep a backup.

Notes stay outside the generated workbook, keyed by month + category. Cases absent from the source appear in unmatched_notes.csv. The public note example is empty. Real notes and run folders are Git-ignored; keep client source files outside a public repository.

## Troubleshooting

| Message or symptom | Action |
|---|---|
| Missing/repeated column headers | Restore the documented export schema. |
| Order date does not match filename month | Move the row to its correct monthly delivery or fix the filename. Dates are day/month/year. |
| Conflicting Row ID | Verify the upstream export and replace the affected monthly file deliberately; the program never picks a conflicting version silently. |
| Identical repeated ID | The duplicate is skipped and logged in repeated_rows.csv; verify whether the upstream export repeats rows. |
| Missing file coverage | Add the missing delivery. A gap stays unavailable; it is not invented zero sales. |
| Reviewed needs owner and note | Supply both fields, or use In progress. |
| Excel generation failed | Inspect workbook-build.log in the staging directory and verify SETUP.md runtime paths. |
| PDF generation failed | Inspect briefing-build.log in the retained staging folder; install reportlab. The previous successful report stays current. |
| Another refresh owns the lock | Let the running refresh finish. If it crashed, inspect `.refresh.lock` and its process ID before manually removing a stale lock. |

## Recovery and retention
The wrapper creates an isolated staging folder, then renames it into a successful version and atomically replaces latest.json. A malformed input or failed workbook build leaves the old pointer untouched and writes a failed-run JSON log. Failed staging directories are retained for diagnosis. Run cleanup and archival are manual; there is no unattended scheduler, watcher or retention policy. Do not edit files while a refresh is running. A lock serializes refreshes to the same output folder; it does not lock external source or notes editing.

The notes input is copied into the run before ingestion. Each accepted line carries source filename and row number; input hashes and the notes hash identify the version used. Renaming latest.json does not make every filesystem operation a database transaction. If a crash occurs between run-folder publication and pointer replacement, the older pointer remains valid and a complete, unreferenced version may be present.

## What updates and what is editable
Every refresh rebuilds KPI cards, native chart bindings, comparison labels, segment order and ranked product leads for the latest delivery. The Excel cards and charts link to Monthly detail O:S; the plain-language headline and ranked list regenerate when the pipeline runs. Editing a cell manually does not rerun Python, re-rank leads or rewrite the HTML/PDF. Edit source CSVs and rerun for a consistent new report.

The first sheet compares matched day cutoffs. Monthly report shows full observed months; its YoY can differ because the prior month can contain additional days. Review notes are the intended manual workbook inputs. Keep source files and client annotations private.
