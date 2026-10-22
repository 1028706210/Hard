---
id: cpp-core-memory-arrays
title: C++ 数组
concepts: [arrays]
objectives:
  - 声明定长数组并用下标访问元素。
  - 用有限循环遍历数组完成累计统计。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-arrays.html
source_snapshot_date: 2026-08-23
---

# C++ 数组

## 概念定义与适用场景

数组是长度固定、元素同类型、按下标连续存储的容器，下标从 0 开始。长度必须是编译期常量，元素个数在声明后不可改变。

```cpp
int scores[5] = {1, 2, 3, 4, 5};
int first = scores[0];  // 1
```

## 语法、API 与边界

越界访问（如 5 元素数组取下标 5）不会自动报错，而是未定义行为。遍历用 for 下标循环或范围 for；sizeof(arr)/sizeof(arr[0]) 在数组作用域内可求元素个数。

```cpp
int total = 0;
for (int value : scores) {
    total += value;  // 15
}
```

## 常见错误与实践建议

不要把元素个数与最大下标混淆（n 个元素最大下标是 n-1）；数组作为参数传递时退化为指针，长度需额外传入。本课练习把输入存入定长数组后统计输出。
