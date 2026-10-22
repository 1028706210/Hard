---
id: python-flow-collections-data-structures
title: Python 数据结构
concepts: [collections, control-flow, data-structures]
objectives: [为问题选择列表字典或集合, 用组合数据结构表达简单记录]
prerequisites: [python-flow-collections-comprehensions]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python3-data-structure.html
source_snapshot_date: 2026-08-23
---

# 选择匹配问题的容器

列表强调顺序，字典强调名称，集合强调唯一成员。先说清要按位置、按键还是按成员访问，再选择容器。

```python
record = {"name": "Hard", "tags": ["python"]}
print(record["tags"][0])
```

组合容器时，命名中间值能减少嵌套访问造成的误读。

```python
groups = {"beginner": ["syntax"]}
print(groups["beginner"])
```

## 从访问方式选择结构

| 问题 | 合适起点 | 需要保留的语义 |
| --- | --- | --- |
| 按原顺序保存任务，可重复 | `list` | 位置与重复次数 |
| 一条固定位置的坐标记录 | `tuple` | 各位置的意义 |
| 按名字找到一条记录 | `dict` | 唯一键与对应值 |
| 判断是否出现过或计算交集 | `set` | 唯一成员，不依赖顺序 |
| 从尾部进出，后进先出 | 列表的 `append/pop` | 栈顺序 |
| 两端频繁进出，先进先出 | `collections.deque` | 队列顺序 |

不要为简单数据再设计一个容器类。字典与集合的常见查找平均较快，但不能理解为任何规模、任何键都固定耗时；列表按值查找通常需要逐项比较。频繁从列表头部删除会移动剩余元素，队列应采用适合的结构。

```python
from collections import deque

stack = []
stack.append("first")
stack.append("second")
print(stack.pop())
queue = deque(["first", "second"])
queue.append("third")
print(queue.popleft(), list(queue))
```

预期输出：

```text
second
first ['second', 'third']
```

## 组合结构与遍历

记录列表能表达多条独立数据，再由字典索引或集合筛选帮助访问。`enumerate` 同时提供序号和值，`zip` 按位置配对；普通 `zip` 到最短输入处结束，若业务要求等长，可在支持的 Python 版本中使用 `strict=True`（Python 3.10 起）拒绝长度不匹配。

```python
records = [{"name": "Lin", "tags": ["read", "read"]},
           {"name": "Mei", "tags": ["test"]}]
for number, record in enumerate(records, start=1):
    print(number, record["name"], len(record["tags"]))
names = [record["name"] for record in records]
counts = [len(record["tags"]) for record in records]
print(dict(zip(names, counts, strict=True)))
```

预期输出：

```text
1 Lin 2
2 Mei 1
{'Lin': 2, 'Mei': 1}
```

这里保留两次 `read`，因为它们可能代表两次记录；只有业务确实只关心成员是否存在时才去重。`dict(zip(...))` 遇到重复名字会覆盖旧值，因此真实记录若允许同名，应使用稳定唯一标识或把每个名字映射到一个列表。组合容器不会自动验证嵌套字段，仍需在数据入口检查结构。

技术参考：[官方数据结构与遍历技巧](https://docs.python.org/3.14/tutorial/datastructures.html)、[deque](https://docs.python.org/3.14/library/collections.html#collections.deque)。现有分组练习仍只读取 `beginner` 下的课程列表；队列和记录索引不属于自动判题范围。

## 概念定义与适用场景

外层字典负责按组名查找，内层列表负责保存有顺序的课程名称。先取 groups 中的 beginner，再处理列表，能让每一步操作的对象类型保持清楚。

## 语法、API 与边界

本题支架读取 JSON 并验证所有组都为字符串列表。缺少 beginner 与 beginner 为空列表都会得到数量零；列表中的空字符串仍是一个元素，会输出一个空行。

## 常见错误与实践建议

不要把字典的键数量误当作课程数量，也不要把列表改为集合而丢失顺序或重复项。使用多个组和重复课程可以检查是否读取了正确的层级。
