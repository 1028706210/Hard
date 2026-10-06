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

量化策略的离线回测边界解决的是把明确输入转换为可核验结果的问题。先识别数据的来源、所有权和生命周期，再选择最小的 Python API；这比先堆叠库调用更容易排错，也更容易在测试中复现。

## 语法、API 与边界

示例中的调用应只承担一个职责：准备输入、执行主题操作、检查输出。外部数据、空值、编码、资源关闭和异常路径都属于接口合同；不要把它们藏在偶然成功的默认行为里。

## 常见错误与实践建议

常见错误是把演示环境当成生产环境、跳过返回值检查，或用固定输出掩盖未处理的分支。实践时应使用小而可重复的输入，为失败路径写断言，并把网络、文件、GUI 或服务端依赖限制在可替换的边界之后。
