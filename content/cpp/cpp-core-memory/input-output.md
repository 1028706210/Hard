---
id: cpp-core-memory-input-output
title: C++ 基本的输入输出
concepts: [io]
objectives:
  - 使用 cin/cout 完成多值读取与格式化输出。
  - 使用 <iomanip> 的 setw 控制对齐宽度。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-basic-input-output.html
source_snapshot_date: 2026-08-23
---

# C++ 基本的输入输出

## 概念定义与适用场景

标准库 <iostream> 提供 std::cin（标准输入）与 std::cout（标准输出），>> 按空白分隔读取、<< 串联输出，是控制台程序交互的基础。

```cpp
int value = 0;
std::cin >> value;
std::cout << "read:" << value << std::endl;
```

## 语法、API 与边界

<iomanip> 的 std::setw(w) 设置下一字段的最小宽度，默认右对齐、空格填充；连续读取多个值时 >> 自动跳过空白。读取失败（类型不符）后流进入失败态，后续读取全部失效。

```cpp
#include <iomanip>

std::cout << std::setw(5) << 42;  // "   42"
```

## 常见错误与实践建议

不要忽略读取失败态（可用 if (std::cin >> x) 检查）；setw 只作用于紧随其后的一个字段，重复使用才持续生效。本课练习要求用 setw 完成定宽输出。
