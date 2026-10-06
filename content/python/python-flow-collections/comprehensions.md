---
id: python-flow-collections-comprehensions
title: Python 推导式
concepts: [collections, control-flow]
objectives: [用列表推导式转换一组值, 在推导式中加入简单筛选条件]
prerequisites: [python-flow-collections-first-program]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/python3/python-comprehensions.html
source_snapshot_date: 2026-08-23
---

# 把遍历写成一个表达式

推导式适合把一次遍历和一个清晰的转换放在一起。表达式过长或分支过多时，普通循环通常更容易阅读和调试。

```python
values = [1, 2, 3]
squares = [value * value for value in values]
print(squares)
```

条件位于末尾时，只保留符合规则的元素。

```python
values = [1, 2, 3, 4]
even = [value for value in values if value % 2 == 0]
print(even)
```


## 概念定义与适用场景

Python 推导式解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
