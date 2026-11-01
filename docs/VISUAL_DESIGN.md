# Maintaining the Monthly Sales presentation

The project uses white, cobalt and pink, aligned numerical displays and generous report spacing. Segoe UI and Arial use installed system fonts; PDF presentations use Helvetica. No proprietary font files are distributed.

`design-tokens.json` contains the native palette. Run `python tools/apply_native_theme.py` after rebuilding native report source. The existing report generator calls the applier where supported. Monthly Sales also retains its separate Tableau tokens and `tools/apply_visual_theme.py`. Chart roles, units, annotations and source attribution must remain visible. Excel exports stay light; their workbook builders retain the refreshed palette and formula definitions. PDF/HTML presentation builders retain the corresponding palette.

After editing source, open the native report in the desktop application, refresh it, inspect every page and a representative filter, restore the default selections, save and reopen it. Rebuild the existing portable package after the native save. Public previews are rendered from the working report. Tableau Public is not configured; the workbook runs locally in Tableau Desktop under the existing download arrangement.

Control example: **83,030.3888 matched-period sales; 223 orders; prior 95,007.3530 and 167 orders**. Compare the relevant source totals and mapped fields as well as displayed rounded labels. Formatting must not change calculations, missing values, duplicate policies, key relationships or the population used by a measure.

The cover source is in `presentation/`. Capture the actual current report into the image named in `presentation/cover.json`, then run `python presentation/build_cover.py --motion --workdir <scratch folder outside the project>`. This requires the development Playwright package and Edge. It writes the two cover sizes and a short cover animation into `deliverables/`. Cover motion does not make a native report or PDF an animated application.

Practice: change one accent in a disposable copy, rebuild and confirm the control example still reconciles. Check long labels, explicit warnings, missing/zero values, keyboard controls where available and thumbnail crops. Restore the approved palette. Keep older screenshots and verification records as dated history; record new checks separately.
