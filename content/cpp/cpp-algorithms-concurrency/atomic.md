---
id: cpp-algorithms-concurrency-atomic
title: C++ <atomic>
concepts: [concurrency]
objectives:
  - 会用 std::atomic 与 fetch_add 做原子计数。
  - 理解 atomic 只保证单变量单操作的原子性。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-atomic.html
source_snapshot_date: 2026-08-23
---

# C++ <atomic>

## 概念定义与适用场景

`<atomic>` 让单变量的读写变成不可分割的原子操作：多线程并发 fetch_add 不会丢更新，无需互斥量。适合计数器、标志位等轻量共享状态。

这里的“无需互斥量”指调用者不必另加锁来保护这一次原子操作；std::atomic 不保证所有类型与实现都无锁，其内部可能使用锁。可用对象的 is_lock_free() 或 C++17 的 is_always_lock_free 查询相应保证。本课所谓“无锁计数”应理解为使用原子计数接口，不能据此推断实现一定无锁。

```cpp
#include <atomic>

std::atomic<long long> counter{0};
counter.fetch_add(1);      // 原子加，返回旧值
counter++;                 // 等价于 fetch_add(1)
bool positive = counter.load() > 0;
```

## 语法、API 与边界

fetch_add 返回加之前的旧值；load/store 是显式原子读写；compare_exchange_strong 做「等于期望值才替换」的原子更新。atomic 不保证多条语句组成的区间一致，复杂不变量仍需互斥量。整型 atomic 上的 ++/-- 与复合赋值都是原子的。

```cpp
std::atomic<int> state{0};
int expected = 0;
if (state.compare_exchange_strong(expected, 1)) {
    // 只有把 state 从 0 改成 1 成功的线程进入
}
```

## 常见错误与实践建议

常见错误：以为 atomic 能保护多语句临界区、无必要地调低内存序。默认顺序一致性最稳妥，先写对再谈优化。本课练习要求双线程对同一 atomic 累加，join 后输出确定总和。
