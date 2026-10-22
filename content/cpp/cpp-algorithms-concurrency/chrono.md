---
id: cpp-algorithms-concurrency-chrono
title: C++ <chrono>
concepts: [types]
objectives:
  - 会用 std::chrono::milliseconds 表示时长。
  - 会用 duration_cast 在单位间显式换算。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-chrono.html
source_snapshot_date: 2026-08-23
---

# C++ <chrono>

## 概念定义与适用场景

`<chrono>` 是类型化的时长与时钟库：milliseconds(1500) 表示 1500 毫秒，duration_cast<seconds> 把它换算成 1 秒（截断小数）。不同单位是不同类型，编译期阻止误混。

```cpp
#include <chrono>
#include <iostream>

std::chrono::milliseconds span(1500);
auto whole_seconds = std::chrono::duration_cast<std::chrono::seconds>(span);
std::cout << whole_seconds.count() << std::endl;   // 1
```

## 语法、API 与边界

duration_cast 转为整数表示的较粗单位时向零截断：1500ms→1s，999ms→0s，-1500ms→-1s，并非数学上的向下取整。需要 -1500ms→-2s 这样的向下取整时可用 C++17 的 chrono::floor<seconds>。整数时长从毫秒转为秒不能隐式进行，需要显式换算；具体数值仍须处于中间计算和目标表示的有效范围。steady_clock 单调适合测耗时，system_clock 对应墙上时间。

```cpp
auto begin = std::chrono::steady_clock::now();
auto spent = std::chrono::steady_clock::now() - begin;
```

## 常见错误与实践建议

常见错误：以为毫秒到秒会四舍五入（实际截断）、用 system_clock 测耗时被校时跳变干扰。测试取两端：999 与 1000。本课练习要求输出毫秒对应的整秒数。
