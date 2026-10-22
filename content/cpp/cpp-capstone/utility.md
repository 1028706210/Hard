---
id: cpp-capstone-utility
title: C++ <utility>
concepts: [operators]
objectives:
  - 会用 std::pair 与 std::sort 完成双键排序。
  - 理解 pair 的字典序比较规则。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-utility.html
source_snapshot_date: 2026-08-23
---

# C++ <utility>

## 概念定义与适用场景

`<utility>` 提供 pair 与 move。pair 的 operator< 是字典序：先比 first，first 相等再比 second——这正是「主键 + 次键」排序的天然实现。

```cpp
#include <algorithm>
#include <iostream>
#include <utility>
#include <vector>

std::vector<std::pair<int, int>> pairs{{2, 20}, {1, 10}, {2, 5}};
std::sort(pairs.begin(), pairs.end());
// 排序后：{1,10} {2,5} {2,20}
```

## 语法、API 与边界

make_pair(a, b) 推导类型构造；first/second 访问成员。std::move 把值转为可被「偷走」的右值引用，配合移动构造避免深拷贝，被移对象处于有效但未指定状态。

```cpp
auto slot = std::make_pair(7, 9);
```

## 常见错误与实践建议

常见错误：忘记 sort 后 pair 已按双键有序、对被 move 的对象继续读值。本课练习要求读入多组 (k, v) 并按 pair 字典序输出。
