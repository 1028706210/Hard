---
id: cpp-capstone-numbers
title: C++ <numbers>
concepts: [operators]
objectives:
  - 会用 std::numbers::pi 等 C++20 数学常量。
  - 理解常量精度与输出格式化的配合。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-numbers.html
source_snapshot_date: 2026-08-23
---

# C++ <numbers>

## 概念定义与适用场景

C++20 `<numbers>` 内置 pi、e、sqrt2、pi_v<float> 等数学常量为 constexpr 变量模板，编译期即可用，替代手写 3.14159 拼写错误。

```cpp
#include <cstdio>
#include <numbers>

double radius = 2.0;
std::printf("%.5f\n", std::numbers::pi * radius * radius);   // 12.56637
```

## 语法、API 与边界

std::numbers::pi 是 double 精度（≈3.141592653589793）；pi_v<T> 取指定浮点类型精度。常量本身是 inline constexpr，无运行期开销。

```cpp
static_assert(std::numbers::e > 2.71 && std::numbers::e < 2.72);
```

## 常见错误与实践建议

常见错误：写 22/7 整数除法得 3、float 与 double 常量混用丢精度。本课练习要求按半径计算圆面积并保留 5 位小数输出。
