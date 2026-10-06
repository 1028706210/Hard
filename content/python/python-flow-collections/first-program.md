---
id: python-flow-collections-first-program
title: Python 编程第一步
concepts: [variables, control-flow]
objectives: [把问题拆成输入处理输出步骤, 用小程序验证一个明确结果]
prerequisites: [python-flow-collections-loops]
difficulty: beginner
experience_points: 25
source_url: https://www.runoob.com/python3/python3-step1.html
source_snapshot_date: 2026-08-23
---

# 先做一个能观察的程序

程序练习应从可观察的输入、处理和输出开始。把目标写成一个小例子，先验证结果，再增加分支或数据量。

```python
name = "Hard"
print(name.upper())
```

每次只引入一个新概念，错误出现时就能快速回到最后一个有效版本。

```python
items = [1, 2]
print(len(items))
```


## 概念定义与适用场景

Python 编程第一步解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
