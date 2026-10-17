# Visual design and interpretation

## Reader and decision
The report is for a small-business owner or operations manager reviewing monthly sales. It answers: Did sales change? Was that associated with order count or average order value? Which segments and product IDs deserve investigation?

## Visual language
Warm paper (#F8F6F1), dark ink (#20323C), muted slate (#647579), teal (#126F69) and terracotta (#B74732). The HTML/PDF use a serif editorial title with sans-serif data; Excel uses Arial for predictable rendering. Sign, labels and exact numbers accompany color. Units and cutoff dates remain visible.

Excel compares current and prior segment sales with two editable, cell-bound column charts; gray is prior and teal is current. A third native line chart shows full observed-month history. Bars start at zero. HTML/PDF use diverging change bars with a shared symmetric magnitude scale across category and region; zero sits in the center. Region and category declines overlap and are not additive. The workbook keeps detailed inputs and arithmetic inspectable rather than flattening the report to an image.

## Views and calculations
- Sales review: current results, prior baselines, segment comparisons, arithmetic bridge, ranked leads.
- Monthly report: full observed-month sales history and coverage, which differs from matched-day comparisons.
- Monthly detail: all-month inputs and formulas in A:J; matched-period inputs, calculations and chart ranges in O:S. Sources are cited beside inputs. This is a working calculation area, not a terminal audit.
- Category review: yellow editable owner/status/note fields with stable month + category keys.

The PDF is a concise two-page output: up to four leading rows per segment view and the first five review leads; full detail remains in HTML, Excel and review_actions.csv. New schemas or unusually long segment names require layout review. There are no slicers, macros, live feeds or cloud schedules. All deliverables use the same validated run. Excel formulas and native charts recalculate from linked cells; generated narrative and ranks update through the Python refresh.

## Design references
Reviewed these public discussions for inspiration and critique, without copying their charts, layout files or assets:
- [Regional sales dashboard, r/dataisbeautiful](https://www.reddit.com/r/dataisbeautiful/comments/l0ff0l/)
- [Superstore performance dashboard discussion, r/dataisbeautiful](https://www.reddit.com/r/dataisbeautiful/comments/1cn1qfy/)

The implementation is an original report for this project's question and existing verified data. The design preserves source attribution and historical-sample context.

## Verification and scope
All four sheets and both PDF pages were rendered and reviewed. The builder changes and restores a source amount to verify card propagation, checks full-data totals, exercises note prerequisites, and scans formula errors. An actual-engine refresh replay adds a month, reruns identical input and rejects a conflict. Independent QA checks saved values, formula links, three chart objects and exported colors. This does not constitute native Microsoft Excel recalculation verification; that remains untested.
