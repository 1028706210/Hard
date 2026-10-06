---
id: python-modules-io-oop-files
title: Python 文件
concepts: [io, exceptions]
objectives: [在受控临时目录中读写文本文件, 使用 with 确保文件句柄关闭]
prerequisites: [python-modules-io-oop-input-output]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/python3/python3-file-methods.html
source_snapshot_date: 2026-08-23
---

# 文件操作限定在授权目录

文件句柄是资源，应使用 `with` 明确打开范围。学习题只操作 Runner 临时工作目录中的固定文件名，不读取用户磁盘或系统路径。

```python
from pathlib import Path
Path("note.txt").write_text("ready", encoding="utf-8")
```

读取时指定编码并在边界处理异常。

```python
from pathlib import Path
print(Path("note.txt").read_text(encoding="utf-8"))
```

## 概念定义与适用场景

文件 API 把字节或文本保存在命名路径中，适合小型配置、导出和可审计的学习产物。`with open(...)` 或 `Path` 的读写方法将资源生命周期限定在代码块内，避免句柄泄漏和未刷新的缓冲区。

## 语法、API 与边界

文本读写必须显式指定 `encoding='utf-8'`，并区分 `r`、`w`、`a` 的覆盖与追加语义。相对路径在 Runner 中只解析到该题的临时工作目录；路径穿越、用户主目录和系统目录都不属于课程题允许范围。空文件是正常边界，缺失文件或非法编码应走清晰的异常分支。

## 常见错误与实践建议

不要把一次 `read()` 当成永远安全的操作，也不要在异常发生后忘记关闭资源。写入前确认覆盖策略，读取外部文件前限制大小；测试至少覆盖普通文本、空文本和无法处理的输入。
