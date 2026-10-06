---
id: python-capstone-quiz
title: Python 路线自测与诊断
concepts: [types, control-flow, exceptions]
objectives: [通过短题定位语言基础的薄弱点, 根据错误类型选择复习策略]
prerequisites: [python-capstone-examples]
difficulty: advanced
experience_points: 35
source_url: https://www.runoob.com/quiz/python-quiz.html
source_snapshot_date: 2026-08-23
---

# 自测的目标是诊断

测验不是背诵输出。面对一段代码，先追踪值的类型和分支条件。例如空列表的布尔值为假，所以可以用它表达“尚无记录”。

```python
records = []
message = "待录入" if not records else "已有记录"
print(message)
```

答错后应分类：语法错误先让程序可解析，类型错误检查输入契约，逻辑错误则补一个能暴露分支的样本。不要把异常吞掉，否则诊断信息会消失。

```python
def parse_count(text):
    try:
        return int(text)
    except ValueError:
        return None

print(parse_count("两"))
```

自测结果应转成下一步行动，例如复习集合去重、函数参数或异常分支，而不是只记录一个总分。

## 概念定义与适用场景

结业挑战把核心类型、集合、函数、异常、标准输入的文本数据和协程编排放到一个小型、可重复的任务中。它的目标是判断学习摘要，而不是输出预先背下来的固定文本。

## 语法、API 与边界

参考实现从 stdin 读取 JSON，先在函数中验证整数列表并去重，再在协程中计算通过数和总分，最后由 `asyncio.run` 输出稳定 JSON。空列表是合法边界；类型错误、格式错误和保留的无效输入应以失败状态结束。

## 常见错误与实践建议

不要把 JSON 解析、数据校验和汇总计算混在一行，也不要用固定打印绕过数据变化。测试普通重复分数、空列表和非法载荷；重试同一道题只能改善评分记录，不能伪造经验。
