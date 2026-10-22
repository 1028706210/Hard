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

前缀匹配不能验证真实主机，必须按解析后的 scheme、hostname、凭据与端口检查。允许列表只是本地计划规则，本题没有执行 URL 请求，也不构成完整服务端请求安全方案。

## 语法、API 与边界

读取 URL 文本并去掉首尾空白。仅当 scheme 为 https、hostname 为 example.test、无用户名密码、端口未指定或为 443，且输入不含空白或反斜杠时输出 True；否则输出 False，均正常结束。主机名大小写不敏感，路径与查询不参与判断。使用 urlsplit，不发起请求。端口解析错误也返回 False。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
