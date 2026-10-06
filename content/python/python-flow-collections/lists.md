---
id: python-flow-collections-lists
title: Python 列表
concepts: [collections, variables]
objectives: [创建并读取有序列表, 使用 append 增加一个元素]
prerequisites: [python-core-types-strings]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-list.html
source_snapshot_date: 2026-08-23
---

# 有序的可变序列

列表按位置保存多个值，适合需要增加、删除或更新的项目集合。索引从零开始；先检查长度再读取可避免越界。

```python
tasks = ["read", "code"]
print(tasks[0])
```

`append` 把一个值追加到末尾，修改的是同一份列表。

```python
tasks = []
tasks.append("test")
print(tasks)
```


## 概念定义与适用场景

Python 列表解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
