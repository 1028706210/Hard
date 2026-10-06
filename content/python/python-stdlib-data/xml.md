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

XML 用元素和属性表达层级数据。解析外部输入前应限制大小和来源；练习只使用内嵌的受信字符串，不访问网络或文件路径。

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

Python XML解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
