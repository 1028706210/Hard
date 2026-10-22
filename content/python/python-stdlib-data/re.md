---
id: python-stdlib-data-re
title: Python re 模块
concepts: [strings, functions]
objectives: [使用编译后的模式匹配文本, 选择 fullmatch 验证完整输入]
prerequisites: [python-stdlib-data-datetime]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-re.html
source_snapshot_date: 2026-08-23
---

# 可复用的文本规则

re 模块支持编译和复用模式。完整字段校验优先使用 fullmatch，避免局部匹配误认为整个输入有效。

```python
import re
pattern = re.compile(r"[a-z]+")
print(bool(pattern.fullmatch("hard")))
```

模式应限制为任务所需的最小范围。

```python
import re
print(bool(re.fullmatch(r"[0-9]{2}", "42")))
```

## 概念定义与适用场景

fullmatch 要求整个文本符合模式，match 只要求开头匹配。模式编译后可用于多个值，避免在各调用点重复拼接规则。

## 语法、API 与边界

[a-z] 只表示 ASCII 小写范围，+ 要求至少一个。这里不使用 strip，因为空格是需要检测的不合法字符。

## 常见错误与实践建议

匹配失败返回 None，bool 将它变为 False。不能用 search 接受局部小写，也不能先 lower 使本来错误的输入通过。
