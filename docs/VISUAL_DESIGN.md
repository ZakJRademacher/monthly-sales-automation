# Maintaining the Monthly Sales presentation

The native report uses navy backgrounds, light text, blue for the main series, and orange for comparisons or emphasis. Keep labels, signs, units, and definitions readable alongside the colors. Fonts are installed Segoe UI and Arial; no font files are distributed.

## Where to edit

`design-tokens.json` holds the shared palette and layout metadata. `tools/powerbi_layout.py and tools/tableau_layout.py` controls the native visual positions and formatting. The original report builders still define the data, calculations, and queries.

After rebuilding source, apply the layout from the repository root:

```sh
python tools/apply_native_theme.py
```

Close the report in Desktop before rebuilding, then reopen it. Saving an older in-memory copy can overwrite newer source changes. For a visual-only Power BI edit, keep the existing semantic-model format rather than accepting an optional format migration.

## Verify and hand off

1. Back up the source and download before editing.
2. Run the project tests and compare data, calculations, relationships, filters, and visual queries with the baseline.
3. Open the actual report in its desktop application. Refresh it, inspect every page, and check representative filters, tooltips, and scrolling.
4. Restore defaults, save the editable source and portable download, then reopen that download.
5. Check long labels, small text, contrast, blank and zero values, and PDF exports. Capture previews from the working report.

Control example: **December 1–30, 2018: 83,030.3888 sales and 223 orders. Matched 2017: 95,007.3530 sales and 167 orders.** Rounded labels may differ in precision from the source; underlying calculations must agree.

## Motion and presentation

Native report interactions include the filtering, highlighting, hover detail, and navigation described in the report guide. Motion covers are separate presentation files. PDF exports show a static view; long native tables may contain more rows than an exported page can display.

Keep source attribution and analytical qualifications in the report. A new screenshot or color change does not establish a new data benchmark or refresh test. Record any new checks separately from the historical evidence.

## A small practice change

In a disposable copy, change one accent in `design-tokens.json`, apply the layout, and verify the control example. Test a supported interaction, then reset it. The appearance should change while the figures and filter definitions stay consistent. Restore the shared palette before portfolio use.

The separate browser report has a daily comparison replay, keyboard controls, and reduced-motion support. Its source is `web/`; rebuild it with `python tools/build_interactive.py`. Those transitions do not run inside Tableau or Power BI.
