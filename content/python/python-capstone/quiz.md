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

规范化操作应明确改变哪些字符。本题只处理首尾空白和大小写，不压缩内部空格，也不把空文本误判为运行故障。

## 语法、API 与边界

读取全部文本，normalize(text) 去掉首尾空白并转成小写，打印结果，保留内部空格。中文不因大小写转换消失；空白输入输出一个换行，正常结束。

模块挑战：输入JSON对象，scores为整数列表（布尔值不算整数）。去重后计算count（不同分数数目）、passed（不低于60的不同分数数目）、total（不同分数之和），使用本地async协程和asyncio.run，输出json.dumps(sort_keys=True)结果。允许任意整数和空列表；结构或类型错误无输出，退出码1。只作离线汇总，不联网。

## 常见错误与实践建议

先验证结构和字段，再执行结果计算；使用题面中的正常值、边界值和不同输出分支核对行为。在线判题观察运行结果，不能据此推断已经完成真实外部服务集成。
