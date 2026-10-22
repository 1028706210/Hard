from __future__ import annotations

import re
from pathlib import Path


_BUILD_LINE = re.compile(r"Program\.cs\((\d+),(\d+)\):\s*(error|warning)\s+([A-Z]+\d+):\s*(.+)")
_RUNTIME_LINE = re.compile(r"in .*Program\.cs:line (\d+)")


def normalize_csharp_diagnostic(output: str, workspace: Path) -> str:
    """Normalize dotnet output into one safe Chinese diagnostic line."""
    safe = output.replace(str(workspace), "<workspace>").replace("\\", "/")
    nonempty = [line.strip() for line in safe.splitlines() if line.strip()]

    compile_line = next((line for line in nonempty if _BUILD_LINE.search(line)), None)
    if compile_line is not None:
        match = _BUILD_LINE.search(compile_line)
        assert match is not None
        row, column, _severity, code, message = match.groups()
        return f"编译错误（Program.cs 第 {row} 行，第 {column} 列，{code}）：{message}"

    headline = next(
        (
            line
            for line in nonempty
            if not line.startswith("at ") and not line.startswith("--- End of stack trace")
        ),
        "C# 运行失败",
    )
    frame_line = next((line for line in nonempty if "Program.cs:line " in line), None)
    if frame_line is not None:
        frame = _RUNTIME_LINE.search(frame_line)
        if frame is not None:
            return f"运行错误（第 {frame.group(1)} 行）：{headline}"
    return f"运行错误（未知位置）：{headline}"
