---
id: cpp-advanced-threads
title: C++ 多线程
concepts: [concurrency]
objectives:
  - 启动 std::thread 并用 join 等待结束。
  - 使用 std::mutex 保护共享数据的并发修改。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-multithreading.html
source_snapshot_date: 2026-08-23
---

# C++ 多线程

## 概念定义与适用场景

std::thread 启动并发执行流：构造时传入函数与参数，join() 等待其结束（不 join 就析构会 terminate）。多线程同时修改共享数据时必须用 std::mutex 串行化临界区。

```cpp
#include <mutex>
#include <thread>

std::mutex guard;
long long shared_total = 0;

void add_range(int begin, int end) {
    for (int i = begin; i <= end; i++) {
        std::lock_guard<std::mutex> locked(guard);
        shared_total += i;
    }
}
```

## 语法、API 与边界

join 前线程对象必须处于 joinable 状态。不同线程对同一内存位置发生冲突访问（至少一方修改），至少一个访问非原子，且没有 happens-before 先后关系时，构成数据竞争并导致未定义行为；只读共享、正确的原子访问或写入独立内存位置不自动构成竞争。lock_guard 在作用域结束自动解锁，避免忘记 unlock。

```cpp
std::thread worker(add_range, 1, 50);
worker.join();  // 等待线程完成再读取结果
```

## 常见错误与实践建议

不要在持有锁时调用未知回调（死锁风险）；能按区间拆分独立结果再合并就减少锁争用。本课练习要求双线程分区累加后合并输出。
