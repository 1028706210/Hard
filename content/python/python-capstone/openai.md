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

解析函数依赖明确的本地数据契约。缺少字段和空字符串不同，前者失败，后者是合法内容。本课只测试结构提取，不验证真实模型能力或服务可用性。

## 语法、API 与边界

读取一个本地JSON响应fixture，choices必须为非空列表，第一项的message.content必须为字符串。提取并打印content，允许空字符串，保留内部内容；其他choice不参与。缺失结构、类型不符或非法JSON无输出，退出码1。这是题目指定的离线响应结构，不调用任何AI服务、不读取密钥，不声称涵盖所有API返回类型。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
