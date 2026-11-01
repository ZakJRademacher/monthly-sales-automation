# Maintaining the Monthly Sales presentation

The working report uses the shared **Midnight / Blue / Orange** design: navy canvas, light text, electric blue for the primary series and warm orange for a comparison or emphasis. Labels, units, signs and definitions carry analytical meaning alongside color. Segoe UI and Arial are installed system fonts; no font files are distributed.

The redesign changes composition as well as color: a persistent left control rail, clear page navigation, a prominent lead metric, compact supporting metrics, larger charts and a separate explanation area. The native canvas is 1600 × 1000. Dense tables retain scrolling and source identifiers.

## Where to edit

- `design-tokens.json`: reusable palette and layout metadata.
- `tools/powerbi_layout.py` or `tools/tableau_layout.py`: native visual positions, spacing and formatting. Edit the helper rather than maintaining an unrelated picture of the dashboard.
- `tools/apply_native_theme.py`: apply the approved layout after rebuilding the existing native source. Run from the project root: `python tools/apply_native_theme.py`.
- The original native builders still generate data, calculations and visual queries. The layout helper must preserve those contracts.

Close the relevant desktop report before rebuilding source. Reopen it afterwards; Desktop keeps an in-memory copy and saving an older open report can overwrite newer source formatting. Keep the existing semantic-model format when Power BI offers an optional migration during a visual-only edit.

## Verify and hand off

1. Preserve a dated backup before changing native source or downloads.
2. Run the existing project tests. Compare source data, calculations, filters, relationships and visual queries with the pre-change baseline.
3. Open the actual report in Tableau Desktop or Power BI Desktop. Refresh, inspect every report page, exercise a representative filter and inspect tooltips and scrolling.
4. Restore default filters, save the editable source and save the existing downloadable format. Reopen the saved artifact to verify it independently.
5. Check small text, contrast, long labels, missing/zero values and exports. A screenshot is evidence of the current working report; it is not a replacement for the report.

Control example: **December 1–30, 2018: 83,030.3888 sales, 223 orders; matched prior: 95,007.3530 sales, 167 orders.** Displayed values may be rounded; the source arithmetic must remain unchanged.

## Motion and presentation

Native Power BI and Tableau reports retain their supported filtering, highlighting, hover detail and navigation. They do not implement the browser application's custom animated transitions. Static PDFs and Excel exports remain static. Monthly Sales additionally has a working browser report with a replayable daily comparison, keyboard control, responsive layout and reduced-motion support. Its source is `web/`; rebuild with `python tools/build_interactive.py`.

Keep Excel worksheets light. Preserve source attribution, analytical caveats and licenses in all exports. The working interfaces were reviewed before regenerating covers and public screenshots from the native captures on November 1, 2026. Cover choreography is distinct from report interaction. Historical benchmark evidence must not be described as rerun merely because the visual design changed.

## A small practice change

Make a disposable copy. Change one accent in `design-tokens.json`, reapply the layout, open the report and verify the control example above. Try one filter, then reset it. Success means the appearance changes while counts, totals, dates and filters behave identically. Restore the shared palette before using the report in the portfolio.
