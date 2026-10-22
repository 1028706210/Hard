---
id: cpp-algorithms-concurrency-algorithm
title: C++ <algorithm>
concepts: [collections]
objectives:
  - 会用 std::sort 对区间排序并取有序中位元素。
  - 会用 min_element/max_element 类标准算法替代手写循环。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-algorithm.html
source_snapshot_date: 2026-08-23
---

# C++ <algorithm>

## 概念定义与适用场景

`<algorithm>` 提供作用于迭代器区间的通用算法：sort 排序、find 查找、count 计数、min_element/max_element 求最值。算法不绑定容器，任何提供合适迭代器的序列都能用。

```cpp
#include <algorithm>
#include <vector>

std::vector<int> values = {3, 1, 4, 2, 5};
std::sort(values.begin(), values.end());   // 升序
int middle = values[values.size() / 2];    // 有序后取中位
```

## 语法、API 与边界

sort 默认升序，传 greater<int>() 得降序；区间是 `[first, last)` 左闭右开。对空区间调用 min_element 返回 last（等于 end），解引用前必须判空。

```cpp
auto smallest = std::min_element(values.begin(), values.end());
if (smallest != values.end()) {
    int value = *smallest;
}
```

## 常见错误与实践建议

常见错误：忘记 sort 后才取「第 k 大」、对返回 end 的 min_element 解引用。等长比较用 minmax 一次拿两个最值。本课练习要求排序后输出中位元素。
