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

阈值必须写清是否包含端点。把判断放进函数便于用59与60直接比较，输入校验与分数判断分别负责不同边界。

## 语法、API 与边界

读取0到100（含端点）的整数成绩，定义passed(score)，不低于60返回True，否则False，打印返回值。非整数、空输入或越界无输出，退出码1。支架已提供n。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
