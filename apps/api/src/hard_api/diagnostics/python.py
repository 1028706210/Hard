from __future__ import annotations

import re
from pathlib import Path


_LINE = re.compile(r"line (\d+)")


def normalize_python_diagnostic(stderr: str, workspace: Path) -> str:
    safe = stderr.replace(str(workspace), "<workspace>").replace("\\", "/")
    line = _LINE.search(safe)
    caret_column = next((item.index("^") + 1 for item in safe.splitlines() if "^" in item), None)
    location = f"第 {line.group(1)} 行" if line else "未知位置"
    if caret_column is not None:
        location = f"{location}，第 {caret_column} 列"
    message = next((item.strip() for item in reversed(safe.splitlines()) if item.strip()), "Python 执行失败")
    if "SyntaxError" in safe:
        return f"语法错误（{location}）：{message}"
    if "AssertionError" in safe:
        return f"断言失败（{location}）：{message}"
    if "Timeout" in safe:
        return f"执行超时（{location}）：{message}"
    return f"运行错误（{location}）：{message}"
