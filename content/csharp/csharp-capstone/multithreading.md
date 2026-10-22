---
id: csharp-capstone-multithreading
title: 多线程与确定性汇总
concepts: [concurrency]
objectives:
  - 掌握 Thread 的启动、完成等待和共享状态风险，理解 Join 建立的完成顺序。
  - 通过分片所有权让两个工作线程写入不同结果槽位，再由主线程确定性合并结果。
prerequisites: [csharp-capstone-unsafe-code]
difficulty: advanced
experience_points: 40
source_url: https://www.runoob.com/csharp/csharp-multithreading.html
source_snapshot_date: 2026-08-23
---

# 多线程与确定性汇总

## 概念定义与适用场景

线程是进程中的独立执行路径。多个线程可以同时推进计算，但只要它们读写同一可变状态，就必须定义所有权或同步规则。并发不保证执行顺序，也不保证更快；任务足够大、能够独立分片并且合并成本较低时，并发才可能带来收益。

```csharp
var worker = new Thread(() => Console.WriteLine("worker"));
worker.Start();
worker.Join();
Console.WriteLine("completed");
```

## 语法、API 与边界

`Start` 让线程进入可调度状态，`Join` 阻塞调用线程直到目标线程结束。不要让两个线程对同一个计数器执行 `value++`，因为读、加一和写回不是不可分割操作。可以使用 `lock`、`Interlocked`，也可以像本课练习一样给每个线程独占的结果槽位，等待全部线程结束后再合并。

```csharp
var partial = new long[2];
var left = new Thread(() => partial[0] = 20);
var right = new Thread(() => partial[1] = 22);
left.Start();
right.Start();
left.Join();
right.Join();
Console.WriteLine(partial[0] + partial[1]);
```

## 常见错误与实践建议

常见错误包括忘记 `Join` 就读取未完成结果、在循环闭包中捕获不断变化的索引、持锁执行慢操作，以及用 `Sleep` 猜测线程完成。测试并发逻辑时应让输出与调度顺序无关，避免依赖“某个线程先打印”。本课把输入索引按奇偶分给两个线程，每个线程只写自己的汇总槽位，主线程在两次 `Join` 后输出唯一确定的结果。
