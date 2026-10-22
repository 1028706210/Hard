---
id: python-flow-collections-for-loop
title: Python for 循环
concepts: [control-flow, collections]
objectives: [用 for 遍历序列, 使用 range 构造有限次数的循环]
prerequisites: [python-flow-collections-data-structures]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-for.html
source_snapshot_date: 2026-08-23
---

# 按元素或次数遍历

`for` 适合已知序列和有限范围。循环变量只代表当前元素；不要依赖它在循环结束后仍承担原来的业务含义。

```python
for letter in "Hi":
    print(letter)
```

`range` 产生一个受控的整数序列，终点本身不包含在内。

```python
for index in range(3):
    print(index)
```

## 概念定义与适用场景

range(n) 给出从零开始的 n 个整数，但不包含 n 本身。for 每次把其中一个整数赋给 index，因此循环次数和输出行数一致。

## 语法、API 与边界

本题把 n 限定在 0 到 100，避免过量输出。range(0) 是空序列，程序应成功结束而不打印空行；输入无效则按支架退出。

## 常见错误与实践建议

range(n + 1) 会多出一行，range(1, n) 会丢掉零。用 n=0 与 n=1 检查两个最小情况，再检查较长序列的末尾。
