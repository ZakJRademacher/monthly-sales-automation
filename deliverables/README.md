# Ready-to-review reports

Start with `case-study.pdf` for the generated two-page sales briefing or `monthly-sales_2018-12.xlsx` for the editable four-sheet workbook. `excel-sales-overview.png` shows the actual Excel opening view; `portfolio-cover.png` is page one of the PDF rendered as an image. Supporting workbook previews include the full first sheet, history, monthly inputs, matched calculations and note-entry workflow.

Download `sales-review.html` and open it locally. It is responsive and self-contained; keep `review_actions.csv` beside it for the download link. GitHub displays HTML source. The report includes matched dates, segment changes and product IDs to investigate.

Run `python refresh.py --render --pdf` to regenerate the design and findings for the latest monthly inputs. See docs/SETUP.md for the optional spreadsheet runtime and reportlab. Save review notes through the documented CSV import before refresh. The authoring engine verified formulas; native Microsoft Excel recalculation remains untested.
