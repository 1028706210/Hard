---
id: cpp-foundations-modifiers
title: C++ 类型修饰符
concepts: [types]
objectives:
  - 理解 signed 与 unsigned 对取值范围的影响。
  - 使用 unsigned 转换观察负整数的回绕解释。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-modifier-types.html
source_snapshot_date: 2026-08-23
---

# C++ 类型修饰符

## 概念定义与适用场景

signed、unsigned 表达整数类型的符号性，short、long、long long 表达整数宽度类别；具体位数及不同类别是否同宽由实现与标准最低范围共同决定。int 可与 signed/unsigned 及 short/long/long long 组合；char 可写 signed char 或 unsigned char，不能写 short char 或 long char。long 还可与 double 组合为 long double，不能把这些关键字任意叠加。

```cpp
unsigned int distance = 4000000000u;  // 32 位无符号可容纳
long big_id = 100000L;
```

## 语法、API 与边界

普通赋值将整数转换为无符号类型时，结果按该类型范围取模：在 32 位 unsigned int 下 -1 变为 4294967295。有符号与无符号混合比较按通常算术转换选择共同类型：同等级常转为无符号；若更高等级的有符号类型能表示无符号类型的全部值，则可以把无符号一侧转为有符号。不能一概认为有符号操作数必定转成无符号；花括号初始化还可能因窄化转换被拒绝。

```cpp
int raw = -1;
unsigned int wrapped = raw;            // 4294967295
if (raw < 1u) { /* raw 被转成无符号，条件为假 */ }
```

## 常见错误与实践建议

不要对可能为负的计数、差值使用 unsigned；循环变量与容器大小比较时注意 std::size_t 是无符号类型。本课练习通过显式转换把输入整数按无符号解释后输出。
