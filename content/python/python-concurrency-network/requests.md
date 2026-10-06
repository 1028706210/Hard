---
id: python-concurrency-network-requests
title: Python requests
concepts: [io, security]
objectives: [用注入响应 fixture 处理 HTTP 状态, 为请求边界定义超时语义]
prerequisites: [python-concurrency-network-urllib]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python-requests.html
source_snapshot_date: 2026-08-23
---

# HTTP 代码应依赖接口

请求库应隐藏在可替换的客户端后。单元练习只读取字典 fixture 的状态码，不导入第三方包也不访问网络。

```python
response = {"status_code": 200}
print(response["status_code"] == 200)
```

非成功状态需要明确交给调用方处理。

```python
status = 404
print(status >= 400)
```


## 概念定义与适用场景

Python requests解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
