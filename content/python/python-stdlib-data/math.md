---
id: python-stdlib-data-math
title: Python math
concepts: [operators, types]
objectives: [使用 math 的确定性数学函数, 区分取整与精确值]
prerequisites: [python-stdlib-data-operator]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-math.html
source_snapshot_date: 2026-08-23
---

# 明确数学意图

math 提供标准数学函数。选用函数前要说明精度和取整规则，避免把展示格式误当作计算值。

```python
import math
print(math.ceil(2.1))
```

平方根输入需要符合数学定义域。

```python
import math
print(math.sqrt(9))
```

## 概念定义与适用场景

sqrt 计算实数平方根，负数不在本题定义域内。math 使用浮点结果，展示保留三位小数并不表示内部计算只有三位精度。

## 语法、API 与边界

先验证非负整数，再调用 sqrt，最后用 .3f 格式化。与前面模块课一致，0 输出 0.000，非完全平方数需要保留小数，不能用整数截断。

## 常见错误与实践建议

平方根与平方、除以二不是同一运算。只使用 9 和 16 容易掩盖精度错误，因此本题公开包含 2，并检查零与上界。
