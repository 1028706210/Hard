---
id: python-core-types-numbers
title: Python 数字
concepts: [types, operators]
objectives:
  - 区分整数除法、真除法和取余的结果。
  - 选择可读的数值表达式完成简单计算。
prerequisites: [python-core-types-operators]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-number.html
source_snapshot_date: 2026-08-23
---

# 数字计算要说明精度

`/` 会产生浮点结果，`//` 取整除后的商，`%` 得到余数。根据业务问题选择运算符，而不是只看结果看起来是否接近。

```python
average = 7 / 2
print(average)
```

余数常用于判断周期或奇偶。变量名应说明计算的单位与含义。

```python
item_count = 7
is_odd = item_count % 2 == 1
print(is_odd)
```

## 概念定义与适用场景

取余与向下取整的商满足 a == (a // b) * b + a % b。非零余数与除数同号：-7 % 2 为 1，而 7 % -2 为 -1。它与截断除法的余数规则不能混用。

## 语法、API 与边界

练习允许两个整数为负数，也允许被除数为零。除数为零时必须先退出，不能尝试计算余数。起始代码确保恰好读取两个可解析的整数，缺少或多出一个数都属于失败输入。

## 常见错误与实践建议

不要把 % 写成 / 或 //，也不要对参与计算的数先取绝对值。用整除、负被除数、负除数分别检查，最后确认零除数不会产生输出。
