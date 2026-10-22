---
id: cpp-stl-containers-standard-library
title: C++ 标准库
concepts: [collections]
objectives:
  - 了解标准库按功能分头组织（容器、算法、数值、通用工具）。
  - 会用 <cstdlib> 的通用工具函数处理数值。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-standard-library.html
source_snapshot_date: 2026-08-23
---

# C++ 标准库

## 概念定义与适用场景

C++ 标准库是 STL 之外还包括输入输出、字符串、数值计算与通用工具的总称，按头文件分域提供能力：容器与算法在 STL，通用工具如 abs、exit 在 `<cstdlib>`，极限值在 `<limits>`。程序按需组合这些头即可覆盖大部分日常任务。

```cpp
#include <cstdlib>
#include <iostream>

int distance = std::abs(-7);
```

## 语法、API 与边界

`std::abs` 对 int 取绝对值（`<cstdlib>`），浮点版本在 `<cmath>`；对 INT_MIN 取绝对值会溢出，属未定义行为。`std::exit` 可立即结束进程，但会跳过局部对象析构。

```cpp
int a = 3, b = 10;
std::cout << std::abs(a - b) << std::endl;  // 7
```

## 常见错误与实践建议

常见错误：混用 C 宏（如 abs 未加 std:: 时对 double 截断）、依赖隐式包含（某头间接包含了另一头在别的实现不存在）。建议每个使用的名字都显式包含其标准头。本课练习要求用 std::abs 输出差值。
