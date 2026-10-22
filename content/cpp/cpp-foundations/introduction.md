---
id: cpp-foundations-introduction
title: C++ 简介
concepts: [tooling]
objectives:
  - 了解 C++ 的历史与主要编程范式。
  - 能够编写并运行最小的 C++ 程序。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-intro.html
source_snapshot_date: 2026-08-23
---

# C++ 简介

## 概念定义与适用场景

C++ 由 Bjarne Stroustrup 在 C 语言基础上发展而来，保留了接近硬件的性能，同时加入了类、模板、异常和标准库等抽象能力。它广泛用于系统软件、游戏引擎、高频交易和嵌入式领域。

```cpp
#include <iostream>

int main() {
    std::cout << "cpp intro" << std::endl;
    return 0;
}
```

## 语法、API 与边界

每个可执行程序都从 main 函数开始；`#include <iostream>` 引入标准输入输出设施，`std::cout` 向标准输出写内容。return 0 表示程序成功结束。

```cpp
int answer = 42;
std::cout << answer << std::endl;
```

## 常见错误与实践建议

初学者常忘记包含头文件或遗漏分号；先保证程序能编译，再关心风格。C++ 兼容大量 C 语法，但应优先使用 C++ 风格的输入输出与类型设施。
