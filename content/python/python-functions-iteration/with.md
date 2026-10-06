---
id: python-functions-iteration-with
title: Python with
concepts: [io, functions]
objectives: [理解上下文管理器的进入和退出边界, 使用 with 表达资源使用范围]
prerequisites: [python-functions-iteration-iterators]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python3-with-keyword.html
source_snapshot_date: 2026-08-23
---

# 让资源边界可见

`with` 将资源获取与清理放在同一个明确范围中。即使块内发生异常，上下文管理器也能执行退出逻辑；这比依赖分散的关闭调用更可靠。

```python
from contextlib import nullcontext
with nullcontext("ready") as state:
    print(state)
```

文件、锁和数据库会话都应在有限的上下文里使用。

```python
from contextlib import nullcontext
with nullcontext(2) as value:
    print(value + 1)
```


## 概念定义与适用场景

Python with解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
