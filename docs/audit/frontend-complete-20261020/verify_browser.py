"""Audit-only server ownership for Windows environments blocking taskkill /T."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen

import psutil

ROOT = Path(__file__).resolve().parents[3]
AUDIT = Path(__file__).resolve().parent
WEB = ROOT / "apps/web"
NODE = Path("C:/Program Files/nodejs/node.exe")
CONFIG = AUDIT / "playwright-external.config.mts"
RUN = AUDIT / f"browser-owned-{int(time.time() * 1000)}"
RUN.mkdir()


def ready(url: str) -> None:
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except OSError:
            pass
        time.sleep(0.2)
    raise RuntimeError(f"Server did not become ready: {url}")


def phase(name: str, files: list[str]) -> dict:
    directory = RUN / name
    directory.mkdir()
    environment = {**os.environ, "HARD_E2E_RUN_ID": f"run-{int(time.time() * 1000)}"}
    for key, child in {
        "HARD_VISUAL_AUDIT_DIR": "screenshots",
        "HARD_TASK55_AUDIT_DIR": "comparison",
        "HARD_AUDIT_SCREENSHOT_DIR": "flows",
        "HARD_UI_SCREENSHOTS": "maps",
    }.items():
        environment[key] = str(directory / child)
    processes: list[subprocess.Popen] = []
    identities = []
    handles = []
    result: dict = {"phase": name, "run_id": environment["HARD_E2E_RUN_ID"], "files": files}
    try:
        for label, command, cwd in [
            ("api", [sys.executable, str(ROOT / "apps/api/tests/e2e_server.py")], ROOT),
            ("web", [str(NODE), str(WEB / "node_modules/vite/bin/vite.js"), "--host", "127.0.0.1", "--port", "4173", "--strictPort"], WEB),
        ]:
            handle = (directory / f"{label}.log").open("w", encoding="utf-8")
            handles.append(handle)
            process = subprocess.Popen(command, cwd=cwd, env=environment, stdout=handle, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
            processes.append(process)
            identities.append({"label": label, "pid": process.pid, "create_time": psutil.Process(process.pid).create_time(), "command": command})
        ready("http://127.0.0.1:8000/api/_e2e/lifecycle")
        ready("http://127.0.0.1:4173/")
        command = [str(NODE), str(WEB / "node_modules/@playwright/test/cli.js"), "test", *files, "--config", str(CONFIG), "--reporter=json", "--output", str(directory / "results")]
        with (directory / "playwright.json").open("w", encoding="utf-8") as output, (directory / "playwright.stderr.log").open("w", encoding="utf-8") as errors:
            completed = subprocess.run(command, cwd=WEB, env=environment, stdout=output, stderr=errors, timeout=600)
        result["exit_code"] = completed.returncode
        try:
            result["stats"] = json.loads((directory / "playwright.json").read_text(encoding="utf-8"))["stats"]
        except (ValueError, KeyError) as error:
            result["report_parse_error"] = str(error)
            result["exit_code"] = completed.returncode or 1
    finally:
        cleanup_errors = []
        for process, identity in reversed(list(zip(processes, identities))):
            if process.poll() is not None:
                continue
            try:
                owned = psutil.Process(process.pid)
                if owned.create_time() != identity["create_time"]:
                    raise RuntimeError("Process identity changed; cleanup refused")
                descendants = owned.children(recursive=True)
                for child in reversed(descendants):
                    try:
                        child.kill()
                    except psutil.NoSuchProcess:
                        pass
                owned.kill()
                process.wait(timeout=10)
                _, alive = psutil.wait_procs(descendants, timeout=10)
                if alive:
                    raise RuntimeError(f"Owned descendants still alive: {[child.pid for child in alive]}")
            except (psutil.Error, OSError, RuntimeError) as error:
                cleanup_errors.append(str(error))
        for handle in handles:
            handle.close()
        result["processes"] = identities
        result["cleanup_errors"] = cleanup_errors
        (directory / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return result


print(f"Evidence: {RUN}", flush=True)
results = [phase("python", ["tests/e2e/python-journey.spec.ts"])]
if results[0]["exit_code"] == 0:
    files = [f"tests/e2e/{path.name}" for path in sorted((WEB / "tests/e2e").glob("*.spec.ts")) if path.name != "python-journey.spec.ts"]
    results.append(phase("battery", files))
(RUN / "summary.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
raise SystemExit(0 if len(results) == 2 and all(result["exit_code"] == 0 and not result["cleanup_errors"] for result in results) else 1)
