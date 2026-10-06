---
id: python-stdlib-data-operator
title: Python operator
concepts: [operators, functions]
objectives: [使用 operator 表达基本运算, 选择可读的函数式操作]
prerequisites: [python-stdlib-data-builtins]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-operator.html
source_snapshot_date: 2026-08-23
---

# 具名运算

operator 将常用运算符提供为函数，适合传给排序和映射 API。它应提高调用的表达力，而非替代直观的普通表达式。

```python
import operator
print(operator.add(2, 3))
```

比较函数也返回布尔结果。

```python
import operator
print(operator.gt(3, 2))
```


## 概念定义与适用场景

Python operator解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
