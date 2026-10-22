---
id: python-stdlib-data-xml
title: Python XML
concepts: [io, collections]
objectives: [解析受信 XML 文本的简单节点, 从结构化节点读取明确字段]
prerequisites: [python-stdlib-data-regex-basics]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python3-xml-processing.html
source_snapshot_date: 2026-08-23
---

# 按结构读取 XML

XML 用元素和属性表达层级数据。解析外部输入前应限制大小和来源；练习只解析大小和结构受限的输入文本，不访问网络或文件路径。

```python
from xml.etree import ElementTree as ET
root = ET.fromstring("<item>Hard</item>")
print(root.text)
```

节点查询应尽量精确，避免依赖不稳定的位置顺序。

```python
from xml.etree import ElementTree as ET
root = ET.fromstring("<item id='1'/>")
print(root.get("id"))
```

## 概念定义与适用场景

XML 先解析为元素，再按结构读取。本题采用严格教学子集，避免把任意外部 XML 当作安全或完整支持的输入。

## 语法、API 与边界

root.text 是首个子节点之前的文本，本题不允许子节点，所以可直接读取。空元素的 text 为 None，应输出空字符串；实体转义由解析器处理。

## 常见错误与实践建议

不能用正则删除标签代替解析，也不能用 strip 改变元素内部的内容。限制大小和禁用声明仅是本题边界，不是通用 XML 安全方案。
