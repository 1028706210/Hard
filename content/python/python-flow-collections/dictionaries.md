---
id: python-flow-collections-dictionaries
title: Python 字典
concepts: [collections, variables]
objectives: [用键值对保存具名信息, 通过键安全读取字典内容]
prerequisites: [python-flow-collections-tuples]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-dictionary.html
source_snapshot_date: 2026-08-23
---

# 用名字定位数据

字典将唯一键映射到值，适合记录具有字段名的信息。键的意义比位置更重要，因此读取时应使用明确的字段名称。

```python
profile = {"name": "Hard", "level": 1}
print(profile["name"])
```

`get` 可以提供缺失时的默认值，让可选字段的处理更平稳。

```python
profile = {}
print(profile.get("city", "unknown"))
```

## 键、更新与删除

字典的键必须可哈希，常用字符串、整数或所有元素都可哈希的元组；列表和字典本身不能作键。键唯一，重复写入同一键会更新值。字典保持插入顺序，但顺序不等于按键排序；覆盖原键通常不改变其位置，删除后重新插入则放到末尾。

```python
scores = {"Lin": 2, "Mei": 3}
scores["Lin"] = 4
scores.update({"Bo": 1})
print(list(scores.items()))
print(scores.pop("Mei"))
print("Lin" in scores, 4 in scores.values())
```

预期输出：

```text
[('Lin', 4), ('Mei', 3), ('Bo', 1)]
3
True True
```

`key in mapping` 检查的是键。`del mapping[key]` 和没有默认值的 `pop(key)` 在缺键时抛出 `KeyError`；`pop(key, default)` 允许缺失。`True`、`1`、`1.0` 相等且哈希相同，作为键会对应同一条记录，不适合用来区分这三种业务身份。

## 视图、遍历与默认值

`keys()`、`values()` 和 `items()` 返回动态视图，反映字典后续变化。只需要遍历键时直接遍历字典；同时使用键和值时通过 `items()` 解包。遍历时改变键的数量可能触发 `RuntimeError`，应先收集待删除键或创建新字典。

```python
counts = {}
for word in ["read", "test", "read"]:
    counts[word] = counts.get(word, 0) + 1
for word, count in counts.items():
    print(word, count)
profile = {"name": None}
print(profile.get("name", "unknown"))
print(profile.get("city", "unknown"))
```

预期输出：

```text
read 2
test 1
None
unknown
```

`get` 不插入默认项；`setdefault(key, default)` 在缺键时插入并返回该默认项。`dict.copy()` 与列表复制一样只复制外层，嵌套对象仍可能共享。需要保持重复记录时用记录列表，不能通过重复字典键保存多个独立值。

技术参考：[官方字典教程](https://docs.python.org/3.14/tutorial/datastructures.html#dictionaries)、[映射类型边界](https://docs.python.org/3.14/library/stdtypes.html#mapping-types-dict)。本课练习只检查可选名称读取；新增计数示例不是对输入 JSON 规则的修改。

## 概念定义与适用场景

字典按键而非位置查找数据。profile["name"] 在键缺失时抛出 KeyError；profile.get("name", "unknown") 只在缺失时使用默认值，不会自动替换空字符串或 None。

## 语法、API 与边界

JSON 读取支架已经给出，当前任务只练习字典读取。缺失 name 是正常情况；显式提供无效 name 是输入错误。这两种情况有不同结果，不能合并成同一个兜底。

## 常见错误与实践建议

不要以为 get 的默认值会验证字段类型；支架先验证，再读取。尝试空对象、额外字段和带内部空格的名称，确认没有错误拒绝可选字段或压缩名称。
