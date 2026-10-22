---
id: python-database-deployment-mongodb
title: MongoDB 文档与查询边界
concepts: [databases, data-structures, security]
objectives: [构造最小化的文档查询条件, 校验允许的过滤字段以限制查询范围]
prerequisites: [python-database-deployment-pymysql]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-mongodb.html
source_snapshot_date: 2026-08-23
code_exercise_exception_reason: MongoDB 练习不连接服务；使用内存文档和白名单过滤字段完成可评分判断。
---

# 文档查询也需要边界

MongoDB 用字典形状表达文档和条件，但“灵活”不等于接受任意键。接口应只允许它承诺支持的过滤字段，并拒绝未知条件。这样可以让索引、权限与查询成本保持可预测。本课在内存中处理字典，不导入数据库客户端。

```python
learner = {"name": "Ada", "level": 2}
query = {"level": 2}
print(learner["level"] == query["level"])
```

把允许字段集中声明，便于审阅与扩展。

```python
ALLOWED = {"name", "level"}
print(set({"level": 2}) <= ALLOWED)
```

## 概念定义与适用场景

允许字段检查应按子集关系验证所有键，不能只检查存在一个允许键。空过滤条件合法只是题目约定，真实服务还需要权限、范围及值结构验证。

## 语法、API 与边界

输入 JSON 对象作为查询条件，只检查顶层键是否全部属于 name、level。输出 True 或 False；空对象为 True。值不参与本题判断，因此这不是完整查询净化。非法JSON或非对象无输出，退出码1。不连接MongoDB。

模块挑战：输入JSON对象，records为记录列表，level为整数（非布尔）。每条记录必须含字符串name和整数level。按level精确匹配，输出姓名JSON列表，保留原顺序和重复项，使用ensure_ascii=False。空列表或无匹配输出[]。错误结构无输出，退出码1。不连接数据库。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
