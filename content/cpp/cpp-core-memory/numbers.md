---
id: cpp-core-memory-numbers
title: C++ 数字
concepts: [types]
objectives:
  - 使用 <cmath> 完成绝对值、幂等常用数学运算。
  - 理解整数与浮点结果的类型差异。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-numbers.html
source_snapshot_date: 2026-08-23
---

# C++ 数字

## 概念定义与适用场景

C++ 内建 int、long long、float、double 等数字类型，标准库 <cmath> 提供绝对值、幂、开方等数学函数。整数运算精确但范围有限，double 有 15 位左右有效数字并可能产生舍入误差。

```cpp
#include <cmath>

int magnitude = std::abs(-7);        // 7
double square = std::pow(2.0, 10);   // 1024.0
```

## 语法、API 与边界

整数相除仍为整数；需要小数结果时先把操作数转为 double。std::abs 用于整数、std::fabs 用于浮点；混用类型时编译器会按常规算术转换提升。

```cpp
int raw = -12;
double ratio = static_cast<double>(raw) / 8;  // -1.5
```

## 常见错误与实践建议

不要用 == 直接比较两个 double 的计算结果，应给定误差容限；大整数累加前确认类型范围（int 约 21 亿）。本课练习用 <cmath> 函数完成可核验计算。
