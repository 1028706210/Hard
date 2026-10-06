---
id: python-core-types-operators
title: Python 运算符
concepts: [operators, types]
objectives:
  - 使用算术与比较运算符构造确定的表达式。
  - 区分赋值符号与相等比较符号。
prerequisites: [python-core-types-data-types]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-basic-operators.html
source_snapshot_date: 2026-08-23
---

# 用表达式得到新结果

算术运算符从数字得到新数字，比较运算符得到布尔值。`=` 用于把结果绑定给名称，`==` 用于判断两个值是否相等；把两者分开思考能避免常见错误。

```python
remaining = 10 - 3
print(remaining)
```

比较结果可以直接保存，也可以交给条件语句使用。

```python
passed = 82 >= 70
print(passed)
```


## 概念定义与适用场景

Python 运算符解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
