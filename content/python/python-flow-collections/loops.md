---
id: python-flow-collections-loops
title: Python 循环语句
concepts: [control-flow, collections]
objectives: [遍历一个有限集合, 在循环中维护清晰的单步动作]
prerequisites: [python-flow-collections-conditions]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-loop.html
source_snapshot_date: 2026-08-23
---

# 重复执行可验证的步骤

循环将同一动作应用到多个值。先确定数据来源和停止条件，再把循环体保持为最小的业务步骤。

```python
for item in ["a", "b"]:
    print(item)
```

计数变量要在每次循环中朝结束条件推进，避免无意的无限循环。

```python
count = 0
while count < 2:
    count += 1
print(count)
```

## 概念定义与适用场景

for 逐项取出有限序列的元素，循环体对每项执行同一动作。序列为空时循环体执行零次，这是正常完成，不需要伪造一个空元素。

## 语法、API 与边界

本题以空白切分名称，输出一个名称后换行。顺序和重复次数都是数据的一部分，不能排序或先转换为集合。计数型 while 则需要显式推进状态。

## 常见错误与实践建议

一次 print(items) 会输出列表表示形式；print(*items) 默认以空格连接，也不是逐行输出。重复项与空列表能发现这类输出格式错误。
