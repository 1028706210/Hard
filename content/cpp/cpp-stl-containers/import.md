---
id: cpp-stl-containers-import
title: C++ 导入标准库
concepts: [preprocessor-directives]
objectives:
  - 区分带 .h 与不带 .h、带 c 前缀的传统 C 头。
  - 会按需包含头文件而不是全量包含。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cppo-import-header-file.html
source_snapshot_date: 2026-08-23
---

# C++ 导入标准库

## 概念定义与适用场景

C++ 标准库头文件用 `#include <名字>` 导入：C++ 自身的头不带扩展名（如 `<vector>`），继承自 C 的头加 c 前缀（如 `<cmath>`、`<cstdlib>`）。导入后所有名字位于 std 命名空间，需要 std:: 前缀或 using 声明。

```cpp
#include <cmath>
#include <iostream>

int root = static_cast<int>(std::sqrt(81.0));
```

## 语法、API 与边界

`<math.h>` 是标准 C++ 支持的 C 兼容头，`<cmath>` 提供相应的数学设施，并保证相关函数声明位于 std 命名空间。兼容头与 c 前缀头的命名空间保证不同，不应依赖实现额外暴露的名字；普通 C++ 代码优先使用 `<cmath>` 与 std:: 前缀。头文件应按实际使用包含，多余包含会拖慢编译。

```cpp
double value = std::sqrt(2.0);   // cmath 的函数在 std 内
long rounded = std::lround(value);
```

## 常见错误与实践建议

常见错误：用了函数却忘包含对应头（如 sqrt 忘 `<cmath>`）、在头文件里写 using namespace std 造成污染。建议源文件中显式 std:: 前缀。本课练习要求用 `<cmath>` 的 sqrt 计算整数平方根。
