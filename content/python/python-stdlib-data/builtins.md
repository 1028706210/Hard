---
id: python-stdlib-data-builtins
title: Python 内置函数
concepts: [functions, collections]
objectives: [使用 len、sum 等内置函数处理简单数据, 选择表达意图的内置函数]
prerequisites: [python-stdlib-data-date-time]
difficulty: beginner
experience_points: 25
source_url: https://www.runoob.com/python3/python3-built-in-functions.html
source_snapshot_date: 2026-08-23
---

# 优先使用清楚的内置函数

内置函数覆盖常见的长度、聚合和转换操作。使用它们能减少手写循环，但仍应明确输入类型和空集合的行为。

```python
print(len(["a", "b"]))
```

聚合结果由元素类型决定，先验证数据再计算。

```python
print(sum([1, 2, 3]))
```

## 概念定义与适用场景

len 计算容器的元素数量，同一个名称出现三次仍是三个列表项。内置函数无需导入，但应先确认输入对象的类型：字符串长度和字符串列表长度表示不同含义。

## 语法、API 与边界

split() 将连续空白作为分隔符，不产生额外空项；len([]) 是零。这里只统计文本项，不把数字样式的项自动转换，也不应用集合去重。

## 常见错误与实践建议

len(text) 得到字符数，len(set(items)) 得到不同项数量，两者都不符合本题。空输入是合法的空列表，没有必要人为制造失败标记。
