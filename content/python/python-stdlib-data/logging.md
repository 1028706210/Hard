---
id: python-stdlib-data-logging
title: Python logging
concepts: [tooling, security]
objectives: [使用日志级别区分诊断重要性, 避免在日志中写入私密数据]
prerequisites: [python-stdlib-data-stringio]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-logging.html
source_snapshot_date: 2026-08-23
---

# 记录安全的诊断信息

日志用于理解运行状态，不应用来保存密码、隐藏测试或完整用户代码。级别应反映事件的可操作性，消息应当简洁且可搜索。

```python
import logging
logging.warning("retry planned")
```

结构化上下文只放安全标识。

```python
import logging
logging.info("lesson=%s", "python")
```

## 概念定义与适用场景

日志等级决定消息是否被处理，处理器和格式决定写到哪里、显示什么。本题用公开计数作为诊断信息，不记录输入原文。

## 语法、API 与边界

basicConfig 将流明确设为 sys.stdout，否则默认日志常写到 stderr，在线输出就不匹配。WARNING 阈值会过滤 INFO，使用占位参数表达数值。

## 常见错误与实践建议

不应把任意用户输入插入日志。验证次数失败时直接退出，不回显敏感样式的字符串。通过输出测试不代表完成了整个应用的日志安全审计。
