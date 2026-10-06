---
id: python-modules-io-oop-modules
title: Python 模块
concepts: [functions, tooling]
objectives: [使用 import 引入模块能力, 区分模块公共接口和启动代码]
prerequisites: [python-functions-iteration-type-hints]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python3-module.html
source_snapshot_date: 2026-08-23
---

# 将代码组织为模块

模块是可导入的 Python 文件。导入公开函数能复用经过验证的逻辑；把启动行为放在入口守卫中，避免导入时发生意外副作用。

```python
import math
print(math.sqrt(9))
```

按需导入明确名称，能让调用来源容易追踪。

```python
from math import floor
print(floor(2.8))
```


## 概念定义与适用场景

Python 模块解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
