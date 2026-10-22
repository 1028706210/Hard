---
id: python-concurrency-network-multithreading
title: Python 多线程
concepts: [concurrency, security]
objectives: [理解并发任务的共享状态风险, 用纯函数检查任务结果聚合]
prerequisites: [python-concurrency-network-subprocess]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python3-multithreading.html
source_snapshot_date: 2026-08-23
---

# 并发从数据约定开始

多线程会同时访问状态，必须定义所有权和同步规则。本课不启动线程，只在确定的列表 fixture 上验证结果汇总。

```python
results = [1, 2]
print(sum(results))
```

共享结果应由单一受控位置提交。

```python
done = [True, True]
print(all(done))
```

## 概念定义与适用场景

先把并发工作与汇总分开，确定每个结果只提交一次。这里的固定列表表示已经完成的结果；求和通过不证明调度顺序、锁或线程回收已经正确。

## 语法、API 与边界

读取 JSON 整数列表作为已完成任务结果，布尔值不算整数，使用 sum 汇总并输出。空列表为 0，保留重复项，允许零与负数。非法 JSON 或错误类型无输出，退出码 1。该课只验证聚合逻辑，不启动线程，支架已验证 data。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
