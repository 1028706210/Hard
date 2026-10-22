---
id: cpp-foundations-constants
title: C++ 常量与字面量
concepts: [types]
objectives:
  - 使用 const 与 constexpr 定义不可修改的命名常量。
  - 区分整型、浮点、字符与字符串字面量。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-constants-literals.html
source_snapshot_date: 2026-08-23
---

# C++ 常量与字面量

## 概念定义与适用场景

常量是初始化后不可再赋值的命名值，用 const 声明；constexpr 进一步要求初始化能在编译期完成，适合用作数组长度等编译期上下文。字面量是直接写在代码中的值，如 42、1.5、'c'、"text"。

```cpp
const double tax_rate = 0.25;
constexpr int factor = 3;
int scaled = factor * 14;
```

## 语法、API 与边界

const 常量拥有类型并参与作用域与类型检查，比 #define 宏更安全；对 const 常量的赋值会在编译期报错。整数字面量默认为 int，过大时需要后缀（如 LL）提升为 long long。

```cpp
const int limit = 100;
// limit = 200;  // 编译错误：常量不可赋值
long long big = 6000000000LL;
```

## 常见错误与实践建议

不要用 #define 定义带类型的常量（无类型检查、不受作用域约束）；魔法数字应提炼为命名常量，使修改点唯一。本课练习要求用 constexpr 定义乘数常量完成计算。
