---
id: cpp-algorithms-concurrency-thread
title: C++ <thread>
concepts: [concurrency]
objectives:
  - 会用 std::thread 启动带参数的任务并 join 取回结果。
  - 理解不 join 就析构会 terminate 的规则。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-thread.html
source_snapshot_date: 2026-08-23
---

# C++ <thread>

## 概念定义与适用场景

`<thread>` 提供线程：构造时给函数与参数即并发执行，join() 阻塞等待结束。结果通过引用参数、返回值经 future 或共享变量交回主线程。

```cpp
#include <iostream>
#include <thread>

void square(int value, long long* out) {
    *out = static_cast<long long>(value) * value;
}

long long result = 0;
std::thread worker(square, 3, &result);
worker.join();   // 不 join 就析构会 std::terminate
```

## 语法、API 与边界

构造后必须 join 或 detach 二选一；join 前线程必须 joinable。传引用参数要用 std::ref 包装，否则被拷贝。线程函数抛出的异常不会自动传播到主线程。

```cpp
int shared = 0;
std::thread setter([](int* target) { *target = 9; }, &shared);
setter.join();
```

## 常见错误与实践建议

常见错误：忘 join 导致 terminate、裸引用捕获局部变量后线程仍存活（悬垂）。简单任务可用 async 替代。本课练习要求线程算平方、主线程合并求和。
