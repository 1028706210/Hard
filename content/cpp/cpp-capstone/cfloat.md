---
id: cpp-capstone-cfloat
title: C++ <cfloat>
concepts: [types]
objectives:
  - 会用 DBL_EPSILON 做浮点相等比较。
  - 理解浮点直接 == 比较的舍入误差陷阱。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-cfloat.html
source_snapshot_date: 2026-08-23
---

# C++ <cfloat>

## 概念定义与适用场景

`<cfloat>` 定义 FLT_EPSILON、DBL_EPSILON、DBL_MAX 等浮点边界常量。判断近似计算结果是否足够接近，需要按数据量级和误差合同选择容差；直接 == 比较的是已存储的浮点值是否相等，也有精确比较的适用场景。不能把固定 epsilon 倍数当作所有 double 数据的通用相等规则。

```cpp
#include <cmath>
#include <cfloat>
#include <iostream>

double left = 0.1 + 0.2;
double right = 0.3;
bool same = std::fabs(left - right) <= DBL_EPSILON * 10;
std::cout << same << std::endl;   // 视舍入与容差而定
```

## 语法、API 与边界

DBL_EPSILON 是 1 与下一个大于 1 的可表示 double 的差，本平台约为 2.22e-16，不是最小正数。数据量级跨度较大时通常需要随量级缩放的相对容差；接近零时再结合绝对容差，实际阈值由误差需求决定。对有限且差值计算可表示的数，常见形式为 |a-b| <= max(abs_tol, rel_tol * max(|a|, |b|))。本课练习特意规定固定的 DBL_EPSILON×10 绝对容差，仍按该题目合同输出 same/diff，不把通用策略替换进旧练习。

```cpp
static_assert(DBL_MAX > 1e308 * 0.9);
```

## 常见错误与实践建议

常见错误：金融/计数场景用 double 精确比较、把 epsilon 当任意小数。本课练习要求读入两个两位小数并用 DBL_EPSILON 容差判断 same/diff。
