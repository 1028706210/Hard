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

CGI 的请求边界解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
