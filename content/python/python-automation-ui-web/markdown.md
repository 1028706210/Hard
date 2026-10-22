---
id: python-automation-ui-web-markdown
title: Python Markdown 安全转换
concepts: [security, strings]
objectives: [识别 Markdown 的标题和链接语法, 在展示不可信 Markdown 前保留转义与净化边界]
prerequisites: [python-automation-ui-web-scrapy]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python-markdown2html.html
source_snapshot_date: 2026-08-23
---

# 文本格式不是可信 HTML

Markdown 适合写笔记和说明，但转换结果若进入网页，仍要使用经过审计的净化器。本课仅做字符串规则练习，不导入转换库，也不把文本渲染为页面。

```python
line = "# 今日计划"
print(line.startswith("# "))
```

链接目标需要单独审查，不能因为它写在 Markdown 中就信任它。

```python
url = "https://docs.example.test/guide"
print(url.startswith("https://"))
```

## 概念定义与适用场景

文本语法识别与安全渲染是两个问题。这里只判断一个明确的简化标题模式，不把结果视为净化后的 HTML，也不验证链接安全。

## 语法、API 与边界

读取一行文本，仅去掉末尾换行符。按简化规则判断一级标题：必须以 # 和一个空格开头，后面的标题去掉空白后非空，而且整段不含内部换行。输出 True 或 False，所有输入正常结束。不要渲染 HTML；此规则不是完整 CommonMark 解析器。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
