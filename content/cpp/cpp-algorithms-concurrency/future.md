---
id: cpp-algorithms-concurrency-future
title: C++ <future>
concepts: [concurrency]
objectives:
  - 会用 std::async 启动任务并用 future::get 取回返回值。
  - 理解 get() 只能调用一次、异常经 future 传播。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-future.html
source_snapshot_date: 2026-08-23
---

# C++ <future>

## 概念定义与适用场景

`<future>` 把「异步计算的结果」封装成值：std::async 启动任务并返回 std::future，get() 阻塞取回返回值；std::promise 可手动设值配 future。线程里抛出的异常会存进 future，在 get() 时重新抛出。

```cpp
#include <future>

std::future<long long> task = std::async(std::launch::async, [] {
    long long total = 0;
    for (int i = 1; i <= 10; i++) total += i;
    return total;
});
long long result = task.get();   // 55
```

## 语法、API 与边界

std::future 的 get() 只能调用一次，之后 valid() 为 false、再调用是未定义行为；不指定 std::launch::async 时任务可能延迟到 get() 才执行。promise::set_value 为共享状态设置结果；该状态已有值或异常时再次设置，会抛出 std::future_error，错误条件为 std::future_errc::promise_already_satisfied。

```cpp
std::promise<int> handoff;
std::future<int> slot = handoff.get_future();
handoff.set_value(42);
int value = slot.get();
```

## 常见错误与实践建议

常见错误：丢弃 async 返回的 future 导致任务被迫同步执行、对同一 future 两次 get。简单并行取回结果用 async + get 最省事。本课练习要求 async 求和、get 后输出。
