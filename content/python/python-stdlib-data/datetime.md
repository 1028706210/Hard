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

timedelta 表达时间间隔，date 加减它会处理月份和闰年的进位。输出完整日期才能观察跨月跨年，而不只是日字段。

## 语法、API 与边界

输入解析与结果溢出是两个边界：合法的起点加上一天也可能超出 date 支持范围。捕获 OverflowError 后按题面退出，不能输出部分结果。

## 常见错误与实践建议

不要直接把 day 加一并拼接字符串，也不要用机器当前日期替代输入。零天应保持日期不变，负天数表示向过去移动。
