---
id: python-stdlib-data-random
title: Python random
concepts: [functions, collections]
objectives: [理解随机值用于模拟而非安全令牌, 在测试中固定随机来源]
prerequisites: [python-stdlib-data-math]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-random.html
source_snapshot_date: 2026-08-23
---

# 随机性需要边界

random 适合模拟和抽样，不适合安全凭据。测试应固定种子或注入随机源，保证结果可以复现。

```python
import random
random.seed(1)
print(random.randint(1, 1))
```

从有限候选项选择时要明确候选集合。

```python
import random
print(random.choice(["a"]))
```


## 概念定义与适用场景

Python random解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
