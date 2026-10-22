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

算术均值是所有样本之和除以样本数量，每一次观察都参与计算，重复值不能删除。它与中位数不同，极端值也会影响均值。

## 语法、API 与边界

statistics.mean 需要非空样本，单元素序列的均值就是该元素。支架验证整数与范围，输出使用 .2f 保留两位小数；这只是展示格式，不应先截断均值。

## 常见错误与实践建议

用 // 整除会丢失小数，使用 median 则计算了另一种统计量。空数据不能假装得到零，真实的 [0] 与空列表含义不同。
