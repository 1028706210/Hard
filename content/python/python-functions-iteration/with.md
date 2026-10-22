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

with 划定上下文的进入和退出边界。真正的文件上下文负责关闭文件；nullcontext 则原样提供传入的值，退出时不执行额外清理，适合先观察语法而不接触外部资源。

## 语法、API 与边界

with nullcontext(n) as value 将进入上下文得到的对象绑定到 value。块内按题意加一并输出。with 不会创建独立的变量作用域，也不保证任意异常都会被吞掉；异常处理由具体管理器决定。

## 常见错误与实践建议

不要把演示用 nullcontext 当成文件关闭验证。它不改变数值，也不检查输入格式；整数解析由支架完成。本题检查输出，不能据此证明答案使用了 with。
