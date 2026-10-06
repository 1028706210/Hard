---
id: python-stdlib-data-json
title: Python JSON
concepts: [io, collections]
objectives: [把简单对象编码为 JSON, 从 JSON 文本解析受信字段]
prerequisites: [python-stdlib-data-xml]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python3-json.html
source_snapshot_date: 2026-08-23
---

# 在文本和对象之间转换

JSON 是常见的数据交换格式。编码时只输出公开、必要字段；解析时把输入当作不可信数据，并在业务边界验证字段类型。

```python
import json
print(json.dumps({"name": "Hard"}))
```

解析后的对象仍需要按键读取和检查。

```python
import json
data = json.loads('{"count": 2}')
print(data["count"])
```

## 概念定义与适用场景

JSON 是跨语言的数据交换格式：对象对应字典，数组对应列表，文本、数字、布尔和 null 对应 Python 基础值。它适合公开配置和请求负载，不适合承载可执行代码、密码或未经验证的任意对象。

## 语法、API 与边界

`json.dumps` 编码对象，`json.loads` 解析文本；解析成功只说明语法正确，并不说明字段可信。读取后仍要检查对象形状、必需键、类型、范围和未知字段。数字中的布尔值在 Python 中是 `int` 的子类，整数校验时要专门排除它。

## 常见错误与实践建议

不要把 JSON 字符串手工拼接，也不要在解析后直接信任嵌套字段。用固定 fixture 覆盖正常对象、零值、缺键和错误格式；对公开 API 只序列化允许暴露的字段。
