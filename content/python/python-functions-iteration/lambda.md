---
id: python-functions-iteration-lambda
title: Python lambda
concepts: [functions, collections]
objectives: [使用 lambda 表达单个简单表达式, 在复杂逻辑中选择具名函数]
prerequisites: [python-functions-iteration-functions]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python-lambda.html
source_snapshot_date: 2026-08-23
---

# 简短函数表达式

`lambda` 适合只有一个表达式的小转换。若需要多步逻辑、注释或单元测试入口，应使用 `def` 写出具名函数。

```python
double = lambda value: value * 2
print(double(3))
```

它常与排序等接收回调的 API 配合。

```python
items = ["bbb", "a"]
print(sorted(items, key=lambda item: len(item)))
```

## 概念定义与适用场景

lambda 创建一个以单个表达式为函数体的函数对象，表达式的结果就是返回值。参数 value 是本次调用的输入，不应从外层偷取某个固定示例数。

## 语法、API 与边界

double(n) 才会执行表达式；只打印 double 会显示函数对象而不是数值。lambda 不能放多条语句，需要分支、日志或较长解释时优先使用 def。

## 常见错误与实践建议

乘以二不同于平方，负数可以清楚揭示混淆。不要把 n 转成字符串后重复两次；int 解析必须保留，空输入也不能伪造结果零。
