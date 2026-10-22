---
id: cpp-stl-containers-unordered-map
title: C++ <unordered_map>
concepts: [collections]
objectives:
  - 会用 unordered_map 做平均 O(1) 的键值查询与计数。
  - 会配合 vector 记录首次出现顺序。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-unordered_map.html
source_snapshot_date: 2026-08-23
---

# C++ <unordered_map>

## 概念定义与适用场景

`std::unordered_map<K, V>` 是哈希键值表：按 key 的哈希存放，查找/更新平均 O(1)。计数场景比 map 快，但遍历无序；需要「按首次出现顺序输出」时要另配一个顺序容器记录。

```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>

std::unordered_map<std::string, int> counts;
std::vector<std::string> order;          // 记录首次出现
counts["a"]++;
order.push_back("a");
```

## 语法、API 与边界

`um[key]` 同样会对不存在的 key 插入默认值；只读判断用 count/find。最坏情况（哈希冲突）退化为 O(n)，key 需可哈希（标准类型自带，自定义类型要提供 hash）。

```cpp
for (const std::string& key : order) {
    std::cout << key << " " << counts[key] << std::endl;
}
```

## 常见错误与实践建议

常见错误：依赖遍历顺序、重复 push_back 导致顺序表重复（先判 count 再记录）。高频计数优先 unordered_map，输出顺序交给辅助容器。本课练习要求按首次出现顺序输出词频。
