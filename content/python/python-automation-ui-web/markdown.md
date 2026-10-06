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

Python Markdown 安全转换解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
