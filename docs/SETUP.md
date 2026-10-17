# Setup and reproducibility

## Portable useful output
Run `python refresh.py --summary-only` with Python 3.10+ alone. No pip install or spreadsheet runtime is required. Open the HTML report and prioritized CSV in the directory referenced by runs/latest.json. The Node dependency below applies only to optional XLSX generation. Add `--pdf` after installing `reportlab` to produce the same designed two-page report without Excel generation: `python refresh.py --summary-only --pdf`.

## Core workflow
Python 3.10+ runs ingestion, SQLite, note import and the 34 tests with the standard library. Selected monthly source files are already included. Run from this repository's root.

## Excel generation
`refresh.py` invokes `tools/build_workbook.mjs`. It requires Node.js and **@oai/artifact-tool**, supplied by a compatible Codex desktop dependency runtime. This dependency is not bundled in the repository and is not assumed to be publicly installable from npm. The ready-made XLSX can be opened independently; generating new workbooks requires that runtime or a separately implemented replacement writer.

The wrapper first uses `SALES_NODE`, then Node on PATH, then the documented runtime binary path. `ARTIFACT_RUNTIME_ROOT` points to the runtime's Node dependency root (the directory containing node_modules). On a standard Codex desktop setup, the default is `~/.cache/codex-runtimes/codex-primary-runtime/dependencies/node`. Set the variables explicitly if installed elsewhere:

```powershell
$env:SALES_NODE='C:/path/to/dependencies/node/bin/node.exe'
$env:ARTIFACT_RUNTIME_ROOT='C:/path/to/dependencies/node'
python refresh.py --render --pdf
```

These are task-specific paths to an installed authoring runtime, not credentials. Without the runtime the refresh fails clearly and leaves the last published version intact. The Python/SQL code, included source files and tests remain inspectable and usable.

## Recreate the monthly source deliveries
Optional: `python src/download_data.py` downloads the Kaggle snapshot into ignored `data/raw/`. `python src/prepare_demo.py` selects the documented eight columns and partitions by parsed Order Date. Original source values are retained. The source hash is in `docs/source-provenance.json`. If the public endpoint changes, download train.csv manually from the linked Kaggle page.

## QA and presentation dependencies
`pip install -r requirements-qa.txt` supplies read-only XLSX/PDF inspection. `pip install -r requirements-visuals.txt` supplies reportlab for the optional PDF builder. `python tools/demo_refresh.py` also needs the real spreadsheet runtime. `tools/verify_outputs.py` needs the original downloaded train.csv and delivered evidence. `tools/build_presentation.py` needs the verified evidence, while packaging uses only the standard library.

GitHub Actions runs the 34 core tests on Python 3.10 and 3.12. It does not pretend to install the optional private authoring runtime or recalculate in native desktop Excel.

The `--render` previews require the spreadsheet runtime. PDF rendering into portfolio PNGs uses optional Poppler: `pdftoppm -r 144 -png -f 1 -singlefile deliverables/case-study.pdf deliverables/portfolio-cover`. The PDF builder itself needs no Poppler or Matplotlib.
