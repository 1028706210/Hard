from __future__ import annotations

import re


_COMPILE_LINE = re.compile(r"(\S+\.java):(\d+):")
_STACK_FRAME = re.compile(r"\((\S+\.java):(\d+)\)")


def normalize_java_diagnostic(output: str, workspace) -> str:
    """Normalize javac/JVM output into one safe Chinese diagnostic line."""
    safe = output.replace(str(workspace), "<workspace>").replace("\\", "/")
    nonempty = [line.strip() for line in safe.splitlines() if line.strip()]

    compile_line = next((line for line in nonempty if _COMPILE_LINE.search(line)), None)
    if compile_line is not None:
        match = _COMPILE_LINE.search(compile_line)
        name = match.group(1)
        row = match.group(2)
        message = compile_line[match.end():].strip() or compile_line
        return f"编译错误（{name} 第 {row} 行）：{message}"

    headline = next((line for line in nonempty if not line.startswith("at ")), "Java 运行失败")
    frame_line = next((line for line in reversed(nonempty) if line.startswith("at ") and ".java:" in line), None)
    if frame_line is not None:
        frame = _STACK_FRAME.search(frame_line)
        if frame is not None:
            return f"运行错误（第 {frame.group(2)} 行）：{headline}"
    return f"运行错误（未知位置）：{headline}"
