---
id: python-flow-collections-sets
title: Python 集合
concepts: [collections, types]
objectives: [使用集合去除重复值, 判断一个值是否属于集合]
prerequisites: [python-flow-collections-dictionaries]
difficulty: beginner
experience_points: 25
source_url: https://www.runoob.com/python3/python3-set.html
source_snapshot_date: 2026-08-23
---

# 关注成员而非顺序

集合保存不重复的元素，不承诺显示顺序。它适合表达允许值、已访问项和去重后的标签。

```python
tags = {"python", "python", "test"}
print(len(tags))
```

成员测试直接回答一个值是否已出现，无需手写循环。

```python
allowed = {"read", "write"}
print("read" in allowed)
```


## 概念定义与适用场景

Python 集合解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
