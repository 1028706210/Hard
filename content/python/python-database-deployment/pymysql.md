---
id: python-database-deployment-pymysql
title: PyMySQL 的事务意图
concepts: [databases, exceptions]
objectives: [用明确步骤表达提交与回滚意图, 在异常路径上保持资源处理可审查]
prerequisites: [python-database-deployment-mysql-connector]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python3-mysql.html
source_snapshot_date: 2026-08-23
code_exercise_exception_reason: 真实 PyMySQL 需要数据库和网络；本课对纯函数返回的事务决策进行评分。
---

# 把失败路径写在设计里

使用 PyMySQL 时，写入操作应把成功提交和失败回滚视为一对选择。连接、游标与异常处理应由可审查的结构控制；不要把连接对象或密码传到无关函数。本课仅模拟“操作是否成功”的决策，不创建连接。

```python
def transaction_action(ok):
    return "commit" if ok else "rollback"

print(transaction_action(False))
```

参数化同样适用于更新，值保持在参数序列中。

```python
sql = "UPDATE learner SET level = %s WHERE id = %s"
params = (2, 7)
print(len(params))
```

## 概念定义与适用场景

事务成功与失败应走不同分支，但返回 commit 字符串并不代表数据已提交。严格布尔输入避免把非空的字符串 false 错误解释为真。

## 语法、API 与边界

输入 JSON 布尔值 true 或 false。transaction_action(ok) 为 True 返回 commit，为 False 返回 rollback，打印结果。其他 JSON 类型或非法文本无输出，退出码1。仅计算事务意图，不连接数据库，不执行提交或回滚。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
