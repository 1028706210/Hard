---
id: python-stdlib-data-overview
title: Python 标准库概览
concepts: [tooling, functions]
objectives: [识别标准库模块的作用, 选择最小的内置能力解决问题]
prerequisites: [python-modules-io-oop-classes]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python3-stdlib.html
source_snapshot_date: 2026-08-23
---

# 先使用受维护的标准能力

标准库随 Python 一起提供常见问题的稳定接口。导入前先确认问题边界，避免为了一个简单操作引入不需要的第三方依赖。

```python
import math
print(math.ceil(2.1))
```

模块名表达职责，调用点应保留其来源。

```python
import json
print(json.dumps({"ready": True}))
```

## 概念定义与适用场景

标准库提供随解释器分发的常用能力。这里直接使用 math.ceil 表达向上取整，不需要第三方包；模块名让调用来源清楚。

## 语法、API 与边界

ceil 的方向是朝正无穷，不是远离零。因此 -2.1 得到 -2，而不是 -3。支架拒绝非有限数和范围外输入，避免让无意义的数值进入运算。

## 常见错误与实践建议

int 会向零截断，round 则是另一种舍入规则，都不能代替 ceil。用正小数、负小数和整数分别测试，不能只看 2.1 一个示例。
