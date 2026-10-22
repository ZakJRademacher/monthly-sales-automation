# Setup and reproducibility

## Portable useful output
Run `python refresh.py --summary-only` with Python 3.10+ alone. No pip install or spreadsheet runtime is required. Open the HTML report and prioritized CSV in the directory referenced by runs/latest.json. The Node dependency below applies only to optional XLSX generation. Add `--pdf` after installing `reportlab` to produce the same designed two-page report without Excel generation: `python refresh.py --summary-only --pdf`.

## Core workflow
Python 3.10+ runs ingestion, SQLite, note import and the 42 tests with the standard library. Selected monthly source files are already included. Run from this repository's root.

## Excel generation
`refresh.py` invokes `tools/build_workbook.mjs`. It requires Node.js and **@oai/artifact-tool**, supplied by a compatible spreadsheet authoring runtime. This dependency is not bundled in the repository and is not assumed to be publicly installable from npm. The ready-made XLSX can be opened independently; generating new workbooks requires that runtime or a separately implemented replacement writer.

The wrapper uses `SALES_NODE` or Node on PATH. Set `ARTIFACT_RUNTIME_ROOT` to an installed authoring runtime's Node dependency root (the directory containing node_modules), or make the package resolvable from this project. Set `PYTHON` if the workbook metadata helper should use a Python executable other than `python`:

```powershell
$env:PYTHON='C:/path/to/python.exe'
$env:SALES_NODE='C:/path/to/dependencies/node/bin/node.exe'
$env:ARTIFACT_RUNTIME_ROOT='C:/path/to/dependencies/node'
python refresh.py --render --pdf
```

These are task-specific paths to an installed authoring runtime, not credentials. Without the runtime the refresh fails clearly and leaves the last published version intact. The Python/SQL code, included source files and tests remain inspectable and usable.

## Recreate the monthly source deliveries
Optional: `python src/download_data.py` downloads the Kaggle snapshot into ignored `data/raw/`. `python src/prepare_demo.py` selects the documented eight columns and partitions by parsed Order Date. Original source values are retained. The source hash is in `docs/source-provenance.json`. If the public endpoint changes, download train.csv manually from the linked Kaggle page.

## QA and presentation dependencies
`pip install -r requirements-qa.txt` supplies read-only XLSX/PDF inspection. `pip install -r requirements-visuals.txt` supplies reportlab for the optional PDF builder. `python tools/demo_refresh.py` also needs the real spreadsheet runtime. `tools/verify_outputs.py` needs the original downloaded train.csv and delivered evidence. `tools/build_presentation.py` needs the verified evidence, while packaging uses only the standard library.

GitHub Actions runs the 42 core tests on Python 3.10 and 3.12. It does not pretend to install the optional private authoring runtime or recalculate in native desktop Excel.

The `--render` previews require the spreadsheet runtime. PDF rendering into portfolio PNGs uses optional Poppler: `pdftoppm -r 144 -png -f 1 -singlefile deliverables/case-study.pdf deliverables/portfolio-cover`. The PDF builder itself needs no Poppler or Matplotlib.

## Native Power BI dashboard

The interactive report is `deliverables/Monthly Sales Explorer.pbix` from the repository root. See [Power BI setup, exploration and refresh](../powerbi/README.md) and [native verification](../powerbi/NATIVE_QA.md). Its four-page PDF and PNG previews are static native exports; the PBIX contains the interactive report and imported public sample.

Workbook authoring also uses Python 3.10+ for display-only theme metadata normalization. Set `PYTHON` to its executable if `python` is unavailable. This helper preserves native workbook parts and does not recalculate formulas.
