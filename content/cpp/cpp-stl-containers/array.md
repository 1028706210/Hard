---
id: cpp-stl-containers-array
title: C++ <array>
concepts: [arrays]
objectives:
  - 会声明定长 std::array 并用下标与 size() 访问。
  - 理解定长数组与 vector 的取舍。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-array.html
source_snapshot_date: 2026-08-23
---

# C++ <array>

## 概念定义与适用场景

`std::array<T, N>` 是长度在编译期固定的容器，包装原生数组并补上容器接口：size()、at()（越界抛异常）、begin/end 迭代。长度已知且不变时优先用它——无堆分配、缓存友好。

```cpp
#include <array>
#include <iostream>

std::array<int, 3> values = {1, 2, 3};
for (std::size_t i = 0; i < values.size(); i++) {
    std::cout << values[i] << " ";
}
```

## 语法、API 与边界

模板第二参数 N 必须是编译期常量，运行时才能确定的长度只能用 vector；at() 带边界检查，operator[] 不检查。std::array 支持拷贝赋值与比较运算。

```cpp
int first = values.at(0);   // 越界抛 std::out_of_range
int raw = values[0];        // 不检查
```

## 常见错误与实践建议

常见错误：把运行时变量当 N、越界下标未用 at 导致未定义行为。建议遍历用范围 for，需要防御时用 at。本课练习要求读满定长数组后逆序输出。
