---
id: cpp-advanced-preprocessor
title: C++ 预处理器
concepts: [preprocessor-directives]
objectives:
  - 使用 #define 常量与 #include 引入头文件。
  - 用 #ifdef 控制条件编译。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-preprocessor.html
source_snapshot_date: 2026-08-23
---

# C++ 预处理器

## 概念定义与适用场景

预处理器在编译前做文本级处理：#include 展开头文件，#define 定义宏（简单常量或带参宏），#ifdef/#endif 按宏是否存在裁剪代码。它不认识 C++ 类型与作用域。

```cpp
#define STEP 5

#include "config.h"  // 引入项目内头文件

int moved = base + STEP;  // 宏在编译前被替换为 5
```

## 语法、API 与边界

带参宏是纯文本替换，参数不加括号会被优先级坑害；#define 没有类型检查，常量优先用 constexpr。条件编译用于平台差异与调试开关。

```cpp
#ifdef DEBUG_MODE
    std::cerr << "trace" << std::endl;
#endif
```

## 常见错误与实践建议

不要用宏替代内联函数或模板；#define 后不加分号（替换后会把分号带进表达式）。本课练习要求用 #define 常量参与计算。
