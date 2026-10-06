---
id: python-functions-iteration-functions
title: Python 函数
concepts: [functions, variables]
objectives: [定义带参数的函数, 用返回值传递计算结果]
prerequisites: [python-functions-iteration-with]
difficulty: beginner
experience_points: 35
source_url: https://www.runoob.com/python3/python3-function.html
source_snapshot_date: 2026-08-23
---

# 给可复用行为命名

函数将一段单一职责的行为命名。参数是函数的输入，`return` 让调用方接收结果；打印适合展示，而返回适合继续计算。

```python
def add(left, right):
    return left + right
print(add(2, 3))
```

明确的参数名比位置猜测更易读。

```python
def greet(name):
    return f"Hello, {name}"
print(greet("Hard"))
```


## 概念定义与适用场景

Python 函数解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
