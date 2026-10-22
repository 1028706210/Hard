---
id: python-stdlib-data-queue
title: Python queue
concepts: [collections, concurrency]
objectives: [使用队列按先进先出传递任务, 理解队列在并发协作中的作用]
prerequisites: [python-stdlib-data-pickle]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-queue.html
source_snapshot_date: 2026-08-23
---

# 有界的任务交接

队列让生产者和消费者通过受控容器交接任务。单线程示例仍应保持先进先出的语义，不把队列当作共享全局列表。

```python
from queue import Queue
items = Queue()
items.put("task")
```

取出一个值后，队列长度相应减少。

```python
from queue import Queue
items = Queue(); items.put(1)
print(items.get())
```

## 概念定义与适用场景

Queue 表示先进先出的任务交接，先放入的任务先取出。这里用单线程观察顺序，不能据此宣称完成了并发调度或线程安全验证。

## 语法、API 与边界

先完成入队，再用 get_nowait 取出。本题单线程下 empty 判断后不会有其他线程抢走元素；真实并发代码需处理 Empty，而不能依赖先检查再操作的原子性。

## 常见错误与实践建议

使用栈会反转顺序，使用集合会丢失重复任务。在没有任务时直接阻塞 get 可能一直等待，本题空输入应立即结束。
