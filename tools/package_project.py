"""Build a portable bundle and hash the exact packaged bytes."""
import argparse
import csv
import hashlib
import io
import json
import os
import sys
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
PROJECT = "monthly-sales-automation"
BUNDLE = "monthly-sales-automation-portfolio.zip"
PREFIX = "monthly-sales-automation"


def build(root=ROOT, results=None):
    root = Path(root).resolve()
    is_monthly = PROJECT == "monthly-sales-automation"
    if is_monthly:
        selected = None
        folders = ["src","sql","tools","tests","docs","deliverables","evidence","powerbi","data/incoming",".github"]
    else:
        from publication import current_output
        selected = current_output(results if results is not None else root/"results")
        folders = ["src","sql","tools","tests","docs","deliverables","data/sample",".github"]
    files = {}
    for folder in folders:
        for path in (root/folder).rglob("*"):
            rel = path.relative_to(root)
            if (not path.is_file() or any(part in {"__pycache__", ".pbi", "node_modules", ".git"} for part in rel.parts)
                or any(part.startswith(("latest_", "staging_", ".staging_", "~$")) for part in rel.parts)
                or path.suffix in {".pyc", ".zip"} or path.name.endswith(".inspect.ndjson")
                or path.name == "package-manifest.json"):
                continue
            files[rel.as_posix()] = path.read_bytes()
    root_names = {"README.md","LICENSE","NOTICE",".gitignore",".gitattributes","refresh.py","release.json"}
    for path in root.iterdir():
        if path.is_file() and (path.name in root_names or path.name.startswith("requirements") and path.suffix==".txt"):
            files[path.name] = path.read_bytes()
    if is_monthly:
        for name in ["data/LICENSE","data/notes/review_notes.example.csv"]:
            path = root/name
            if path.is_file():
                files[name] = path.read_bytes()
    else:
        if not selected.is_dir():
            raise ValueError("Run the pipeline before packaging")
        omitted = {"cleaned_lines.csv","review_queue.csv","quality_issues.csv","latest.json"}
        for path in selected.iterdir():
            if path.is_file() and path.suffix in {".json",".csv"} and path.name not in omitted:
                files["results/"+path.name] = path.read_bytes()
        filename = "cleaned_lines.csv" if PROJECT == "retail-sales-data-quality" else "review_queue.csv"
        sample_name = "cleaned_example_1000.csv" if PROJECT == "retail-sales-data-quality" else "review_examples_100.csv"
        count = 1000 if PROJECT == "retail-sales-data-quality" else 100
        if (selected/filename).is_file():
            output = io.StringIO(newline="")
            writer = csv.writer(output)
            with (selected/filename).open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.reader(stream)
                writer.writerow(next(reader))
                for number, row in enumerate(reader):
                    if number == count:
                        break
                    writer.writerow(row)
            files["data/sample/"+sample_name] = output.getvalue().encode("utf-8-sig")
        if PROJECT == "complaint-intake-operations":
            # A portable example never includes another reviewer's persistent notes.
            files["data/review_notes.csv"] = b"complaint_id,owner,review_status,notes\n"
    if "README.md" not in files or (not is_monthly and "results/analysis.json" not in files):
        raise ValueError("Incomplete package inputs")
    release = json.loads(files.get("release.json", b"{}"))
    manifest = {
        "package_schema": 2,
        "project": PROJECT,
        "release": release,
        "results_layout": "Static reference exports; a new pipeline run publishes results/latest.json" if not is_monthly else "Included input deliveries and validated Power BI sample",
        "files": [{"path": name, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()} for name, content in sorted(files.items())],
        "omitted": ["raw downloads","generated databases","complete row-level outputs","private review notes","local caches","older ZIPs"],
        "rebuild": "See README.md and docs",
    }
    manifest_bytes = (json.dumps(manifest, indent=2)+"\n").encode("utf-8")
    files["docs/package-manifest.json"] = manifest_bytes
    target = root/BUNDLE
    pending = root/(BUNDLE+"."+uuid.uuid4().hex+".tmp")
    try:
        with zipfile.ZipFile(pending, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, content in sorted(files.items()):
                info = zipfile.ZipInfo(PREFIX+"/"+name, (1980,1,1,0,0,0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, content)
        with zipfile.ZipFile(pending) as archive:
            if archive.testzip() is not None:
                raise ValueError("Package integrity check failed")
            for record in manifest["files"]:
                content = archive.read(PREFIX+"/"+record["path"])
                if hashlib.sha256(content).hexdigest() != record["sha256"]:
                    raise ValueError("Packaged file differs from its manifest")
        (root/"docs").mkdir(exist_ok=True)
        (root/"docs/package-manifest.json").write_bytes(manifest_bytes)
        os.replace(pending, target)
    finally:
        if pending.exists():
            pending.unlink()
    return {"zip": str(target), "files": len(files), "sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "manifest_verified": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, help="Optional published result root; latest.json is resolved once")
    args = parser.parse_args()
    print(json.dumps(build(results=args.results), indent=2))
