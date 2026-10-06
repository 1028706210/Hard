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

Python OS解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
