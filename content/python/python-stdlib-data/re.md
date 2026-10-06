---
id: python-stdlib-data-re
title: Python re 模块
concepts: [strings, functions]
objectives: [使用编译后的模式匹配文本, 选择 fullmatch 验证完整输入]
prerequisites: [python-stdlib-data-datetime]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-re.html
source_snapshot_date: 2026-08-23
---

# 可复用的文本规则

re 模块支持编译和复用模式。完整字段校验优先使用 fullmatch，避免局部匹配误认为整个输入有效。

```python
import re
pattern = re.compile(r"[a-z]+")
print(bool(pattern.fullmatch("hard")))
```

模式应限制为任务所需的最小范围。

```python
import re
print(bool(re.fullmatch(r"[0-9]{2}", "42")))
```


## 概念定义与适用场景

Python re 模块解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
