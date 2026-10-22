---
id: cpp-core-memory-date-time
title: C++ 日期 & 时间
concepts: [types]
objectives:
  - 使用 <chrono> 表示时长并做单位换算。
  - 理解 duration_cast 的显式转换语义。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-date-time.html
source_snapshot_date: 2026-08-23
---

# C++ 日期 & 时间

## 概念定义与适用场景

<chrono> 库以编译期类型安全的 duration 表示时长：std::chrono::seconds、minutes、hours 是不同周期的时间量，配合 duration_cast 在单位间显式换算，避免手写 60、3600 魔法数字。

```cpp
#include <chrono>

std::chrono::seconds total(3661);
auto hours = std::chrono::duration_cast<std::chrono::hours>(total);       // 1
auto minutes = std::chrono::duration_cast<std::chrono::minutes>(total % std::chrono::hours(1));  // 1
```

## 语法、API 与边界

duration_cast 截断小数部分（向零取整），换算前先取模可得到余量部分；count() 取出底层整数值。混用不同周期的 duration 直接赋值会编译失败，必须显式转换。

```cpp
auto secs = total % std::chrono::minutes(1);  // 1 秒
int second_value = static_cast<int>(secs.count());
```

## 常见错误与实践建议

不要手写 86400 等换算常量（可读性差且易错）；时钟相关操作注意 steady_clock 与 system_clock 的语义差别。本课练习用 <chrono> 完成秒到时分秒的换算输出。
