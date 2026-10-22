---
id: python-flow-collections-lists
title: Python 列表
concepts: [collections, variables]
objectives: [创建并读取有序列表, 使用 append 增加一个元素]
prerequisites: [python-core-types-strings]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-list.html
source_snapshot_date: 2026-08-23
---

# 有序的可变序列

列表按位置保存多个值，适合需要增加、删除或更新的项目集合。索引从零开始；先检查长度再读取可避免越界。

```python
tasks = ["read", "code"]
print(tasks[0])
```

`append` 把一个值追加到末尾，修改的是同一份列表。

```python
tasks = []
tasks.append("test")
print(tasks)
```

## 索引、切片与更新

负索引从尾部读取，`values[start:stop:step]` 的结束位置不包含在结果中。直接索引超出范围会抛出 `IndexError`，切片则会截取可用部分。列表可直接给元素或切片赋值。

```python
values = [10, 20, 30, 40]
print(values[-1], values[1:3], values[::2])
values[1] = 25
values[2:4] = [35]
print(values)
```

预期输出：

```text
40 [20, 30] [10, 30]
[10, 25, 35]
```

`append(x)` 加入一个元素，`extend(iterable)` 依次加入其中元素，`insert(i, x)` 在位置前插入。`remove(x)` 删除首个相等项，不存在时抛出 `ValueError`；`pop(i)` 按位置删除并返回值，省略位置则弹出最后一项；`del values[i]` 仅删除。

```python
values = [3, 1]
values.append([8, 9])
print(values)
values.pop()
values.extend([2, 2])
values.remove(2)
print(values.pop(), values)
print(sorted(values), values)
print(values.sort(), values)
```

预期输出：

```text
[3, 1, [8, 9]]
2 [3, 1]
[1, 3] [3, 1]
None [1, 3]
```

`sort()` 原地排序并返回 `None`，`sorted()` 返回新列表；别写 `values = values.sort()`。混合不支持大小比较的类型不能直接排序。按记录字段排序可使用 `key`，无需自己写排序算法。

## 共享引用与浅复制

`other = values` 不复制列表；`values.copy()` 或 `values[:]` 只复制最外层。内部列表仍可能共享，重复嵌套列表时也要注意这一点。

```python
rows = [[0]] * 2
rows[0].append(1)
print(rows)
rows = [[0] for _ in range(2)]
copied = rows.copy()
copied[0].append(2)
print(rows, copied)
```

预期输出：

```text
[[0, 1], [0, 1]]
[[0, 2], [0]] [[0, 2], [0]]
```

需要独立嵌套结构时，应按数据结构逐层构建或在确有需求时使用深复制。遍历时删除元素容易跳过后续元素，过滤通常创建新列表更清晰。列表尾部 `append/pop` 可组成栈；频繁从头部取出应考虑 `collections.deque`。

技术参考：[官方列表方法与数据结构](https://docs.python.org/3.14/tutorial/datastructures.html#more-on-lists)。下面的现有练习仍只读取输入列表的第一项，不要求排序、删除或改变输入顺序。

## 概念定义与适用场景

列表保留顺序和重复项，索引 0 是第一项；append 修改原列表并把元素放到末尾。读取 tasks[0] 前必须确认列表非空。

## 语法、API 与边界

本题以任意空白分隔名称，不把每一行当成一个名称。支架提供 tasks，学习重点是列表索引。空列表按题面退出；单元素列表可以正常读取。

## 常见错误与实践建议

排序会改变用户输入顺序；取 tasks[-1] 则得到最后一项。用 z a 与单个 solo 检查索引，不要只试 read code。
