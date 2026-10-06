---
id: python-stdlib-data-logging
title: Python logging
concepts: [tooling, security]
objectives: [使用日志级别区分诊断重要性, 避免在日志中写入私密数据]
prerequisites: [python-stdlib-data-stringio]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-logging.html
source_snapshot_date: 2026-08-23
---

# 记录安全的诊断信息

日志用于理解运行状态，不应用来保存密码、隐藏测试或完整用户代码。级别应反映事件的可操作性，消息应当简洁且可搜索。

```python
import logging
logging.warning("retry planned")
```

结构化上下文只放安全标识。

```python
import logging
logging.info("lesson=%s", "python")
```


## 概念定义与适用场景

Python logging解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
