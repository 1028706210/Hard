---
id: python-flow-collections-conditions
title: Python 条件控制
concepts: [control-flow, operators]
objectives: [编写 if 和 else 分支, 根据布尔表达式选择唯一执行路径]
prerequisites: [python-flow-collections-sets]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-conditional-statements.html
source_snapshot_date: 2026-08-23
---

# 让条件决定路径

条件语句根据布尔表达式选择一个代码块。每个分支应给出可解释的结果，避免把无关动作混在同一判断中。

```python
score = 80
if score >= 70:
    print("pass")
```

`else` 处理条件不成立的情况，使两种结果都被明确覆盖。

```python
ready = False
if ready:
    print("start")
else:
    print("wait")
```

## 概念定义与适用场景

if 与 else 为同一个判断提供互斥分支。本题把等于 70 归入通过，先判断 >= 再处理其余有效成绩；输入校验与成绩判断分别负责不同问题。

## 语法、API 与边界

支架保证 n 是 0 到 100 的整数。70 是比较边界，0 和 100 是合法范围边界；69 与 70 应输出不同结果。判断表达式后需冒号，分支体保持缩进。

## 常见错误与实践建议

写成 > 70 会错过恰好及格的成绩；没有 else 会让未通过成绩没有输出。不要把 0 当成空值或用多个无关 if 导致重复输出。
