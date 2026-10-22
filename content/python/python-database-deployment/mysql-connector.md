---
id: python-database-deployment-mysql-connector
title: mysql-connector 与参数化查询
concepts: [databases, security]
objectives: [区分 SQL 模板与参数值, 编写不拼接用户输入的查询描述]
prerequisites: [python-database-deployment-cgi]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-mysql-connector.html
source_snapshot_date: 2026-08-23
code_exercise_exception_reason: 数据库连接需要外部服务与凭据，本课以 SQL 模板和参数元组的静态结构评分。
---

# 让数据与指令分开

mysql-connector 可以把 SQL 模板和参数分别交给驱动。模板描述查询形状，参数承载值；不要用 f-string 或字符串相加把用户输入塞进 SQL。真实连接信息应来自受保护的部署配置，本练习不安装驱动或连接数据库。

```python
sql = "SELECT id FROM learner WHERE email = %s"
params = ("ada@example.test",)
print(sql, params)
```

把构造过程写成纯函数，既便于测试，也避免把凭据带入日志。

```python
def learner_lookup(email):
    return "SELECT id FROM learner WHERE email = %s", (email,)

print(learner_lookup("ada@example.test"))
```

## 概念定义与适用场景

模板和值分别传递，才能在真实驱动中使用参数化查询。本题只输出结构，不能替代驱动的执行或注入防护测试；邮箱格式限制与 SQL 参数化是不同职责。

## 语法、API 与边界

读取一个简化 email 标签：去掉首尾空白后恰好一个 @，两侧均非空，且不含空白。这个教学规则不是完整邮箱规范。构造固定 SQL 模板 SELECT id FROM learner WHERE email = %s 和单元素参数元组，输出 JSON 对象（键为 sql、params），使用 json.dumps(sort_keys=True)。格式无效时无输出，退出码1。参数不得拼进SQL；不连接数据库。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
