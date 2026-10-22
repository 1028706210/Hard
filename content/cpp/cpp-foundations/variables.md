---
id: cpp-foundations-variables
title: C++ 变量类型
concepts: [variables]
objectives:
  - 正确声明并初始化各类型变量。
  - 理解读取未初始化局部变量是未定义行为。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-variable-types.html
source_snapshot_date: 2026-08-23
---

# C++ 变量类型

## 概念定义与适用场景

变量是带类型的命名存储位置，声明时给出类型，可在存活期内被重新赋值。局部变量在声明时不会自动清零，读取未初始化的局部变量是未定义行为，因此应当声明即初始化。

```cpp
int width = 3;
int height = 4;
int area = width * height;  // 12
```

## 语法、API 与边界

变量名是标识符，不能与关键字冲突（例如 int double = 3; 无法编译）。同类型变量可用 auto 从初始化表达式推导类型；变量类型决定能参与的运算与赋值时的转换规则。

```cpp
auto count = 42;      // 推导为 int
auto ratio = 1.5;     // 推导为 double
```

## 常见错误与实践建议

不要使用未初始化的局部变量参与计算，也不要把变量名起成关键字；声明处初始化是最低成本的防御。本课练习从标准输入读取两个整数并用变量保存中间结果后输出。
