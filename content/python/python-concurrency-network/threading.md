---
id: python-concurrency-network-threading
title: Python threading
concepts: [concurrency, security]
objectives: [识别锁保护共享状态的目的, 使用有限本地线程验证临界区与等待语义]
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

锁保护共享状态的一次完整更新，join 确保结果读取前所有线程已完成。输出测试验证计数结果，不足以证明任意并发程序无竞争，因此还需检查源代码中的锁和等待位置。

## 语法、API 与边界

读取线程数 n，必须为 0 到 8（含端点）的整数。创建 n 个本地线程，每个线程在同一把 Lock 保护下将共享计数器加一；启动全部线程后 join 全部，再输出计数。0 输出 0。非法输入无输出，退出码 1。禁止用 sleep 猜测完成时间，不进行网络操作。支架已验证 n。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
