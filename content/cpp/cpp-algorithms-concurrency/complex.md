---
id: cpp-algorithms-concurrency-complex
title: C++ <complex>
concepts: [types]
objectives:
  - 会构造 std::complex 并读取实部虚部。
  - 会用 std::abs 求复数模长。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-complex.html
source_snapshot_date: 2026-08-23
---

# C++ <complex>

## 概念定义与适用场景

`std::complex<double>` 表示复数：构造时给实部与虚部，real()/imag() 分别读取。支持 +、-、*、/ 四则与共轭、模长（std::abs）等运算，适合几何向量与信号处理中的复数计算。

```cpp
#include <complex>
#include <iostream>

std::complex<double> point(3.0, 4.0);
double magnitude = std::abs(point);  // 5.0
```

## 语法、API 与边界

abs 对复数返回模长 sqrt(re²+im²)；norm 返回模长平方。比较相等用 == 时按实部虚部逐一比较，浮点误差场景应自行设容差。

```cpp
std::complex<double> sum = point + std::complex<double>(1.0, 0.0);
std::cout << sum.real() << " " << sum.imag() << std::endl;  // 4 4
```

## 常见错误与实践建议

常见错误：把 abs 当成只取实部、浮点直接比较相等。输出定点小数时配合 `<iomanip>` 的 fixed/setprecision。本课练习要求输出复数模长（两位小数）。
