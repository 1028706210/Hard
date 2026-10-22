---
id: cpp-foundations-data-types
title: C++ 数据类型
concepts: [types]
objectives:
  - 区分整数、浮点、字符与布尔等基本类型。
  - 使用 sizeof 与整除、取余运算观察类型行为。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-data-types.html
source_snapshot_date: 2026-08-23
---

# C++ 数据类型

## 概念定义与适用场景

数据类型决定变量占用的字节数、取值范围和可参与的运算。C++ 的基本类型包括 bool、char、int、long long、float、double 等，sizeof 运算符在编译期给出任一类型或对象占用的字节数，其中 sizeof(char) 恒为 1。

```cpp
int apples = 7;
double ratio = 1.5;
bool ready = true;
```

## 语法、API 与边界

两个整数相除执行整除并丢弃小数部分，% 取余数；整除与取余仅适用于整数类型。当数值可能超出 int 范围时应改用 long long，浮点比较则要容忍精度误差。

```cpp
int quotient = 7 / 2;   // 3，向零截断
int remainder = 7 % 2;  // 1
```

## 常见错误与实践建议

不要用整数类型保存需要小数的量（金额、均值），也不要对 double 使用 %；混用有符号与无符号整数参与比较时容易得到反直觉结果。本课练习固定从标准输入读取整数并用整除、取余输出可核验的结果。
