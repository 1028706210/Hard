---
id: cpp-stl-containers-iomanip
title: C++ <iomanip>
concepts: [io]
objectives:
  - 会用 setw 控制输出宽度与对齐。
  - 会用 fixed 与 setprecision 固定小数位数。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-iomanip.html
source_snapshot_date: 2026-08-23
---

# C++ <iomanip>

## 概念定义与适用场景

`<iomanip>` 提供流操控符：setw 设置下一次输出的最小宽度（默认右对齐，左侧补空格），fixed 配合 setprecision(n) 固定 n 位小数。它们让控制台输出可按列对齐。

```cpp
#include <iomanip>
#include <iostream>

double pi = 3.14159;
std::cout << std::setw(8) << std::fixed << std::setprecision(2) << pi << std::endl;
// 输出：    3.14（宽度 8，右对齐）
```

## 语法、API 与边界

setw 只对紧随其后的一个输出生效，之后恢复默认；fixed/setprecision 是粘性的，设置后一直有效直到再次更改。宽度不足时输出自动扩展，不会截断。

```cpp
std::cout << std::setw(4) << 7 << std::endl;    // "   7"
std::cout << std::setw(2) << 12345 << std::endl; // "12345"（不够宽不截断）
```

## 常见错误与实践建议

常见错误：以为 setw 是粘性的导致后续列错位、fixed 忘记配对 setprecision 输出位数不符。建议每列显式写操控符。本课练习要求按宽度输出定小数。
