---
id: python-foundations-hello-world
title: Hello World
concepts: [variables, io]
objectives:
  - 认识 Python 程序按顺序执行的方式。
  - 使用 print 输出清晰的问候文本。
prerequisites: []
difficulty: beginner
experience_points: 50
source_url: https://www.runoob.com/python3/python3-tutorial.html
source_snapshot_date: 2026-08-23
---

# Hello World

程序的第一步不是记住复杂语法，而是让计算机完成一个可观察的小动作。Python 的 `print` 会把文本写到终端，让你立即确认程序已经运行。

```python
print("Hello, Hard!")
```

你也可以先保存文本，再把它输出。变量让后续修改更直接。

```python
message = "Hello, Hard!"
print(message)
```

当输出与预期不同时，先检查引号、括号和拼写，再重新运行。


## 概念定义与适用场景

Hello World 的关键在于 print、字符串字面量和终端输出。阅读前面的样例时，先指出数据从哪里进入、状态如何变化、结果由哪条规则决定；只有这些关系清楚，练习中的不同输入才有意义。

## 语法、API 与边界

本课的 API 或语法应只承接 print、字符串字面量和终端输出 所需的最小操作。把正常输入、空值或非法值分别写清楚；涉及文件、网络、图形界面、数据库或第三方服务时，只使用本地 fixture 或纯函数边界。

## 常见错误与实践建议

不要把示例的固定结果当作答案。为 Hello World 至少检查一个普通样本、一个边界样本和一个失败分支，并解释为什么输出或异常符合这条主题规则。
