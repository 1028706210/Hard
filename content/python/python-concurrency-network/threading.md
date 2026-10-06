---
id: python-concurrency-network-threading
title: Python threading
concepts: [concurrency, security]
objectives: [识别锁保护共享状态的目的, 在无真实线程的 fixture 中验证临界区语义]
prerequisites: [python-concurrency-network-multithreading]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python-treading.html
source_snapshot_date: 2026-08-23
---

# 临界区要小而明确

锁的目的不是增加并发，而是保护共享状态的一次完整修改。下面用有限数量的本地线程递增计数器；`with lock` 确保即使工作函数失败也会释放锁。

```python
from threading import Lock

state, lock = {"count": 0}, Lock()
with lock:
    state["count"] += 1
print(state["count"])
```

线程应由 `start()` 启动、由 `join()` 等待。不要依赖 `sleep` 猜测顺序；真正的协调条件应由锁、队列或事件明确表达。

```python
from threading import Thread

events = []
thread = Thread(target=lambda: events.append("done"))
thread.start(); thread.join()
print(events)
```

## 概念定义与适用场景

线程允许多个执行流共享同一进程内存，适合与阻塞 I/O 协作或维护既有线程接口。共享可变数据需要 `threading.Lock` 保护临界区；锁并不让业务逻辑更快，它只保证一次读改写不会交错。

## 语法、API 与边界

`Thread(target=...)` 创建工作线程，`start()` 启动，`join()` 等待完成。`with lock:` 保证即使函数中途抛错也会释放锁。线程数、队列容量和取消策略必须有界；本课只启动有限的本地 fixture 线程，不调用网络或外部命令。

## 常见错误与实践建议

不要在持锁状态下等待外部资源，也不要依赖 sleep 制造“正确”顺序。用小计数器和多个线程验证锁的效果，覆盖零任务、最大允许任务和非法任务数；失败路径同样必须释放资源。
