---
id: python-concurrency-network-smtp
title: Python SMTP
concepts: [io, security]
objectives: [理解邮件消息包含收件人与正文, 用 fixture 验证消息格式]
prerequisites: [python-concurrency-network-sockets]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python3-smtp.html
source_snapshot_date: 2026-08-23
---

# 邮件发送应可替换

SMTP 客户端不应在学习 Runner 中真实发信。业务代码应把消息构造与发送器分离，测试只验证受信 fixture 的字段。

```python
mail = {"to": "learner@example.test", "body": "ready"}
print(mail["body"])
```

凭据不能写入消息、日志或代码仓库。

```python
subject = "Hard lesson"
print(subject)
```

## 概念定义与适用场景

消息构造可以独立于发送器验证。to 在本题只是非空接收者标签，不声称它可投递；正文保留原始内容，不输出凭据或额外字段。

## 语法、API 与边界

读取 JSON 对象，要求 to 是非空字符串，body 是字符串（允许空）。输出 body 原文，print 添加换行；允许额外字段。格式或字段类型不合法时无输出，退出码 1。这里只读取消息 fixture，不验证邮箱规范，也不发送邮件。支架已经提供 data。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
