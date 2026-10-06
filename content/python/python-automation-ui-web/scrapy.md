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

Scrapy 将请求、回调、去重和管道组织为抓取流程。允许域名规定请求边界，去重集合避免重复 URL 放大任务；这些规则在真正发送请求前就应该可独立验证。

## 语法、API 与边界

本课把 URL fixture 作为输入，使用 `urlsplit` 检查 host、使用 `set` 计算去重后的计划。它不导入 Scrapy 框架、不访问网站，也不把 HTML 正文保存在课程内容中；实际项目再把同样的纯函数接到 Request 和 callback 上。

## 常见错误与实践建议

不要把任意外域 URL 加入队列，也不要仅靠字符串前缀判断域名。测试重复路径、空队列和外域 URL，记录拒绝原因；真实采集还必须遵守站点规则、频率限制和数据授权。
