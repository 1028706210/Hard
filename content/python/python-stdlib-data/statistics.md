---
id: python-stdlib-data-statistics
title: Python statistics
concepts: [collections, functions]
objectives: [计算一组数的均值, 在聚合前检查数据是否为空]
prerequisites: [python-stdlib-data-random]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-statistics.html
source_snapshot_date: 2026-08-23
---

# 先确认数据样本

statistics 提供常见统计函数。空样本和异常值需要由调用方按业务规则处理，不能用看似合理的默认值掩盖数据问题。

```python
import statistics
print(statistics.mean([1, 3]))
```

中位数不受极端值影响的方式与均值不同。

```python
import statistics
print(statistics.median([1, 9, 2]))
```


## 概念定义与适用场景

Python statistics解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
