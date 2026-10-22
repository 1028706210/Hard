---
id: cpp-stl-containers-queue
title: C++ <queue>
concepts: [data-structures]
objectives:
  - 会用 queue 的 push/pop/front 三件套。
  - 理解 FIFO 顺序与出队次数的边界。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-queue.html
source_snapshot_date: 2026-08-23
---

# C++ <queue>

## 概念定义与适用场景

`std::queue<T>` 是先进先出（FIFO）适配器：push 入队（尾部）、front 看队首、pop 出队（队首）。适合排队处理、广度优先等保持到达顺序的场景。

```cpp
#include <iostream>
#include <queue>

std::queue<int> waiting;
waiting.push(10);
waiting.push(20);
waiting.push(30);
waiting.pop();              // 10 出队
int head = waiting.front(); // 20
```

## 语法、API 与边界

pop() 从队首删除、新元素从队尾进入，两端语义与 stack 相反；空队 front/pop 是未定义行为。出队次数超过元素个数必须先判 empty()。

```cpp
if (!waiting.empty()) {
    waiting.pop();
}
```

## 常见错误与实践建议

常见错误：把 queue 的 front 当成最新元素（那是 back()）、出队循环不检查空。模拟排队时先算清楚出队次数与剩余量的关系。本课练习要求出队 k 次后输出队首。
