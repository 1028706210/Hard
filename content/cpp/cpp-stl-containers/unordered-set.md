---
id: cpp-stl-containers-unordered-set
title: C++ <unordered_set>
concepts: [collections]
objectives:
  - 会用 unordered_set 做平均 O(1) 的成员判断。
  - 理解哈希集合不保序与最坏复杂度。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-unordered_set.html
source_snapshot_date: 2026-08-23
---

# C++ <unordered_set>

## 概念定义与适用场景

`std::unordered_set<T>` 是哈希集合：元素无序存放，insert/count 平均 O(1)，只关心「在不在」时比 set 更快。不保序、不支持范围查询。

```cpp
#include <iostream>
#include <string>
#include <unordered_set>

std::unordered_set<std::string> known = {"apple", "pear"};
if (known.count("pear")) {
    std::cout << "known" << std::endl;
}
known.insert("plum");
```

## 语法、API 与边界

count(x) 返回 0/1，find 返回迭代器；极端哈希冲突下退化为 O(n)。遍历顺序既不是插入序也不是字典序，任何依赖顺序的输出都必须另加排序。

```cpp
std::unordered_set<int> values = {3, 1, 2};
// 遍历顺序不保证是 1 2 3
```

## 常见错误与实践建议

常见错误：依赖遍历顺序做输出（结果不稳定）、对自定义类型忘记提供 hash。需要有序输出时收集到 vector 再 sort。本课练习要求对查询单词逐个输出 yes/no。
