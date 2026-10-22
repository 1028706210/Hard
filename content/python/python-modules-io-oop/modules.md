---
id: python-modules-io-oop-modules
title: Python 模块
concepts: [functions, tooling]
objectives: [使用 import 引入模块能力, 区分模块公共接口和启动代码]
prerequisites: [python-functions-iteration-type-hints]
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/python3/python3-module.html
source_snapshot_date: 2026-08-23
---

# 将代码组织为模块

模块是可导入的 Python 文件。导入公开函数能复用经过验证的逻辑；把启动行为放在入口守卫中，避免导入时发生意外副作用。

```python
import math
print(math.sqrt(9))
```

按需导入明确名称，能让调用来源容易追踪。

```python
from math import floor
print(floor(2.8))
```

## 概念定义与适用场景

import math 引入标准库模块，math.sqrt 清楚标明函数来源。模块是组织可复用能力的单位，不必安装第三方库来求平方根，也不应把本地脚本命名成 math.py 造成名称混淆。

## 语法、API 与边界

sqrt 返回浮点结果，本题用 .3f 固定小数位数，因此零输出 0.000，非完全平方数按格式规则舍入。输入限制为非负整数，避免在实数平方根运算中传入负数。

## 常见错误与实践建议

平方根不是平方，也不是整除。不要用 int 把结果截断；2 的结果能发现只测试完全平方数时看不见的问题。成功输出不能证明一定使用了 import，语法仍需学习者核对。
