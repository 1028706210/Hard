---
id: python-functions-iteration-lambda
title: Python lambda
concepts: [functions, collections]
objectives: [使用 lambda 表达单个简单表达式, 在复杂逻辑中选择具名函数]
prerequisites: [python-functions-iteration-functions]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python-lambda.html
source_snapshot_date: 2026-08-23
---

# 简短函数表达式

`lambda` 适合只有一个表达式的小转换。若需要多步逻辑、注释或单元测试入口，应使用 `def` 写出具名函数。

```python
double = lambda value: value * 2
print(double(3))
```

它常与排序等接收回调的 API 配合。

```python
items = ["bbb", "a"]
print(sorted(items, key=lambda item: len(item)))
```


## 概念定义与适用场景

Python lambda解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
