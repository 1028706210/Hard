---
id: cpp-capstone-cstdint
title: C++ <cstdint>
concepts: [types]
objectives:
  - 会用 int64_t/uint32_t 等定宽整数表达精确范围。
  - 理解定宽类型在跨平台求和场景的必要性。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-cstdint.html
source_snapshot_date: 2026-08-23
---

# C++ <cstdint>

## 概念定义与适用场景

`<cstdint>` 定义 int64_t、uint8_t 等定宽整数：范围由类型名保证，与平台无关。涉及 10^12 级数值求和时用 int64_t 而不是 int，是避免溢出的第一选择。

```cpp
#include <cstdint>
#include <iostream>

std::int64_t total = 1000000000000;
std::int64_t delta = -500000000000;
std::cout << (total + delta) << std::endl;   // 500000000000
```

## 语法、API 与边界

INT64_MIN/INT64_MAX 给出确切边界；int64_t 读入用 std::cin 直接支持。混用有符号/无符号会触发整型提升陷阱，比较前先统一符号性。

```cpp
static_assert(INT64_MAX > 9000000000000000000LL / 2);
```

## 常见错误与实践建议

常见错误：用 int 累加大数值静默溢出、printf 用 %d 打印 int64_t。本课练习要求对 10^12 级数值求和并检查边界拒绝越界输入。
