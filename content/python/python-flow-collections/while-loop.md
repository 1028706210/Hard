---
id: python-flow-collections-while-loop
title: Python while 循环
concepts: [control-flow, operators]
objectives: [用 while 表达状态驱动的重复, 确保循环变量朝停止条件变化]
prerequisites: [python-flow-collections-for-loop]
difficulty: beginner
experience_points: 35
source_url: https://www.runoob.com/python3/python3-while.html
source_snapshot_date: 2026-08-23
---

# 直到状态改变

`while` 在条件为真时继续执行，适合停止时刻由状态决定的问题。循环体必须更新相关状态，并在设计时就说明退出条件。

```python
remaining = 2
while remaining > 0:
    remaining -= 1
print(remaining)
```

把状态更新放在容易看到的位置，有助于检查每轮循环都会前进。

```python
step = 0
while step < 3:
    step += 1
print(step)
```

## 概念定义与适用场景

while 在每轮之前检查条件；状态更新必须让条件最终变为假。从零递增到 n 的练习使用 count < n，并把输出放在循环之外。

## 语法、API 与边界

普通题只输出最终计数，挑战则逐行输出 1 到 n，包含 n。两题均只接受 0 到 100 的整数；n=0 时普通题输出 0，挑战没有任何输出。

## 常见错误与实践建议

把 < 写成 <= 会多执行一次；忘记更新变量可能造成无限循环。自动判题只检查行为结果，不证明一定使用了 while；练习时请自行核对循环写法，不能把成功状态当成语法使用证明。
