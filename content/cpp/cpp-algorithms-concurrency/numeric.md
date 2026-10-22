---
id: cpp-algorithms-concurrency-numeric
title: C++ <numeric>
concepts: [operators]
objectives:
  - 会用 std::partial_sum 生成前缀和序列。
  - 知道 numeric 头与 algorithm 头的分工。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-numeric.html
source_snapshot_date: 2026-08-23
---

# C++ <numeric>

## 概念定义与适用场景

`<numeric>` 收纳数值算法：accumulate 求和、partial_sum 前缀和、iota 生成递增序列、inner_product 内积。它们与 `<algorithm>` 的区别在于都围绕「数值聚合」。

```cpp
#include <numeric>
#include <vector>

std::vector<int> values = {1, 2, 3};
std::vector<int> prefix;
std::partial_sum(values.begin(), values.end(), std::back_inserter(prefix));
// prefix = {1, 3, 6}
```

## 语法、API 与边界

partial_sum 每个位置写「从头到当前位置的累计值」，输出容器要能容纳 n 个元素（back_inserter 自动扩张）；iota 以初始值起步逐个 ++ 填充。初值类型决定累计宽度，求大和用 0LL。

```cpp
std::vector<int> indexes(4);
std::iota(indexes.begin(), indexes.end(), 0);  // 0 1 2 3
```

## 常见错误与实践建议

常见错误：partial_sum 输出到定长容器忘了留空间、accumulate 初值给 int 导致溢出。前缀和数组常配合二分做区间和查询。本课练习要求输出前缀和序列。
