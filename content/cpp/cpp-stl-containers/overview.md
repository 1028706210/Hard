---
id: cpp-stl-containers-overview
title: C++ STL 总览
concepts: [collections]
objectives:
  - 说出 STL 由容器、迭代器与算法三部分组成。
  - 会组合容器与算法完成求和类任务。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-stl-tutorial.html
source_snapshot_date: 2026-08-23
---

# C++ STL 总览

## 概念定义与适用场景

标准模板库（STL）是 C++ 标准库的核心部分，由三类组件构成：容器（vector、map 等存储数据）、迭代器（连接容器与算法的游标）和算法（sort、accumulate 等通用操作）。三者通过模板协作，让「存储」与「处理」解耦。

```cpp
#include <numeric>
#include <vector>

std::vector<int> values = {1, 2, 3};
int total = std::accumulate(values.begin(), values.end(), 0);
```

## 语法、API 与边界

算法通过迭代器区间 `[begin, end)` 操作容器，不关心具体容器类型；accumulate 定义在 `<numeric>`，初值类型决定累加类型（用 0LL 可避免 int 溢出）。容器是值语义：拷贝容器会拷贝全部元素。

```cpp
int total = std::accumulate(values.begin(), values.end(), 0);
long long wide = std::accumulate(values.begin(), values.end(), 0LL);
```

## 常见错误与实践建议

常见错误：区间写反（end 在前）、对空区间传入错误初值类型。建议优先用成员函数 begin/end 与范围 for；需要数值累积时显式给足初值宽度。本课练习要求用 accumulate 求整数和。
