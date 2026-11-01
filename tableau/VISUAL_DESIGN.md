# Cobalt and rose presentation

The approved presentation pairs a refreshed native Tableau dashboard with a separate interactive browser companion. The native workbook runs locally; the repository supplies its preview and download under the existing arrangement.

The companion `deliverables/Monthly Sales Interactive.html` adds a live browser presentation: an animated cumulative comparison, direct day selection with the keyboard or pointer, and animated contribution bars. It is self-contained and works without network access. The native Tableau workbook and exported images remain separate static/native formats.

Rebuild the companion with `python tools/build_interactive.py`. Its 30 pairs of cumulative values and all seven contribution records reconcile to the same unchanged 67-row reporting CSV and validated business review. Monetary source values remain integer ten-thousandths; two-decimal browser labels use half-up display rounding. Half-cent labels can differ by 0.01 from older binary/half-even formatting; source values and totals are unchanged. Motion only reveals the final chart: values do not count up and it is never presented as live incoming data. Reduced-motion preferences disable the animation, and the day control remains usable by keyboard.

The three headline values lead into the matched-period trend, followed by the category and region contributions and the next investigation. Blue represents the current period and increases; pink represents declines. The prior period remains muted and explicitly labeled. No causal conclusion or new metric has been introduced.

`design-tokens.json` contains the palette and dashboard dimensions. `tools/apply_visual_theme.py` applies that presentation to the existing native workbook without rewriting the reporting CSV, queries, filters or field bindings. The normal build and packaging tools use these tokens so a rebuild retains the chosen design. Open and save in Tableau after rebuilding, then package and reopen the TWBX to inspect the result.

Practice: change the `accent` color and apply the theme to a disposable workbook copy. Confirm that declining bars change while the 223 orders and 83,030.39 displayed sales remain unchanged. Restore the chosen accent afterward. Cumulative sales remain a matched December 1–30 comparison; category and regional contributions are overlapping views.
