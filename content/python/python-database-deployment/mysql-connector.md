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

数据库驱动把 SQL 模板和参数值分别发送给服务端。参数化查询让驱动处理转义与类型绑定，适合按值查询、插入和更新；它不能替代对表名、排序字段等结构性输入的白名单验证。

## 语法、API 与边界

以 `SELECT ... WHERE email = %s` 这类固定模板表达语句形状，再把 email 放进独立参数序列。连接地址、用户名和密码只能来自受控部署配置，提交、回滚和关闭需要明确生命周期。课程用 fixture 审核模板与参数，不安装驱动、不连接真实数据库。

## 常见错误与实践建议

不要用 f-string 拼 SQL，也不要把凭据打印到日志。测试普通 email、不同合法 email 与无效格式，确认 SQL 模板不随输入改变；真实服务还应使用最小权限账户与事务边界。
