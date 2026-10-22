---
id: python-flow-collections-comprehensions
title: Python 推导式
concepts: [collections, control-flow]
objectives: [用列表推导式转换一组值, 在推导式中加入简单筛选条件]
prerequisites: [python-flow-collections-first-program]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/python3/python-comprehensions.html
source_snapshot_date: 2026-08-23
---

# 把遍历写成一个表达式

推导式适合把一次遍历和一个清晰的转换放在一起。表达式过长或分支过多时，普通循环通常更容易阅读和调试。

```python
values = [1, 2, 3]
squares = [value * value for value in values]
print(squares)
```

条件位于末尾时，只保留符合规则的元素。

```python
values = [1, 2, 3, 4]
even = [value for value in values if value % 2 == 0]
print(even)
```

## 概念定义与适用场景

列表推导式的前半部分是结果表达式，for 部分决定按什么顺序取值。本题对所有元素求平方，不筛选、不去重，也不改变顺序。

## 语法、API 与边界

写成 [value * value for value in values] 会产生新列表。负数的平方为正，零的平方仍为零；空序列得到空列表。支架已经处理整数解析，输出使用普通 print(list)。

## 常见错误与实践建议

不要把平方写成乘以 2，或先按大小排序。只有明确需要过滤时才加 if；负数也是本题必须保留的输入。推导式的可读性比压缩字符数更重要。
