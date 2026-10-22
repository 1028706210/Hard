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

HTTP 响应规则由接口约定决定。这里精确判断 200，不把所有 2xx 视为通过；这不意味着其他接口不应接受 201。本地数据验证不替代超时和网络异常处理。

## 语法、API 与边界

输入 JSON 响应 fixture，必须含整数 status_code，范围 100 到 599，布尔值不算整数。仅状态恰好 200 输出 True，其他合法状态输出 False。缺字段、错误类型或非法 JSON 无输出，退出码 1。只判断 fixture，不导入 requests、不发网络请求，支架已校验 data。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
