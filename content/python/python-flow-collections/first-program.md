---
id: python-flow-collections-first-program
title: Python 编程第一步
concepts: [variables, control-flow]
objectives: [把问题拆成输入处理输出步骤, 用小程序验证一个明确结果]
prerequisites: [python-flow-collections-loops]
difficulty: beginner
experience_points: 25
source_url: https://www.runoob.com/python3/python3-step1.html
source_snapshot_date: 2026-08-23
---

# 先做一个能观察的程序

程序练习应从可观察的输入、处理和输出开始。把目标写成一个小例子，先验证结果，再增加分支或数据量。

```python
name = "Hard"
print(name.upper())
```

每次只引入一个新概念，错误出现时就能快速回到最后一个有效版本。

```python
items = [1, 2]
print(len(items))
```

## 概念定义与适用场景

把程序拆成读取、变换和输出，才能分辨错误在哪一步。upper 返回一个新字符串，不会原地改变 name，因此要输出返回值或把返回值重新赋给变量。

## 语法、API 与边界

去掉首尾空白后才检查名称是否为空；内部空格保留。大小写变换采用 Python 字符串 upper 的行为，没有大写形式的字符不会凭空消失。

## 常见错误与实践建议

写出 name.upper() 却仍打印旧的 name，结果不会改变；lower 则方向相反。用中英文混合文本与两个内部空格检查变换范围。
