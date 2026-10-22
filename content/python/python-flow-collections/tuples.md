---
id: python-flow-collections-tuples
title: Python 元组
concepts: [collections, types]
objectives: [使用元组表示固定顺序的数据, 区分元组和列表的可变性]
prerequisites: [python-flow-collections-lists]
difficulty: beginner
experience_points: 25
source_url: https://www.runoob.com/python3/python3-tuple.html
source_snapshot_date: 2026-08-23
---

# 固定顺序的记录

元组同样按索引保存多个值，但建立后不能原地修改。对不会变化的坐标、选项或配置片段，元组能清楚表达“固定”的意图。

```python
point = (3, 4)
print(point[1])
```

单元素元组需要尾随逗号，避免与普通括号表达式混淆。

```python
single = ("only",)
print(len(single))
```

## 创建、解包与不可变边界

决定元组的是逗号而不只是括号：`(5)` 是整数，`(5,)` 是单元素元组，空元组写作 `()`。元组支持索引、切片、拼接、`count` 和 `index`，但没有列表的 `append` 或元素赋值操作。普通解包要求数量一致，星号可收集剩余元素为列表。

```python
print(type((5)).__name__, type((5,)).__name__)
x, y = (3, 4)
x, y = y, x
first, *middle, last = (1, 2, 3, 4)
print(x, y)
print(first, middle, last)
```

预期输出：

```text
int tuple
4 3
1 [2, 3] 4
```

`point += (5,)` 会创建新元组并重新绑定名称，不是修改旧元组。元组保存的是对象引用；槽位不可替换，但内部对象若可变，仍能修改。

```python
record = ("Lin", [])
record[1].append("read")
print(record)
lookup = {(3, 4): "seat"}
print(lookup[(3, 4)])
```

预期输出：

```text
('Lin', ['read'])
seat
```

元组可否作为字典键，取决于所有元素是否可哈希；`(3, 4)` 可以，含列表的 `record` 不可以，会抛出 `TypeError`。选择元组是为了表达位置固定的记录，不是获得递归只读或权限保护。

技术参考：[官方元组与序列](https://docs.python.org/3.14/tutorial/datastructures.html#tuples-and-sequences)。现有坐标练习只要求创建二元组并读取第二项，星号解包与嵌套可变对象是拓展讲解。

## 概念定义与适用场景

元组按位置组织固定记录，不能对 point[1] 重新赋值；可以读取或解包为 x、y。不可变指元组槽位本身，若槽位保存可变对象，该对象仍可能变化。

## 语法、API 与边界

二元坐标的第二项索引为 1，负数坐标并不无效。起始代码负责解析两个整数，创建元组和读取坐标由你完成。单元素元组写成 (value,)，逗号不能省。

## 常见错误与实践建议

不要把第二项误写成索引 2，也不要交换 x 和 y。用两个不相同的数测试，避免相同坐标掩盖索引错误。
