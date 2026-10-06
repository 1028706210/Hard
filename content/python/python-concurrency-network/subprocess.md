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

`subprocess` 用于受控地启动已知本机程序，但它把文本变成进程边界，因此风险远高于普通函数调用。安全设计从白名单、结构化参数、固定工作目录、超时和输出上限开始，而不是从拼接 shell 字符串开始。

## 语法、API 与边界

真实代码应传递参数列表并避免 `shell=True`，同时检查返回码、标准输出和错误输出。课程题用纯函数审核命令计划：命令名和参数都必须落在允许集合；它不导入或运行 `subprocess`，也不会放宽 Runner 对进程树的限制。

## 常见错误与实践建议

不要把用户输入、路径或配置值直接视为命令。将“允许”“拒绝”“格式错误”分别测试，记录安全摘要而不是完整敏感参数；生产场景还需要操作系统权限与人工审批。
