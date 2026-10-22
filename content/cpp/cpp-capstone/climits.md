---
id: cpp-capstone-climits
title: C++ <climits>
concepts: [types]
objectives:
  - 会用 INT_MAX/INT_MIN 等宏识别整数边界值。
  - 理解边界宏在防溢出检查中的作用。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-climits.html
source_snapshot_date: 2026-08-23
---

# C++ <climits>

## 概念定义与适用场景

`<climits>` 定义 CHAR_BIT、INT_MAX、INT_MIN、LLONG_MAX 等整数边界宏。它们是写「值是否恰好等于 int 边界」这类判断的唯一直观方式。

```cpp
#include <climits>
#include <iostream>

int edge = INT_MAX;
std::cout << (edge == 2147483647) << std::endl;   // 1
```

## 语法、API 与边界

宏值由实现决定但下界由标准保证（int 至少 16 位、本平台 32 位）。与定宽类型并用时注意 CHAR_BIT 是字节数位宽（通常 8）。

```cpp
static_assert(INT_MIN < 0 && INT_MAX > 0);
static_assert(CHAR_BIT == 8);
```

## 常见错误与实践建议

常见错误：手写 2147483648 当 INT_MAX（实际是 INT_MAX+1 会回绕）、用 int 检查 int 边界溢出。本课练习要求统计输入中等于 INT_MAX/INT_MIN 的元素个数。
