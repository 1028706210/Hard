---
id: python-stdlib-data-builtins
title: Python 内置函数
concepts: [functions, collections]
objectives: [使用 len、sum 等内置函数处理简单数据, 选择表达意图的内置函数]
prerequisites: [python-stdlib-data-date-time]
difficulty: beginner
experience_points: 25
source_url: https://www.runoob.com/python3/python3-built-in-functions.html
source_snapshot_date: 2026-08-23
---

# 优先使用清楚的内置函数

内置函数覆盖常见的长度、聚合和转换操作。使用它们能减少手写循环，但仍应明确输入类型和空集合的行为。

```python
print(len(["a", "b"]))
```

聚合结果由元素类型决定，先验证数据再计算。

```python
print(sum([1, 2, 3]))
```


## 概念定义与适用场景

Python 内置函数解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
