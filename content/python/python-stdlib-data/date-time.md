---
id: python-stdlib-data-date-time
title: Python 日期和时间
concepts: [types, functions]
objectives: [区分日期文本和时间对象, 使用固定格式呈现可比较的日期]
prerequisites: [python-stdlib-data-json]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python3-date-time.html
source_snapshot_date: 2026-08-23
---

# 把时间表示说清楚

日期文本适合传输和展示，时间对象适合计算。固定格式能降低不同地区和工具对同一日期的歧义。

```python
from datetime import date
print(date(2026, 8, 23).isoformat())
```

不要在业务测试中直接读取机器当前时间，应注入或固定时间来源。

```python
from datetime import date
print(date(2026, 1, 1).year)
```


## 概念定义与适用场景

Python 日期和时间解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
