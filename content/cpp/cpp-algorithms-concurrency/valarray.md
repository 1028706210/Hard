---
id: cpp-algorithms-concurrency-valarray
title: C++ <valarray>
concepts: [arrays]
objectives:
  - 会构造 std::valarray 并做整体算术。
  - 会用 valarray 的 sum/size 聚合。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-valarray.html
source_snapshot_date: 2026-08-23
---

# C++ <valarray>

## 概念定义与适用场景

`std::valarray<double>` 是面向数值计算的数组：一个表达式作用到全部元素（整体乘、加），并提供 sum、min、max 等聚合。科学计算里比 vector 更直接的「向量运算」表达。

```cpp
#include <valarray>

std::valarray<int> values = {1, 2, 3};
std::valarray<int> doubled = values * 2;   // {2, 4, 6}
int total = doubled.sum();                 // 12
```

## 语法、API 与边界

整体运算生成新 valarray（或原地修改），不与 STL 迭代器体系互通（没有 begin/end 成员直到 C++11 才有自由函数）；元素个数由构造决定，越界下标未定义。slice 可做矩阵行/列视图。

```cpp
values += 1;            // 每个元素加 1
int count = static_cast<int>(values.size());
```

## 常见错误与实践建议

常见错误：把它当通用容器混用 STL 算法、期待惰性求值（中间结果会物化）。通用编程用 vector，纯数值批量运算才用 valarray。本课练习要求整体翻倍后求和。
