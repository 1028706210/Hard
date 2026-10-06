---
id: python-capstone-examples
title: Python 实例：从需求到可验证程序
concepts: [functions, collections, control-flow]
objectives: [把自然语言需求拆成可测试的函数, 使用边界样本验证小程序的行为]
prerequisites: [python-automation-ui-web-markdown]
difficulty: advanced
experience_points: 35
source_url: https://www.runoob.com/python3/python3-examples.html
source_snapshot_date: 2026-08-23
---

# 实例不是答案仓库

一个有价值的实例先说明输入、输出和边界，再写实现。下面的 `label` 把分数分为三个等级；把等于阈值的情况写清楚，读者就不必猜测。

```python
def label(score):
    if score >= 80:
        return "通过"
    if score >= 60:
        return "补做"
    return "复习"

print(label(60))
```

实例也应避免悄悄修改调用方的数据。排序展示可以返回新列表，让原始记录仍可用于其他统计。

```python
scores = [72, 91, 72]
ranked = sorted(scores, reverse=True)
print(ranked)
print(scores)
```

写完后至少核对典型值、阈值和空输入。小函数的这些样本，就是以后重构时最可靠的护栏。


## 概念定义与适用场景

Python 实例：从需求到可验证程序解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
