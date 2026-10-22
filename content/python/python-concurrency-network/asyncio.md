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

await 在协程允许的位置让出控制权；取消后的任务必须被等待，取消不能伪造成完成。本题只有本地协程，未验证网络并发能力。

## 语法、API 与边界

读取非空文本并去掉首尾空白。普通文本通过本地 async render 协程转大写；文本恰好为 cancel 时创建任务并取消，捕获 CancelledError 后输出 cancelled。其他文本包括 __invalid__ 均按普通文本处理。空白输入无输出，退出码 1。使用 asyncio.run、await，不发请求；支架已读取 text。

模块挑战：读取状态文本并去掉首尾空白，判断它是否恰好属于终态集合 done、cancelled，输出True或False。大小写敏感，空文本与未知状态都为False，正常结束。只验证状态规则，不创建任务。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
