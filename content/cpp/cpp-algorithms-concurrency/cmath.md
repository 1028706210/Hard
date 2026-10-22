---
id: cpp-algorithms-concurrency-cmath
title: C++ <cmath>
concepts: [operators]
objectives:
  - 会用 std::pow 计算幂并处理浮点结果的取整。
  - 知道 cmath 数学函数对 int 与 double 的隐式转换。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-cmath.html
source_snapshot_date: 2026-08-23
---

# C++ <cmath>

## 概念定义与适用场景

`<cmath>` 提供数学函数：pow 幂、sqrt 平方根、floor/ceil 取整、fabs 绝对值。参数与返回值以 double 为主，整数传进去会隐式转换，结果需要整数时要显式取整。

```cpp
#include <cmath>
#include <iostream>

double power = std::pow(2.0, 10.0);   // 1024.0
long long exact = std::llround(power); // 1024
```

## 语法、API 与边界

pow 返回浮点，整数幂可直接用循环乘更精确；llround 四舍五入到 long long，static_cast<int> 只截断。0 的 0 次方返回 1（IEEE 约定），负底的非整数幂返回 NaN。

```cpp
double rooted = std::sqrt(2.0);
double lower = std::floor(3.7);   // 3.0
double upper = std::ceil(3.2);    // 4.0
```

## 常见错误与实践建议

常见错误：pow 结果直接截断丢精度（如 10 的大幂）、对 NaN 做比较。整数幂用循环累乘最稳妥。本课练习要求用 pow 输出整数幂。
