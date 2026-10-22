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

日期文本只是表示形式，date 对象还验证真实日历。固定年月日格式降低地区歧义，练习不读取当前日期，结果可复现。

## 语法、API 与边界

先检查数字位数与分隔符，再进行日历解析。date.fromisoformat 支持的部分其他格式不在本题范围；年份很小时 isoformat 仍补足四位。

## 常见错误与实践建议

不要只用字符串正则判断日期存在，也不要把二月统一视为 28 天。2024 与 2023 的二月二十九日有不同结果。
