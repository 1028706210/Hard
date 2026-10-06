---
id: python-core-types-basic-syntax
title: Python 基础语法
concepts: [variables, interpreter]
objectives:
  - 使用缩进和语句顺序组织一段可运行的 Python 程序。
  - 识别赋值、表达式与输出语句各自的职责。
prerequisites: [python-foundations-learning-resources]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-basic-syntax.html
source_snapshot_date: 2026-08-23
---

# 用顺序和缩进表达意图

Python 从上到下执行语句。名称先绑定到值，再在后面的表达式中使用；同一代码块里的缩进必须一致。把程序拆成小而清晰的语句，能让阅读和排错都更直接。

```python
language = "Python"
print(language)
```

条件块后的四个空格不是装饰，而是这个块的边界。保持每个块只做一件事，可以减少意外的执行路径。

```python
ready = True
if ready:
    print("start")
```


## 概念定义与适用场景

Python 基础语法解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
