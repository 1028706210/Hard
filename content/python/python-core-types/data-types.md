---
id: python-core-types-data-types
title: Python 基本数据类型
concepts: [types, variables]
objectives:
  - 区分整数、浮点数、布尔值和字符串的基本用途。
  - 使用 type 函数观察一个值的运行时类型。
prerequisites: [python-core-types-basic-syntax]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-data-type.html
source_snapshot_date: 2026-08-23
---

# 值和类型一起工作

类型说明一个值可以参与哪些操作。整数适合计数，浮点数适合近似量，布尔值表达真假，而字符串保留文本。先看清值的类型，再决定怎样处理它。

```python
count = 3
ratio = 0.5
enabled = True
```

`type` 是观察工具，不是转换工具。它帮助我们验证变量是否拿到了预期的数据。

```python
label = "Hard"
print(type(label).__name__)
```


## 概念定义与适用场景

Python 基本数据类型解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
