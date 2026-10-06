---
id: python-stdlib-data-csv
title: Python csv
concepts: [io, collections]
objectives: [在内存文本中读取 CSV 行, 使用 DictReader 按列名访问数据]
prerequisites: [python-stdlib-data-re]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python-csv.html
source_snapshot_date: 2026-08-23
---

# 按列名处理表格数据

CSV 是文本表格格式。数据可能包含空值和额外列，读取后应按明确列名验证，而不是假定位置永远不变。

```python
import csv
from io import StringIO
print(next(csv.reader(StringIO("a,b\n"))))
```

DictReader 让字段语义更明确。

```python
import csv
from io import StringIO
print(next(csv.DictReader(StringIO("name\nHard\n")))["name"])
```


## 概念定义与适用场景

Python csv解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
