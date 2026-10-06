---
id: python-flow-collections-tuples
title: Python 元组
concepts: [collections, types]
objectives: [使用元组表示固定顺序的数据, 区分元组和列表的可变性]
prerequisites: [python-flow-collections-lists]
difficulty: beginner
experience_points: 25
source_url: https://www.runoob.com/python3/python3-tuple.html
source_snapshot_date: 2026-08-23
---

# 固定顺序的记录

元组同样按索引保存多个值，但建立后不能原地修改。对不会变化的坐标、选项或配置片段，元组能清楚表达“固定”的意图。

```python
point = (3, 4)
print(point[1])
```

单元素元组需要尾随逗号，避免与普通括号表达式混淆。

```python
single = ("only",)
print(len(single))
```


## 概念定义与适用场景

Python 元组解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
