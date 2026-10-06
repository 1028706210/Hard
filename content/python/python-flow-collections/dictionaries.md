---
id: python-flow-collections-dictionaries
title: Python 字典
concepts: [collections, variables]
objectives: [用键值对保存具名信息, 通过键安全读取字典内容]
prerequisites: [python-flow-collections-tuples]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-dictionary.html
source_snapshot_date: 2026-08-23
---

# 用名字定位数据

字典将唯一键映射到值，适合记录具有字段名的信息。键的意义比位置更重要，因此读取时应使用明确的字段名称。

```python
profile = {"name": "Hard", "level": 1}
print(profile["name"])
```

`get` 可以提供缺失时的默认值，让可选字段的处理更平稳。

```python
profile = {}
print(profile.get("city", "unknown"))
```


## 概念定义与适用场景

Python 字典解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
