# Reports and companion files

Start with the [Tableau brief](Monthly%20Sales%20Review.twbx), or [view its preview](tableau-sales-preview.png). It reviews the fixed December 1–30 comparison.

The [Power BI explorer](Monthly%20Sales%20Explorer.pbix) is the interactive companion. It includes imported data and four pages for the overview, comparisons, products, and data definitions. Its [PDF](Monthly%20Sales%20Explorer.pdf) is a static export. [Power BI guide](../powerbi/README.md) · [Native checks](../powerbi/NATIVE_QA.md).

The [Excel workbook](monthly-sales_2018-12.xlsx) contains four sheets, comparison formulas, charts, and review-note inputs. [Refresh guide](../docs/REFRESH_GUIDE.md). The [two-page briefing](case-study.pdf) is an earlier written summary of the matched-period analysis.

Download `sales-review.html` and open it locally. Keep `review_actions.csv` beside it for the download link. The browser report contains the comparison, segment changes, and product IDs to investigate; GitHub displays its source rather than running it.

The separate [interactive browser presentation](Monthly%20Sales%20Interactive.html) animates the fixed December comparison. It is built from the Tableau reporting data with `python tools/build_interactive.py`; `python refresh.py` does not update it.

`python refresh.py --render --pdf` regenerates the Excel/HTML/CSV outputs and matching briefing for the latest inputs. It needs the optional authoring runtime and reportlab described in [setup](../docs/SETUP.md). Save review notes through the CSV import before refreshing. Recorded workbook checks use the authoring engine; native Excel recalculation remains untested.
