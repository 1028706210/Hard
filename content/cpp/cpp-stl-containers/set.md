---
id: cpp-stl-containers-set
title: C++ <set>
concepts: [collections]
objectives:
  - 会用 set 的 insert 与 size 完成去重计数。
  - 理解 set 的有序性与唯一性约束。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-set.html
source_snapshot_date: 2026-08-23
---

# C++ <set>

## 概念定义与适用场景

`std::set<T>` 是有序不重复集合：insert 自动去重，元素按比较序（默认 `<`）排列，遍历即有序。适合去重、有序维护、成员判断（count）。

```cpp
#include <iostream>
#include <set>

std::set<int> unique_values;
unique_values.insert(1);
unique_values.insert(2);
unique_values.insert(1);   // 重复插入无效
int count = static_cast<int>(unique_values.size());  // 2
```

## 语法、API 与边界

insert 重复值不报错也不改变集合；迭代遍历得到升序序列。底层为红黑树，单次操作 O(log n)。count(x) 返回 0 或 1，可当存在性判断。

```cpp
if (unique_values.count(2) == 1) {
    std::cout << "contains 2" << std::endl;
}
```

## 常见错误与实践建议

常见错误：以为 insert 重复会报错、期待 set 保持插入顺序（那要自己配 vector 记录）。去重统计直接用 size() 最简洁。本课练习要求输出去重后的元素个数。
