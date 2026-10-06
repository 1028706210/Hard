---
id: python-stdlib-data-regex-basics
title: Python 正则表达式基础
concepts: [strings, functions]
objectives: [使用 re 匹配简单文本模式, 避免把复杂正则隐藏在未命名字符串中]
prerequisites: [python-stdlib-data-overview]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python3-reg-expressions.html
source_snapshot_date: 2026-08-23
---

# 用模式描述文本形状

正则表达式适合固定格式的文本检查。把模式写成原始字符串，并为复杂规则补充样例，避免把业务含义埋进难读的符号组合。

```python
import re
print(bool(re.fullmatch(r"[0-9]+", "42")))
```

匹配失败是正常结果，应由调用方决定如何提示或恢复。

```python
import re
print(re.findall(r"[A-Z]", "Hard API"))
```


## 概念定义与适用场景

Python 正则表达式基础解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
