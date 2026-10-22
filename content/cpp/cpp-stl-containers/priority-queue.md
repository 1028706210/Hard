---
id: cpp-stl-containers-priority-queue
title: C++ <priority_queue>
concepts: [data-structures]
objectives:
  - 会用 priority_queue 的 push/top/pop 维护最大堆。
  - 知道如何改比较器得到最小堆。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-priority_queue.html
source_snapshot_date: 2026-08-23
---

# C++ <priority_queue>

## 概念定义与适用场景

`std::priority_queue<T>` 是优先级队列适配器，默认为最大堆：top() 恒为当前最大值，push 后自动调整堆序。适合「每次只关心最值」的调度、Top-K 场景。

```cpp
#include <iostream>
#include <queue>

std::priority_queue<int> heap;
heap.push(5);
heap.push(9);
heap.push(3);
int largest = heap.top();  // 9
```

## 语法、API 与边界

默认模板为 `priority_queue<int, vector<int>, less<int>>`；把比较器换成 `greater<int>` 即得最小堆。pop 移除堆顶后堆自动下沉调整，取次大值就是「pop 一次再 top」。

```cpp
std::priority_queue<int, std::vector<int>, std::greater<int>> min_heap;
```

## 常见错误与实践建议

常见错误：以为 priority_queue 输出有序序列（它只保证堆顶最值）、空堆 top/pop 未定义。需要全序输出就取出到 vector 再排序。本课练习要求弹出一次后输出新的堆顶。
