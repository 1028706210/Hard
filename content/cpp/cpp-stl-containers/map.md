---
id: cpp-stl-containers-map
title: C++ <map>
concepts: [collections]
objectives:
  - 会用 map 的 operator[] 统计词频。
  - 理解 map 按 key 有序遍历的特性。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-map.html
source_snapshot_date: 2026-08-23
---

# C++ <map>

## 概念定义与适用场景

`std::map<K, V>` 是有序键值表（红黑树）：key 唯一且按序排列，`m[key]` 不存在时自动插入默认值，常用于计数。遍历得到按 key 升序的 (key, value) 对。

```cpp
#include <iostream>
#include <map>
#include <string>

std::map<std::string, int> counts;
counts["to"]++;    // 不存在则插入 0 再自增
counts["to"]++;    // 变为 2
```

## 语法、API 与边界

`operator[]` 对不存在的 key 有副作用（插入默认值），只查询时应使用 count 或 find；key 类型必须可比较（默认 `<`）。at(key) 越界会抛 out_of_range，`[]` 则插入。

```cpp
for (const auto& entry : counts) {
    std::cout << entry.first << " " << entry.second << std::endl;
}
```

## 常见错误与实践建议

常见错误：用 `[]` 判断存在反而插入了空键、期待遍历保持插入顺序。输出按 key 排序是 map 的天然合同。本课练习要求词频统计后按字典序输出。
