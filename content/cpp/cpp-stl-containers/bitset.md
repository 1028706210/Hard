---
id: cpp-stl-containers-bitset
title: C++ <bitset>
concepts: [data-structures]
objectives:
  - 会用 bitset 的构造、count 与下标访问。
  - 会执行按位与/或/翻转等位运算。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-bitset.html
source_snapshot_date: 2026-08-23
---

# C++ <bitset>

## 概念定义与适用场景

`std::bitset<N>` 是定长位集合：可用整数或 0/1 字符串构造，count() 数 1 的个数，operator[] 按位读写，还支持 &、|、^、flip 等整体位运算。比手写位标志更清晰且无溢出。

```cpp
#include <bitset>
#include <iostream>

std::bitset<8> flags(std::string("10110000"));
int ones = static_cast<int>(flags.count());  // 3
flags.flip(0);   // 翻转第 0 位
```

## 语法、API 与边界

默认从字符串开头构造时，最多使用前 N 个字符确定各位，所用字符中最左侧对应最高有效位；字符串长于 N 本身不会抛异常。例如 bitset<4>(std::string("101011")) 的位模式为 1010。pos/n 指定的有效输入范围内含指定的 0/1 之外的字符时会抛 invalid_argument；指定的起始位置超出字符串长度则抛 out_of_range。bitset<N> 的 N 是编译期常量，两个不同 N 的 bitset 不能直接运算。

```cpp
std::bitset<4> a(std::string("1010"));
std::bitset<4> b(std::string("0110"));
std::bitset<4> both = a & b;   // 0010
```

## 常见错误与实践建议

常见错误：把字符串下标当位序（所用字符左侧是高位），或把长字符串的截取误认为整串存入。若题目限制长度，须主动校验，不能依靠构造函数替你拒绝长串；非法字符或起始位置也应按合同处理。需要运行期长度可考虑 vector<bool>，位数能容纳时也可用整数运算。本课练习要求统计 0/1 串中 1 的个数，继续遵循题目现有长度约定。
