---
id: python-core-types-conversion
title: Python 数据类型转换
concepts: [types, variables]
objectives:
  - 使用 int、float 和 str 进行显式类型转换。
  - 在转换前识别可能无效的输入格式。
prerequisites: [python-core-types-data-types]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-type-conversion.html
source_snapshot_date: 2026-08-23
---

# 把数据变成需要的形状

输入通常先以文本到达程序。显式调用转换函数能把意图写出来，也让失败位置更容易定位。不要假设每段文本都能变成数字，先约定输入格式。

```python
text_count = "12"
count = int(text_count)
print(count + 1)
```

转换为字符串常用于组合展示信息；它不会改变原变量，只产生一个新值。

```python
score = 95
message = "Score: " + str(score)
print(message)
```


## 概念定义与适用场景

Python 数据类型转换解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
