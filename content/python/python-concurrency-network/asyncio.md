---
id: python-concurrency-network-asyncio
title: Python asyncio
concepts: [concurrency, functions]
objectives: [理解协程等待不会阻塞事件循环, 用纯函数验证任务状态转换]
prerequisites: [python-concurrency-network-threading]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/python3/python-asyncio.html
source_snapshot_date: 2026-08-23
---

# 用本地协程表示异步流程

协程在 `await` 处让出事件循环，而不是阻塞整个解释器。下面的例子只等待零秒，仍完整展示 `async def`、`await` 和 `asyncio.run` 的调用链。

```python
import asyncio

async def normalize(text):
    await asyncio.sleep(0)
    return text.upper()

print(asyncio.run(normalize("hard")))
```

多个协程可通过 `gather` 并发安排；取消是必须保留的终态，不能伪造成成功。本课只运行本地协程，不创建网络连接。

```python
import asyncio

async def label(value):
    await asyncio.sleep(0)
    return f"job:{value}"

async def labels():
    return await asyncio.gather(label(1), label(2))

print(asyncio.run(labels()))
```

## 概念定义与适用场景

`asyncio` 用协程和事件循环协调大量等待型工作。`async def` 定义协程，`await` 在等待点交还控制权，`asyncio.run` 建立并关闭顶层事件循环；它适合异步 I/O 的编排，不会让 CPU 密集任务自动并行。

## 语法、API 与边界

使用 `create_task` 并发安排协程，再用 `gather` 或逐个 `await` 收集结果；`wait_for` 给操作设定超时。取消任务会在等待点抛出 `CancelledError`，清理逻辑应使用 `finally`，而不是把取消标为成功。课程 Runner 只运行本地协程和固定输入，不访问网络。

## 常见错误与实践建议

不要漏掉 `await`，也不要在协程中调用阻塞 API。测试至少覆盖成功、取消或超时、非法输入三种分支；并发题要断言结果和清理语义，而不依赖不稳定的执行顺序。
