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

Python SMTP解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
