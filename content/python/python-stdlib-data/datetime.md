---
id: python-stdlib-data-datetime
title: Python datetime
concepts: [types, functions]
objectives: [创建确定的日期时间值, 用 timedelta 表达时间间隔]
prerequisites: [python-stdlib-data-logging]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-datetime.html
source_snapshot_date: 2026-08-23
---

# 使用可计算的时间对象

datetime 用对象表示日期和时间。业务规则应接收注入时间，使测试不依赖机器当天。

```python
from datetime import date
print(date(2026, 8, 23).day)
```

时间间隔用 timedelta 表达。

```python
from datetime import date, timedelta
print((date(2026, 1, 1) + timedelta(days=1)).day)
```


## 概念定义与适用场景

Python datetime解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
