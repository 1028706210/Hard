---
id: python-modules-io-oop-input-output
title: Python 输入和输出
concepts: [io, strings]
objectives: [用 print 生成可观察输出, 把外部文本在边界处转换为需要的类型]
prerequisites: [python-modules-io-oop-modules]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-inputoutput.html
source_snapshot_date: 2026-08-23
---

# 在边界处理文本

终端输入通常是字符串，输出应当表达给人的信息。先在输入边界检查和转换，再把内部逻辑保持为明确类型，能让错误更早出现。

```python
name = "Hard"
print(f"Hello, {name}")
```

格式化输出把标签和数据分开，便于阅读与测试。

```python
score = 90
print(f"Score: {score}")
```


## 概念定义与适用场景

Python 输入和输出解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
