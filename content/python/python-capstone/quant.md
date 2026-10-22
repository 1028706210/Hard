---
id: python-capstone-quant
title: 量化策略的离线回测边界
concepts: [collections, functions, security]
objectives: [用固定价格 fixture 计算简单策略信号, 区分离线研究结果与真实下单行为]
prerequisites: [python-capstone-ai-draw]
difficulty: advanced
experience_points: 45
source_url: https://www.runoob.com/python3/python-qt.html
source_snapshot_date: 2026-08-23
---

# 回测不是交易

量化学习可以从可复现的数据处理开始。下面根据两日价格判断上升或持平；数据写在程序里，因此每次运行得到同一结果，不会访问行情或交易账户。

```python
prices = [10.0, 10.5]
signal = "buy" if prices[-1] > prices[-2] else "hold"
print(signal)
```

策略函数必须处理价格不足的边界，不能假装没有风险。真实下单还需要权限、风控和人工审核；这些能力不在 Runner 中，也不应由练习代码模拟为网络操作。

```python
def change(prices):
    if len(prices) < 2:
        return 0.0
    return prices[-1] - prices[-2]

print(change([8.0]))
```

离线结果只能说明该规则在给定 fixture 上如何计算，不能承诺收益，更不能替代投资决策。

## 概念定义与适用场景

本题只是相邻数值比较，不能把up解释为收益承诺或买入指令。应比较最后两项而不是首尾，也应对相等和数据不足给出明确结果。

## 语法、API 与边界

输入JSON非负整数价格列表，布尔值不算整数。signal(prices) 在至少两项且最后价格严格高于前一项时返回up，其他情况返回hold；空或单项列表为hold。打印结果。非法JSON、负数或错误类型无输出，退出码1。纯离线数列练习，不是交易建议，不下单。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
