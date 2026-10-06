---
id: python-concurrency-network-urllib
title: Python urllib
concepts: [io, security]
objectives: [解析受控 URL 结构, 区分 URL 构造与实际网络请求]
prerequisites: [python-concurrency-network-smtp]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python-urllib.html
source_snapshot_date: 2026-08-23
---

# 只验证 URL，不发请求

urllib 可以处理 URL，但不受信输入必须限制 scheme 和主机。本课只用解析器检查内嵌 URL，Runner 不进行网络访问。

```python
from urllib.parse import urlsplit
print(urlsplit("https://example.test/a").scheme)
```

查询参数应编码，而不是字符串拼接。

```python
from urllib.parse import urlencode
print(urlencode({"q": "hard"}))
```


## 概念定义与适用场景

Python urllib解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
