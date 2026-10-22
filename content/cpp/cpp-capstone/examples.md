---
id: cpp-capstone-examples
title: C++ 实例：从需求到可验证程序
concepts: [functions, collections]
objectives:
  - 会把一句话需求拆成输入、处理、输出三段可测结构。
  - 会用 vector 与 algorithm 一次完成 sum/max/min 汇总。
prerequisites: []
difficulty: advanced
experience_points: 35
source_url: https://www.runoob.com/cplusplus/cpp-examples.html
source_snapshot_date: 2026-08-23
---

# C++ 实例：从需求到可验证程序

## 概念定义与适用场景

实例题的价值在于示范「需求 → 合同 → 程序」：先约定输入范围与输出格式，再用最直接的 STL 组合实现。求和、最值、计数这类汇总需求，vector 存数 + algorithm 一行完成。

```cpp
#include <algorithm>
#include <iostream>
#include <vector>

std::vector<int> values{3, 1, 4};
std::cout << *std::min_element(values.begin(), values.end()) << std::endl;   // 1
```

## 语法、API 与边界

min_element/max_element 返回迭代器；合法空区间会返回 last（容器区间中就是 end()），查询本身不是未定义行为。解引用尾后迭代器才违反边界，因此取最值前应检查返回值不等于 end()。accumulate 在 `<numeric>`，初值类型决定求和类型。

```cpp
#include <numeric>
long long total = std::accumulate(values.begin(), values.end(), 0LL);
```

## 常见错误与实践建议

常见错误：不约定空输入行为、max_element 解引用前不检查。实例代码先写清范围合同再实现，练习要求一次输出 sum/max/min 三项汇总。
