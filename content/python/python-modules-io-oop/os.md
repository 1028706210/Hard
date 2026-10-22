---
id: python-modules-io-oop-os
title: Python OS
concepts: [io, tooling]
objectives: [使用 pathlib 组合受控路径, 避免从外部输入直接构造系统路径]
prerequisites: [python-modules-io-oop-files]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python3-os-file-methods.html
source_snapshot_date: 2026-08-23
---

# 以路径对象表达文件位置

路径操作应限制在应用已授权的根目录。`pathlib` 让组合和检查路径更清晰；不要把不受信任的文本直接传给文件系统 API。

```python
from pathlib import Path
path = Path("reports") / "today.txt"
print(path.name)
```

路径的名称和父目录可分别读取，不必手工拆分字符串。

```python
from pathlib import Path
path = Path("notes") / "lesson.txt"
print(path.parent.name)
```

## 概念定义与适用场景

路径对象可以仅表示路径文本，不一定执行文件操作。PurePosixPath 固定使用 / 分隔，适合这个跨平台的教学输入；真实本机文件操作应选择相应的 Path 并确认授权范围。

## 语法、API 与边界

path.name 取得最后一段，path.parent 表示父路径。支架在构造前拒绝 .、.. 与空段，避免解析时归一化掩盖原始输入。本题的字符白名单是简化教学规则，不是所有操作系统合法文件名的完整定义。

## 常见错误与实践建议

组合路径不等于创建文件，也不证明路径存在。不要把输入交给 open 或执行系统命令；本题只打印路径末段，不需要联网、创建目录或修改环境变量。
