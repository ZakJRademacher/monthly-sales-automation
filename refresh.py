"""Validate monthly CSVs, generate Excel and atomically publish the successful report version."""

import argparse
import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from sales import analyze, write_json


def workbook_writer(stage, render=False):
    dependency = (
        Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies"
    )
    runtime = Path(os.environ.get("ARTIFACT_RUNTIME_ROOT", str(dependency / "node")))
    node = (
        os.environ.get("SALES_NODE")
        or shutil.which("node")
        or str(runtime / "bin/node.exe")
    )
    env = os.environ.copy()
    env["ARTIFACT_RUNTIME_ROOT"] = str(runtime)
    command = [node, str(ROOT / "tools/build_workbook.mjs"), str(stage)]
    if render:
        command.append("--render")
    result = subprocess.run(
        command, env=env, capture_output=True, text=True, check=False
    )
    (stage / "workbook-build.log").write_text(
        result.stdout + "\n" + result.stderr, encoding="utf-8"
    )
    if result.returncode:
        raise RuntimeError(
            "Excel generation failed; inspect workbook-build.log in the staging directory. A compatible @oai/artifact-tool runtime is required."
        )


def refresh(input_dir, notes, output, render=False, writer=None):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    lock = output / ".refresh.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError(
            "Another refresh owns the output lock; inspect .refresh.lock before retrying"
        ) from exc
    run_id = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "_"
        + uuid.uuid4().hex[:8]
    )
    stage = output / (".staging_" + run_id)
    os.write(fd, json.dumps({"pid": os.getpid(), "run_id": run_id}).encode())
    os.close(fd)
    try:
        stage.mkdir()
        snapshot = stage / "review_notes_input.csv"
        snapshot.write_bytes(
            Path(notes).read_bytes()
            if Path(notes).exists()
            else b"month,category,owner,status,note\n"
        )
        analysis = analyze(input_dir, snapshot, stage)
        (writer or workbook_writer)(stage, render)
        expected = stage / f"monthly-sales_{analysis['metrics']['last_month']}.xlsx"
        if not expected.is_file():
            raise RuntimeError("Workbook generation did not produce the expected XLSX")
        log = {
            "run_id": run_id,
            "status": "success",
            "metrics": analysis["metrics"],
            "input_files": analysis["files"],
            "checks": analysis["checks"],
            "workbook": expected.name,
            "notes_sha256": __import__("hashlib")
            .sha256(snapshot.read_bytes())
            .hexdigest(),
        }
        write_json(stage / "run-log.json", log)
        final = output / run_id
        stage.rename(final)
        pointer = {
            "run_id": run_id,
            "directory": run_id,
            "workbook": expected.name,
            "metrics": analysis["metrics"],
        }
        temp = output / ("latest_" + uuid.uuid4().hex + ".tmp")
        write_json(temp, pointer)
        os.replace(
            temp, output / "latest.json"
        )  # Published only after every required output exists.
        return {**pointer, "directory": str(final)}
    except Exception as exc:
        write_json(
            output / ("failed_" + run_id + ".json"),
            {
                "run_id": run_id,
                "status": "failed",
                "error": str(exc),
                "latest_preserved": True,
            },
        )
        raise
    finally:
        lock.unlink()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, default=ROOT / "data/incoming")
    p.add_argument("--notes", type=Path, default=ROOT / "data/notes/review_notes.csv")
    p.add_argument("--output", type=Path, default=ROOT / "runs")
    p.add_argument("--render", action="store_true")
    a = p.parse_args()
    try:
        print(json.dumps(refresh(a.input, a.notes, a.output, a.render), indent=2))
    except (ValueError, RuntimeError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
