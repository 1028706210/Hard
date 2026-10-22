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

CSV 的逗号与换行可能位于引号内部，因此不能简单 split 行与字段。DictReader 使用表头作为键，解析后仍需验证列数和空值。

## 语法、API 与边界

本课只接受单列 name；挑战只接受单列 count 并求非负整数总和。表头无数据是合法空表；完全空输入则缺少表头。支架严格解析后再输出，避免输出半份结果才发现错误。

## 常见错误与实践建议

不要用第一行数据替代表头，也不要把额外列悄悄丢弃。引号中的逗号和换行仍属于字段，测试应覆盖这些情况。
