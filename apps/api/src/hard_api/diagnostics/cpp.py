from __future__ import annotations

import re
from pathlib import Path


_COMPILE_LINE = re.compile(r"([A-Za-z0-9_][A-Za-z0-9_.-]*\.(?:cpp|cc|cxx|h|hpp)):(\d+):(\d+):\s*(?:fatal\s+)?error:\s*(.+)")


def normalize_cpp_diagnostic(output: str, workspace: Path) -> str:
    """Normalize g++ output into one safe Chinese diagnostic line."""
    safe = output.replace(str(workspace), "<workspace>").replace("\\", "/")
    nonempty = [line.strip() for line in safe.splitlines() if line.strip()]

    compile_line = next((line for line in nonempty if _COMPILE_LINE.search(line)), None)
    if compile_line is not None:
        match = _COMPILE_LINE.search(compile_line)
        assert match is not None
        name, row, column, message = match.groups()
        return f"编译错误（{name} 第 {row} 行，第 {column} 列）：{message}"

    headline = next(iter(nonempty), "C++ 运行失败")
    return f"运行错误（未知位置）：{headline}"
