---
id: cpp-algorithms-concurrency-condition-variable
title: C++ <condition_variable>
concepts: [concurrency]
objectives:
  - 会用 unique_lock 配合 wait/notify 完成线程握手。
  - 理解谓词版 wait 防虚假唤醒的作用。
prerequisites: []
difficulty: advanced
experience_points: 30
source_url: https://www.runoob.com/cplusplus/cpp-libs-condition_variable.html
source_snapshot_date: 2026-08-23
---

# C++ <condition_variable>

## 概念定义与适用场景

条件变量让线程「等到条件成立」：等待方持 unique_lock 调 wait（释放锁并睡眠），通知方改共享状态后 notify_one。这是生产者-消费者握手的标准件。

```cpp
#include <condition_variable>
#include <mutex>

std::mutex guard;
std::condition_variable signal;
bool ready = false;
long long shared_value = 0;
```

## 语法、API 与边界

wait(lock, predicate) 循环检查谓词，应对虚假唤醒；本例中的共享谓词及关联数据必须用与 wait 配套的同一互斥量保护。notify 可以在持锁时或解锁后调用，通知本身不会保存“条件已成立”的状态。下面采用先持锁修改状态、解锁后通知的直观顺序；等待方从 wait 返回前已重新持锁，可以读取受该锁保护的数据。

```cpp
// worker：计算并通知
{
    std::lock_guard<std::mutex> locked(guard);
    shared_value = computed;
    ready = true;
}
signal.notify_one();

// main：等待谓词成立
{
    std::unique_lock<std::mutex> locked(guard);
    signal.wait(locked, [] { return ready; });
}
```

## 常见错误与实践建议

常见错误是未用同一互斥量保护谓词，或无谓词 wait 遇虚假唤醒后直接继续。不能只按 notify 与赋值的表面顺序判断对错：在同一锁内先通知、再更新谓词、最后解锁，也可以正确，因为等待方须重新获得锁才检查谓词；若先通知并让等待方重新检查到 false，再在没有后续通知的情况下更新状态，则可能一直等待。先用简单布尔谓词完成一次握手，再扩展队列。本课练习要求主线程等待 worker 结果后输出。
