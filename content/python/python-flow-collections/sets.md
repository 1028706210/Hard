---
id: python-flow-collections-sets
title: Python 集合
concepts: [collections, types]
objectives: [使用集合去除重复值, 判断一个值是否属于集合]
prerequisites: [python-flow-collections-dictionaries]
difficulty: beginner
experience_points: 25
source_url: https://www.runoob.com/python3/python3-set.html
source_snapshot_date: 2026-08-23
---

# 关注成员而非顺序

集合保存不重复的元素，不承诺显示顺序。它适合表达允许值、已访问项和去重后的标签。

```python
tags = {"python", "python", "test"}
print(len(tags))
```

成员测试直接回答一个值是否已出现，无需手写循环。

```python
allowed = {"read", "write"}
print("read" in allowed)
```

## 集合运算与成员约束

集合中的元素必须可哈希，不能直接放列表或另一个可变集合。集合没有下标，不支持 `tags[0]`；需要稳定展示时显式排序，而不是依赖某次运行的输出顺序。`set("aba")` 处理的是字符，`{"aba"}` 则只有一个完整字符串元素。

```python
left, right = {1, 2, 3}, {3, 4}
print(sorted(left | right))
print(sorted(left & right))
print(sorted(left - right))
print(sorted(left ^ right))
print({1, 2} <= left, left.isdisjoint({8}))
```

预期输出：

```text
[1, 2, 3, 4]
[3]
[1, 2]
[1, 2, 4]
True True
```

`|`、`&`、`-`、`^` 分别是并、交、差和对称差，以上运算返回新集合。`<=` 表示子集，`<` 表示真子集，不是比较成员数量。差集有方向，`left - right` 与 `right - left` 不同。

## 原地更新与不可变集合

`add` 加入单个元素，`update` 加入可迭代对象里的元素。`remove` 删除不存在的值会抛出 `KeyError`，`discard` 则允许其不存在；`pop` 取走某个元素，但不保证取出哪一个。

```python
tags = {"read"}
tags.add("read")
tags.update(["test", "code"])
tags.discard("missing")
print(sorted(tags))
group = frozenset({"read", "test"})
print(group in {group})
print(len({True, 1, 1.0}))
```

预期输出：

```text
['code', 'read', 'test']
True
1
```

`frozenset` 不可变且可哈希，适合把一个成员集合当作字典键或另一集合的元素。集合依赖相等和哈希去重，布尔、整数与浮点数中某些值会相等；不能把集合当作保留原类型差异的通用去重器。若要求去重并保留首次出现顺序，可对可哈希元素使用 `list(dict.fromkeys(items))`。

技术参考：[官方集合类型](https://docs.python.org/3.14/library/stdtypes.html#set-types-set-frozenset)。现有练习仅对字符串标签计数，不增加排序输出或其他集合运算要求。

## 概念定义与适用场景

集合按相等关系去重，适合统计唯一标签或检查成员是否存在。它不保证展示顺序，所以这道题只输出数量，不比较集合的打印顺序。

## 语法、API 与边界

set(items) 创建集合，len 读取成员数，value in tags 检查成员关系。空集合应写 set()；{} 是空字典。字符串标签按大小写敏感的原文比较。

## 常见错误与实践建议

len(items) 会把重复项都算进去；把输入先转小写也会改变本题定义。空输入合法，没有理由为集合计数人为增加失败分支。
