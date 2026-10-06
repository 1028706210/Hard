---
id: python-flow-collections-data-structures
title: Python 数据结构
concepts: [collections, control-flow]
objectives: [为问题选择列表字典或集合, 用组合数据结构表达简单记录]
prerequisites: [python-flow-collections-comprehensions]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python3-data-structure.html
source_snapshot_date: 2026-08-23
---

# 选择匹配问题的容器

列表强调顺序，字典强调名称，集合强调唯一成员。先说清要按位置、按键还是按成员访问，再选择容器。

```python
record = {"name": "Hard", "tags": ["python"]}
print(record["tags"][0])
```

组合容器时，命名中间值能减少嵌套访问造成的误读。

```python
groups = {"beginner": ["syntax"]}
print(groups["beginner"])
```


## 概念定义与适用场景

Python 数据结构解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
