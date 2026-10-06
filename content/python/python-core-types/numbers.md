---
id: python-core-types-numbers
title: Python 数字
concepts: [types, operators]
objectives:
  - 区分整数除法、真除法和取余的结果。
  - 选择可读的数值表达式完成简单计算。
prerequisites: [python-core-types-operators]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-number.html
source_snapshot_date: 2026-08-23
---

# 数字计算要说明精度

`/` 会产生浮点结果，`//` 取整除后的商，`%` 得到余数。根据业务问题选择运算符，而不是只看结果看起来是否接近。

```python
average = 7 / 2
print(average)
```

余数常用于判断周期或奇偶。变量名应说明计算的单位与含义。

```python
item_count = 7
is_odd = item_count % 2 == 1
print(is_odd)
```


## 概念定义与适用场景

Python 数字解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
