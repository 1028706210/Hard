---
id: python-modules-io-oop-input-output
title: Python 输入和输出
concepts: [io, strings]
objectives: [用 print 生成可观察输出, 把外部文本在边界处转换为需要的类型]
prerequisites: [python-modules-io-oop-modules]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-inputoutput.html
source_snapshot_date: 2026-08-23
---

# 在边界处理文本

终端输入通常是字符串，输出应当表达给人的信息。先在输入边界检查和转换，再把内部逻辑保持为明确类型，能让错误更早出现。

```python
name = "Hard"
print(f"Hello, {name}")
```

格式化输出把标签和数据分开，便于阅读与测试。

```python
score = 90
print(f"Score: {score}")
```

## 概念定义与适用场景

标准输入提供文本，内部成绩则是整数。先解析与验证，再生成面向使用者的标签，可以避免把无效文本原样嵌入结果。

## 语法、API 与边界

f"Score: {n}" 把变量嵌入文本，冒号后有一个空格，print 在末尾添加换行。007 解析为整数 7；0 和 100 都合法，小数文本不符合本题整数约定。

## 常见错误与实践建议

忘记 f 会把花括号原样打印；输出额外的输入提示也会破坏约定。不要只打印 90 或沿用上一次输入，测试应改变成绩。
