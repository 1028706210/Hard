---
id: python-concurrency-network-subprocess
title: Python subprocess
concepts: [security, tooling]
objectives: [理解命令执行的风险, 用纯函数检查受控命令配置]
prerequisites: [python-concurrency-network-requests]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python-subprocess.html
source_snapshot_date: 2026-08-23
---

# 命令必须受控

不得把用户文本交给 subprocess。本课不导入 subprocess，只验证允许命令名称的静态列表；Runner 的进程限制保持不变。

```python
allowed = {"python"}
print("python" in allowed)
```

参数应以结构化列表表达，而不是 shell 字符串。

```python
command = ["python", "--version"]
print(command[0])
```

## 概念定义与适用场景

执行前可以先验证结构化命令，但本题只输出决策。命令名与参数数量都属于规则，不应允许空参数或多个白名单选项任意组合。字符串切分也不是通用 shell 解析器。

## 语法、API 与边界

读取命令描述，用任意空白切分成列表。只允许恰好两个字段：python --version 或 python -V；输出 allowed。其他非空命令输出 rejected。空输入无输出，退出码 1。不执行命令，不导入 subprocess 或 shell。支架已提供 parts。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
