"""Package the runnable example, source deliveries, handoff and verified report."""

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
(ROOT / "data/incoming/README.md").write_text(
    """# Monthly input deliveries

48 historical CSV files partitioned by Order Date from the downloaded Kaggle Superstore sample. They contain eight original columns, with original values retained. They replay monthly deliveries; no new sales were fabricated and no live update feed is claimed. Dates use day/month/year. Preserve older files for historical reporting. Source provenance and the GPL 2 license label are documented in docs/SOURCES.md and data/LICENSE.
""",
    encoding="utf-8",
    newline="\n",
)
files = []
for folder in [
    "src",
    "sql",
    "tools",
    "tests",
    "docs",
    "deliverables",
    "evidence",
    "powerbi",
    "data/incoming",
    ".github",
]:
    files.extend(
        p
        for p in (ROOT / folder).rglob("*")
        if p.is_file()
        and "__pycache__" not in p.parts
        and ".pbi" not in p.parts
        and not any(part.startswith(("latest_", "staging_")) for part in p.relative_to(ROOT).parts)
        and not p.name.endswith(".inspect.ndjson")
        and p.name != "package-manifest.json"
    )
files.extend(p for p in ROOT.glob("*") if p.is_file())
files.extend([ROOT / "data/LICENSE", ROOT / "data/notes/review_notes.example.csv"])
files = sorted(set(files))
manifest = ROOT / "docs/package-manifest.json"
manifest.write_text(
    json.dumps(
        {
            "files": [
                {
                    "path": p.relative_to(ROOT).as_posix(),
                    "bytes": p.stat().st_size,
                    "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                }
                for p in files
            ],
            "omitted": [
                "data/raw/*",
                "data/notes/review_notes.csv",
                "runs/*",
                "tmp/*",
                "__pycache__/*",
                "**/.pbi/*",
            ],
            "runtime": "Power BI Desktop for PBIX exploration; Python 3.10+ for data export. Optional XLSX generation also requires Node.js and compatible artifact-tool; see docs/SETUP.md and powerbi/README.md",
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
    newline="\n",
)
files.append(manifest)
target = ROOT.parent / "monthly-sales-automation-portfolio.zip"
with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for file in files:
        archive.write(
            file, "monthly-sales-automation/" + file.relative_to(ROOT).as_posix()
        )
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
print(
    json.dumps(
        {"zip": str(target), "files": len(files), "bytes": target.stat().st_size}
    )
)
