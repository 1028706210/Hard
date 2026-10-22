from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

import psutil
import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import hard_api.runners.processes as processes
from hard_api.runners.processes import ProcessStatus, execute_process


PYTHON = Path("D:/DevTools/python/python.exe")


def test_timeout_terminates_parent_child_and_grandchild_processes(tmp_path: Path) -> None:
    script = tmp_path / "tree.py"
    child_pid_file = tmp_path / "child.pid"
    grandchild_pid_file = tmp_path / "grandchild.pid"
    child_code = (
        "from pathlib import Path; import subprocess, sys, time; "
        "grandchild = subprocess.Popen([sys.executable, '-I', '-c', 'import time; time.sleep(30)']); "
        f"Path({str(grandchild_pid_file)!r}).write_text(str(grandchild.pid), encoding='utf-8'); "
        "time.sleep(30)"
    )
    script.write_text(
        "from pathlib import Path\n"
        "import subprocess, sys, time\n"
        f"child = subprocess.Popen([sys.executable, '-I', '-c', {child_code!r}])\n"
        f"Path({str(child_pid_file)!r}).write_text(str(child.pid), encoding='utf-8')\n"
        "time.sleep(30)\n",
        encoding="utf-8",
    )

    result = execute_process(
        [str(PYTHON), "-I", str(script)],
        cwd=tmp_path,
        environment={},
        stdin="",
        timeout_seconds=0.3,
        output_limit_bytes=64 * 1024,
    )

    assert result.status == ProcessStatus.TIMED_OUT
    for _ in range(30):
        if child_pid_file.exists() and grandchild_pid_file.exists():
            break
        time.sleep(0.05)
    assert child_pid_file.exists() and grandchild_pid_file.exists()
    child_pid = int(child_pid_file.read_text(encoding="utf-8"))
    grandchild_pid = int(grandchild_pid_file.read_text(encoding="utf-8"))
    time.sleep(0.2)
    assert not psutil.pid_exists(child_pid)
    assert not psutil.pid_exists(grandchild_pid)


def test_output_limit_and_cancellation_have_stable_statuses(tmp_path: Path) -> None:
    overflowing = execute_process(
        [str(PYTHON), "-I", "-c", "print('x' * 70000)"],
        cwd=tmp_path,
        environment={},
        stdin="",
        timeout_seconds=5,
        output_limit_bytes=64 * 1024,
    )
    assert overflowing.status == ProcessStatus.OUTPUT_OVERFLOW
    assert len(overflowing.stdout.encode("utf-8")) <= 64 * 1024

    cancelled = threading.Event()
    holder: dict[str, object] = {}
    thread = threading.Thread(
        target=lambda: holder.setdefault(
            "result",
            execute_process(
                [str(PYTHON), "-I", "-c", "import time; time.sleep(30)"],
                cwd=tmp_path,
                environment={},
                stdin="",
                timeout_seconds=5,
                output_limit_bytes=64 * 1024,
                cancellation=cancelled,
            ),
        )
    )
    thread.start()
    time.sleep(0.1)
    cancelled.set()
    thread.join(timeout=5)

    assert holder["result"].status == ProcessStatus.CANCELLED


def test_process_helpers_fail_closed_for_missing_processes_and_strip_path(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(processes.psutil, "Process", lambda _pid: (_ for _ in ()).throw(psutil.NoSuchProcess(1)))
    processes.terminate_process_tree(1)

    environment = processes._minimal_environment({"PATH": "unsafe", "CUSTOM": "value"}, tmp_path)
    assert "PATH" not in environment
    assert environment["CUSTOM"] == "value"

    with pytest.raises(ValueError, match="invalid_process_arguments"):
        execute_process([], cwd=tmp_path, environment={}, stdin="", timeout_seconds=1, output_limit_bytes=1)


def test_process_tree_kills_survivors_after_termination(monkeypatch) -> None:
    calls: list[str] = []

    class Child:
        def __init__(self, *, fails: bool = False) -> None:
            self.fails = fails

        def terminate(self) -> None:
            calls.append("terminate-child")
            if self.fails:
                raise psutil.AccessDenied(123)

        def kill(self) -> None:
            calls.append("kill-child")
            if self.fails:
                raise psutil.AccessDenied(123)

    class Parent(Child):
        def children(self, recursive: bool) -> list[Child]:
            assert recursive is True
            return [child]

    child = Child(fails=True)
    parent = Parent()
    monkeypatch.setattr(processes.psutil, "Process", lambda _pid: parent)
    monkeypatch.setattr(processes.psutil, "wait_procs", lambda _items, timeout: ([], [child]))

    processes.terminate_process_tree(123)

    assert calls == ["terminate-child", "terminate-child", "kill-child"]


def test_process_tree_handles_wait_access_denied_without_escaping(monkeypatch) -> None:
    calls: list[str] = []

    class Process:
        def children(self, recursive: bool) -> list["Process"]:
            assert recursive is True
            return []

        def terminate(self) -> None:
            calls.append("terminate")

        def kill(self) -> None:
            calls.append("kill")

    process = Process()
    monkeypatch.setattr(processes.psutil, "Process", lambda _pid: process)
    monkeypatch.setattr(
        processes.psutil,
        "wait_procs",
        lambda _items, timeout: (_ for _ in ()).throw(psutil.AccessDenied(123)),
    )

    processes.terminate_process_tree(123)

    assert calls == ["terminate", "kill"]
