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

Python 多线程解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
