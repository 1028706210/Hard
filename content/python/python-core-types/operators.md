---
id: python-core-types-operators
title: Python 运算符
concepts: [operators, types]
objectives:
  - 使用算术与比较运算符构造确定的表达式。
  - 区分赋值符号与相等比较符号。
prerequisites: [python-core-types-data-types]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-basic-operators.html
source_snapshot_date: 2026-08-23
---

# 用表达式得到新结果

算术运算符从数字得到新数字，比较运算符得到布尔值。`=` 用于把结果绑定给名称，`==` 用于判断两个值是否相等；把两者分开思考能避免常见错误。

```python
remaining = 10 - 3
print(remaining)
```

比较结果可以直接保存，也可以交给条件语句使用。

```python
passed = 82 >= 70
print(passed)
```

## 概念定义与适用场景

严格大于使用 >，相等时结果是 False。比较产生一个布尔值，print 会输出 True 或 False；赋值符号 = 不进行比较。

## 语法、API 与边界

本题的输入是恰好两个整数，可以有负号或为零。起始代码提供整数解析和失败退出；比较应使用转换后的整数，不能直接比较文本。

## 常见错误与实践建议

>= 会把相等情况错误地当作通过；字符串比较则可能把 "10" 排在 "2" 前面。用相等、负数和 10 与 2 的组合检查，可以区分这些错误。
