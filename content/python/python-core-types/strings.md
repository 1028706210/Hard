---
id: python-core-types-strings
title: Python 字符串
concepts: [strings, types]
objectives:
  - 使用索引、切片和格式化读取字符串信息。
  - 编写不修改原字符串的文本处理表达式。
prerequisites: [python-core-types-conversion]
difficulty: beginner
experience_points: 35
source_url: https://www.runoob.com/python3/python3-string.html
source_snapshot_date: 2026-08-23
---

# 文本是不可变的值

字符串由字符顺序组成。索引读取一个位置，切片读取一个范围；这些操作都会返回新字符串，原始文本保持不变。格式化能把多个值组合成清晰的提示。

```python
word = "Python"
print(word[0:3])
```

f-string 让变量位置明显，也避免大量手工拼接。

```python
name = "Hard"
print(f"Hello, {name}!")
```

## 概念定义与适用场景

字符串是不可变的 Unicode 文本序列，适合保存标签、消息和结构化数据的局部字段。索引从零开始，切片的右边界不包含在结果内；需要展示变量时使用 f-string，而不是依赖隐式拼接。

## 语法、API 与边界

`text[start:stop]` 会创建新字符串，`strip()` 只移除首尾空白，`split()` 与 `join()` 分别处理拆分和组合。空字符串、短于目标长度的字符串和包含非预期字符的输入都要先定义行为；切片不会抛出越界异常，但索引会。

## 常见错误与实践建议

不要把用户文本当作已验证的标识符，也不要把 `is` 用于比较字符串值。格式化日志时避免把令牌、密码等秘密串入文本；对边界输入写用例，确认函数没有靠固定输出蒙混过关。
