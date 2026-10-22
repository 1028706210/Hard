---
id: python-stdlib-data-regex-basics
title: Python 正则表达式基础
concepts: [strings, functions]
objectives: [使用 re 匹配简单文本模式, 避免把复杂正则隐藏在未命名字符串中]
prerequisites: [python-stdlib-data-overview]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python3-reg-expressions.html
source_snapshot_date: 2026-08-23
---

# 用模式描述文本形状

正则表达式适合固定格式的文本检查。把模式写成原始字符串，并为复杂规则补充样例，避免把业务含义埋进难读的符号组合。

```python
import re
print(bool(re.fullmatch(r"[0-9]+", "42")))
```

匹配失败是正常结果，应由调用方决定如何提示或恢复。

```python
import re
print(re.findall(r"[A-Z]", "Hard API"))
```

## 概念定义与适用场景

正则表达式描述文本形状，不是数值大小判断。[0-9]+ 可以保留 007 的表示，而转成整数会丢失这项信息。

## 语法、API 与边界

fullmatch 从头到尾验证，+ 使空串不匹配。Python 的 \d 与 isdigit 涵盖一些 Unicode 数字，本题特意限定 ASCII，因此不能直接替换规则。

## 常见错误与实践建议

负号和小数点不在数字字符集合中；False 是正常验证结果，不应抛异常。不要把空白先去掉而掩盖字段格式问题。
