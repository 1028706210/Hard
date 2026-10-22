---
id: cpp-stl-containers-deque
title: C++ <deque>
concepts: [collections]
objectives:
  - 会用 deque 同时在头尾追加元素。
  - 理解 deque 与 vector 在头插效率上的差异。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-deque.html
source_snapshot_date: 2026-08-23
---

# C++ <deque>

## 概念定义与适用场景

`std::deque<T>`（双端队列）支持两端 O(1) 追加：push_back 与 push_front 都高效，中间插入仍是 O(n)。需要频繁头插尾插（如滑动窗口、任务队列）时用它替代 vector。

```cpp
#include <deque>
#include <iostream>

std::deque<int> values;
values.push_back(1);    // [1]
values.push_front(2);   // [2, 1]
```

## 语法、API 与边界

deque 内存分段连续（不是一整块），随机访问略慢于 vector 但仍是 O(1)；头尾插入不会像 vector 扩容那样搬移全部元素。支持下标、front/back 与迭代器全套接口。

```cpp
std::cout << values.front() << " " << values.back() << std::endl;  // 2 1
```

## 常见错误与实践建议

常见错误：把 deque 当 stack 用时混淆 front/back 语义、期望 &v[0] 连续内存传给 C API。需要连续缓冲就选 vector。本课练习要求奇偶分端插入后顺序输出。
