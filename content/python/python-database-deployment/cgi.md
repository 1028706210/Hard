---
id: python-database-deployment-cgi
title: CGI 的请求边界
concepts: [web, security]
objectives: [识别 CGI 响应中必须先写出的头部, 用纯函数验证表单字段而不执行服务器]
prerequisites: [python-concurrency-network-asyncio]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python3-cgi-programming.html
source_snapshot_date: 2026-08-23
code_exercise_exception_reason: CGI 依赖 Web 服务器环境，本课用可重复的请求数据判题，避免启动服务。
---

# 在边界处整理请求

CGI 程序由服务器启动，输入来自环境和表单，输出则必须是格式正确的响应。业务逻辑不应相信任意字段：先检查必填项、长度和允许值，再把结果交给后续代码。练习只处理内存中的字典，不启动 Web 服务器，也不读取真实环境变量。

```python
def response(text):
    return "Content-Type: text/plain\\n\\n" + text

print(response("ok"))
```

表单值缺失时给出稳定的错误结果，比让异常越过边界更容易诊断。

```python
def greeting(form):
    name = form.get("name", "").strip()
    return "missing" if not name else f"hello {name}"

print(greeting({"name": " Lin "}))
```

## 概念定义与适用场景

表单字段可能缺失，也可能存在但类型错误，应明确区分。当前纯函数只处理名称，不能把输出当成真实 CGI 响应或现代服务器部署；未启动服务。

## 语法、API 与边界

输入 JSON 表单对象，name 缺失时视为空字符串，存在时必须是字符串。greeting(form) 去掉名称首尾空白，非空返回 hello 加空格和名称，否则返回 missing。输出结果，保留内部空格。非法 JSON、非对象或错误字段类型无输出，退出码1。不启动服务器。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
