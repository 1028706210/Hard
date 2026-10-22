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

赋值让后续语句使用读取到的名字，而不是反复复制示例里的 Hard。问候结果依赖实际输入；缩进决定空值检查的范围。

## 语法、API 与边界

本课练习把整段标准输入去掉首尾空白后作为名字。名字内部的空格保留，中文名字也有效。只有处理后为空才退出；起始代码提供了读取与退出分支，重点是赋值和顺序执行。

## 常见错误与实践建议

不要把输出缩进到空值分支中，也不要只写固定的 Hello, Hard。分别用一个英文名字、带空格的名字和空输入检查输出，空输入时不应先打印问候。
