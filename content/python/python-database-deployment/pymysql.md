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

PyMySQL 的事务意图解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
