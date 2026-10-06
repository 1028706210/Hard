---
id: python-capstone-openai
title: Python AI 客户端的本地契约
concepts: [functions, security, collections]
objectives: [用本地 fixture 验证 AI 响应解析逻辑, 将密钥和网络调用隔离在可替换边界之外]
prerequisites: [python-capstone-quiz]
difficulty: advanced
experience_points: 40
source_url: https://www.runoob.com/python3/python-openai.html
source_snapshot_date: 2026-08-23
---

# 先定义边界，再连接服务

AI 应用的核心业务不应直接依赖网络响应。把响应当作普通字典传入解析函数，测试就能使用固定 fixture；本课不发送请求，也不读取任何真实密钥。

```python
fixture = {"choices": [{"message": {"content": "你好"}}]}
text = fixture["choices"][0]["message"]["content"]
print(text)
```

配置层只接收“是否已配置”的事实，不输出或保存令牌。真正的客户端应从受控环境读取密钥，并将请求动作放在 Runner 之外。

```python
config = {"model": "demo-model", "has_token": False}
print(config["has_token"] and bool(config["model"]))
```

解析时还要给缺失字段一个可预测的结果，避免把服务响应异常误认为用户输入错误。


## 概念定义与适用场景

Python AI 客户端的本地契约解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
