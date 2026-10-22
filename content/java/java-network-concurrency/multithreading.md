---
id: java-network-concurrency-multithreading
title: 多线程
concepts: [concurrency, control-flow]
objectives:
  - 掌握多线程的核心概念与使用方式。
  - 用正常、边界和失败输入验证多线程。
prerequisites: [java-network-concurrency-sending-email]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-multithreading.html
source_snapshot_date: 2026-08-23
---

# 多线程

Java 多线程通过 Thread 类和 Runnable 接口实现并发执行。线程调度由 JVM 管理，需注意共享数据的同步。

```java
class Task implements Runnable {
    public void run() { System.out.println("running"); }
}
public class Main {
    public static void main(String[] args) throws Exception {
        Thread t = new Thread(new Task());
        t.start();
        t.join();
    }
}
```

Runnable 定义任务，Thread 启动线程，join 等待线程结束。

```java
public class Main {
    public static void main(String[] args) throws Exception {
        int sum = 0;
        for (int i = 1; i <= 5; i++) sum += i;
        System.out.println(sum);
    }
}
```

单线程顺序计算，线程安全无需同步。多线程下共享 sum 需同步。

## 概念定义与适用场景

多线程解决的是并发执行与资源利用的问题。它通过线程并行执行任务，但共享数据需要同步以避免竞态条件。

## 语法、API 与边界

本课使用单线程计算模拟并发任务的结果验证。输入为整数 N，输出 1 到 N 的总和。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要忽略线程安全（共享数据需 synchronized 或 Lock）。线程启动后不能再次 start。提交前应覆盖单线程计算、边界值和线程等待的验证。
