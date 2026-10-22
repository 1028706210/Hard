---
id: python-stdlib-data-random
title: Python random
concepts: [functions, collections]
objectives: [理解随机值用于模拟而非安全令牌, 在测试中固定随机来源]
prerequisites: [python-stdlib-data-math]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-random.html
source_snapshot_date: 2026-08-23
---

# 随机性需要边界

random 适合模拟和抽样，不适合安全凭据。测试应固定种子或注入随机源，保证结果可以复现。

```python
import random
random.seed(1)
print(random.randint(1, 1))
```

从有限候选项选择时要明确候选集合。

```python
import random
print(random.choice(["a"]))
```

## 概念定义与适用场景

固定种子让同一运行环境中的随机流程可复现。独立 Random 对象不会改变模块级随机状态，适合隔离不同实验。

## 语法、API 与边界

种子和候选顺序都会影响结果。只从单元素列表选择无法展示随机来源的作用，因此测试包含多个候选与不同种子；本题固定调用一次 choice。

## 常见错误与实践建议

不要硬编码首个候选，也不要在 choice 前额外消耗随机数。random 用于模拟，安全令牌应使用专门的安全随机接口。
