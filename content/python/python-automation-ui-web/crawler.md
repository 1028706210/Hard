---
id: python-automation-ui-web-crawler
title: Python 爬虫解析边界
concepts: [security, io]
objectives: [从本地 HTML fixture 提取明确字段, 说明抓取前必须遵守的授权与频率边界]
prerequisites: [python-automation-ui-web-selenium]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python-spider-beautifulsoup.html
source_snapshot_date: 2026-08-23
---

# 解析与访问分开

网页解析函数应只接收文本并返回小而明确的数据。本课不用网络请求，fixture 代表已经获授权、可供练习的页面快照；真实抓取还必须检查 robots 规则、服务条款和速率限制。

```python
html = '<h1>课程标题</h1>'
print(html.removeprefix('<h1>').removesuffix('</h1>'))
```

不把密码、会话令牌或整段页面日志写进结果，结果应当是所需字段。

```python
record = {"title": "课程标题", "url": "/lesson"}
print(sorted(record))
```

## 概念定义与适用场景

解析与访问分开，提取结果仍是普通文本。使用解析器处理内联标签和实体，比只移除固定前后缀更符合 HTML 片段的结构；此支架不是完整网页清洗器。

## 语法、API 与边界

读取至多 4096 字符的本地 HTML fixture，提取第一个有闭合标签的 h1 内的文本（包括内联元素文本），将字符实体解码、去掉结果首尾空白后输出。h1 为空时输出空行；没有完整 h1 或文本超长时无输出，退出码 1。使用已提供的 HeadingParser；只解析本地片段，不抓取网页，不将文本渲染为 HTML。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
