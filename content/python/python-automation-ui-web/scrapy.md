---
id: python-automation-ui-web-scrapy
title: Python Scrapy 请求计划
concepts: [collections, security]
objectives: [用纯数据表达请求队列与解析结果, 为爬取任务设置允许域名和去重边界]
prerequisites: [python-automation-ui-web-crawler]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python-scrapy.html
source_snapshot_date: 2026-08-23
---

# 先检查计划，后执行框架

Scrapy 项目通常包含请求、回调和管道。课程中把请求计划表示为本地结构，先校验允许域名再决定是否入队，绝不运行爬虫或访问站点。

```python
from urllib.parse import urlsplit

allowed = {"example.test"}
url = "https://example.test/list"
print(urlsplit(url).netloc in allowed)
```

队列去重能避免重复工作，也能防止错误配置造成请求放大。回调应处理解析不到字段的情况，而不是默默把错误页面当成数据。

```python
urls = ["https://example.test/a", "https://example.test/a", "https://example.test/b"]
planned = list(dict.fromkeys(urls))
print(len(planned))
```

## 概念定义与适用场景

请求计划的允许范围应在运行框架之前验证。字符串去重不等于 URL 规范化，允许域名也不能自动证明响应可信；本题只处理本地清单。

## 语法、API 与边界

输入每行一个 URL，去掉行首尾空白并忽略空行。必须符合已提供 allowed 函数：HTTPS、example.test 主机、无凭据、端口未指定或443、无空白或反斜杠。所有地址都合格后按完整字符串去重并输出数量；空清单输出0。任一不合格时无输出，退出码1。仅校验计划，不运行爬虫；不同路径或片段仍算不同字符串。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
