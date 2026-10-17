# Report layout and interaction design

A 1280 × 900 canvas uses dark ink backgrounds, Georgia titles, Segoe UI labels and mint/coral/lilac category colors. Native Power BI visuals provide real hover, selection, sorting and filtering. Screenshots and PDF previews support the interactive PBIX.

| Page | Question | Interaction |
|---|---|---|
| The shape of sales | How do sales and category mix move? | Matched KPI cards, dynamic headline and trailing 12-month ribbon |
| Where momentum changes | Which segments account for the change? | Diverging category/region bars; clicks filter comparisons and arithmetic bridge |
| Follow the signal | Which products merit investigation? | Sortable comparison table filters monthly history and original source line references |
| Data & refresh | What was imported and how is it updated? | Full-snapshot counts, delivery coverage, definitions and instructions |

Month/category/region selectors synchronize across analysis pages. Month comes from a disconnected coverage table; category and region come from Sales. Date filtering is replaced for matched calculations while retaining business filters. The full-month ribbon and matched KPIs have explicitly different time bases.

Category colors encode identity. Signs and axes communicate direction. No currency symbol is assumed. Original product IDs are preserved; no names are invented. SourceFile and SourceRow provide traceability.

The ribbon offers a distinctive visual entry point. Bars and tables support precise comparisons and follow-up. Flowing ribbons show changing category ranks, not individual transactions migrating between categories. See the [operating guide](README.md) and [native validation](NATIVE_QA.md).
