from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

import psutil


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

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
