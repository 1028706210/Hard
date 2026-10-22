---
id: cpp-algorithms-concurrency-mutex
title: C++ <mutex>
concepts: [concurrency]
objectives:
  - 会用 std::mutex 与 lock_guard 保护共享累加。
  - 理解 RAII 解锁与死锁的成因。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-mutex.html
source_snapshot_date: 2026-08-23
---

# C++ <mutex>

## 概念定义与适用场景

`<mutex>` 提供互斥量：lock 独占、unlock 释放，保证同一时刻只有一个线程进入临界区。lock_guard 用 RAII 在作用域结束自动解锁，杜绝忘记 unlock。

```cpp
#include <mutex>
#include <thread>

std::mutex guard;
long long shared_total = 0;

void add_chunk(int begin, int end) {
    for (int i = begin; i <= end; i++) {
        std::lock_guard<std::mutex> locked(guard);
        shared_total += i;
    }
}
```

## 语法、API 与边界

不同线程对同一内存位置发生冲突访问（至少一方修改），至少一个访问非原子，且二者没有 happens-before 先后关系时，会构成数据竞争并导致未定义行为。只读共享、正确使用原子操作、访问独立内存位置或已有正确同步，不因“没有互斥锁”就自动构成竞争。两个线程以相反顺序分别持锁后等待对方的锁，可能形成死锁；可固定加锁顺序或用 std::scoped_lock 一次锁多把。unique_lock 支持中途 unlock 等额外控制，具体性能应依据实际使用测量。

```cpp
{
    std::lock_guard<std::mutex> locked(guard);
    shared_total += 1;   // 临界区尽量短
}
```

## 常见错误与实践建议

常见错误：持锁调用外部回调（死锁风险）、临界区放大拖慢并发。能分区独立计算再合并就少用锁。本课练习要求双线程持锁累加共享和。
