---
id: cpp-foundations-environment
title: C++ 环境设置
concepts: [tooling]
objectives:
  - 理解 C++ 从源代码到可执行程序的编译链接过程。
  - 掌握验证编译器版本的基本方法。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-environment-setup.html
source_snapshot_date: 2026-08-23
---

# C++ 环境设置

## 概念定义与适用场景

C++ 是编译型语言：源文件先由编译器翻译为目标代码，再由链接器组合成可执行文件。常见的工具链包括 GCC（g++）、Clang 和 MSVC，本课程使用固定版本的 g++ 并按 C++20 标准编译。

```cpp
#include <iostream>

int main() {
    std::cout << "environment ready" << std::endl;
    return 0;
}
```

## 语法、API 与边界

在命令行执行 `g++ --version` 可以查看编译器版本；版本决定默认支持的语言标准。旧编译器可能无法编译 C++20 特性，因此项目常显式指定 `-std=c++20`。

```cpp
const int required_major = 20;
std::cout << "standard: c++" << required_major << std::endl;
```

## 常见错误与实践建议

遇到"找不到编译器"或"语法不识别"时，先确认工具链安装与版本，再检查语言标准参数。本课程练习环境已固定编译器，不需要自行安装任何工具。
