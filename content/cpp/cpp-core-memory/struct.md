---
id: cpp-core-memory-struct
title: C++ 结构体
concepts: [structs]
objectives:
  - 定义结构体聚合多个字段并完成成员访问。
  - 用结构体作函数参数组织相关数据。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-struct.html
source_snapshot_date: 2026-08-23
---

# C++ 结构体

## 概念定义与适用场景

struct 把多个相关字段聚合为一个自定义类型，用点号访问成员，适合组织坐标、记录等轻量数据。C++ 的 struct 与 class 仅默认访问权限不同（struct 默认公开）。

```cpp
struct Point {
    int x;
    int y;
};

Point origin{0, 0};
int px = origin.x;  // 0
```

## 语法、API 与边界

结构体可整体赋值（逐成员复制）、可作为函数参数按值或按引用传递；定义在函数外可复用，花括号初始化按声明顺序绑定字段。

```cpp
int manhattan(const Point& a, const Point& b) {
    return std::abs(a.x - b.x) + std::abs(a.y - b.y);
}
```

## 常见错误与实践建议

不要用平行数组模拟相关字段（应聚合成 struct）；字段较多时按 const 引用传递避免复制开销。本课练习要求用 struct 组织输入数据完成计算。
