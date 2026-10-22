from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import os
from pathlib import Path
import subprocess
import threading
import time
from typing import Mapping, Sequence

import psutil


class ProcessStatus(StrEnum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    OUTPUT_OVERFLOW = "output_overflow"


@dataclass(frozen=True, slots=True)
class ProcessResult:
    status: ProcessStatus
    stdout: str
    stderr: str
    return_code: int | None
    duration_ms: int


def terminate_process_tree(process_id: int) -> None:
    try:
        parent = psutil.Process(process_id)
    except psutil.Error:
        return
    processes = parent.children(recursive=True)
    processes.append(parent)
    for process in reversed(processes):
        try:
            process.terminate()
        except psutil.Error:
            continue
    try:
        _gone, alive = psutil.wait_procs(processes, timeout=0.5)
    except psutil.Error:
        alive = processes
    for process in alive:
        try:
            process.kill()
        except psutil.Error:
            continue


def _minimal_environment(environment: Mapping[str, str], working_dir: Path) -> dict[str, str]:
    result = {
        "SystemRoot": os.environ.get("SystemRoot", r"C:\Windows"),
        "WINDIR": os.environ.get("WINDIR", r"C:\Windows"),
        "TEMP": str(working_dir),
        "TMP": str(working_dir),
    }
    result.update(environment)
    result.pop("PATH", None)
    return result


def execute_process(
    arguments: Sequence[str],
    *,
    cwd: Path,
    environment: Mapping[str, str],
    stdin: str,
    timeout_seconds: float,
    output_limit_bytes: int,
    cancellation: threading.Event | None = None,
) -> ProcessResult:
    if not arguments or any(not isinstance(argument, str) for argument in arguments):
        raise ValueError("invalid_process_arguments")
    started = time.monotonic()
    process = subprocess.Popen(
        list(arguments),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(cwd.resolve()),
        env=_minimal_environment(environment, cwd.resolve()),
        shell=False,
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
    )
    assert process.stdin is not None and process.stdout is not None and process.stderr is not None
    process.stdin.write(stdin.encode("utf-8"))
    process.stdin.close()

    captured_stdout = bytearray()
    captured_stderr = bytearray()
    captured_size = 0
    lock = threading.Lock()
    overflow = threading.Event()

    def read_stream(stream, destination: bytearray) -> None:
        nonlocal captured_size
        while chunk := stream.read(4096):
            with lock:
                remaining = max(0, output_limit_bytes - captured_size)
                destination.extend(chunk[:remaining])
                captured_size += len(chunk)
                if captured_size > output_limit_bytes:
                    overflow.set()

    readers = [
        threading.Thread(target=read_stream, args=(process.stdout, captured_stdout), daemon=True),
        threading.Thread(target=read_stream, args=(process.stderr, captured_stderr), daemon=True),
    ]
    for reader in readers:
        reader.start()

    status = ProcessStatus.COMPLETED
    while process.poll() is None:
        if cancellation is not None and cancellation.is_set():
            status = ProcessStatus.CANCELLED
            terminate_process_tree(process.pid)
            break
        if overflow.is_set():
            status = ProcessStatus.OUTPUT_OVERFLOW
            terminate_process_tree(process.pid)
            break
        if time.monotonic() - started > timeout_seconds:
            status = ProcessStatus.TIMED_OUT
            terminate_process_tree(process.pid)
            break
        time.sleep(0.01)
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        terminate_process_tree(process.pid)
    for reader in readers:
        reader.join(timeout=1)
    if status == ProcessStatus.COMPLETED and overflow.is_set():
        status = ProcessStatus.OUTPUT_OVERFLOW
    duration_ms = int((time.monotonic() - started) * 1000)
    return ProcessResult(
        status=status,
        stdout=bytes(captured_stdout).decode("utf-8", errors="replace"),
        stderr=bytes(captured_stderr).decode("utf-8", errors="replace"),
        return_code=process.returncode,
        duration_ms=duration_ms,
    )
