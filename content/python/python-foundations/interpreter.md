---
id: python-foundations-interpreter
title: 在解释器中验证想法
concepts: [interpreter, variables]
objectives:
  - 使用交互式表达式快速验证一个小假设。
  - 知道临时会话变量不会自动成为项目代码。
prerequisites: [python-foundations-introduction]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-interpreter.html
source_snapshot_date: 2026-08-23
---

# 交互式会话适合短问题

解释器提示符允许你立刻计算一个表达式。它很适合确认字符串拼接、数字计算或内置函数的行为；当步骤需要保存、复用或测试时，应把代码放回 `.py` 文件。

```python
print(2 + 3)
```

交互式会话中的名称只在当前会话存在。重新启动后需要重新定义，这正是项目代码需要明确入口和测试的原因。

```python
name = "Hard"
print(name.lower())
```

把探索结果整理为短小函数，比保存一长串终端历史更容易复查。

## 概念定义与适用场景

交互式会话适合检查一个表达式；保存成程序后，输入可以变化而步骤保持不变。练习延续两数相加的例子，用不同输入确认程序没有依赖上次会话的状态。

## 语法、API 与边界

起始代码解析恰好两个整数，空白可以是空格或换行。输入无效时先退出，不能打印部分结果。零与负数都参与正常计算，不是失败标记。

## 常见错误与实践建议

不要只输出原例子的 15，也不要把两个字符串直接拼接。验证 7 与 8、两个零和两个负数，可以观察同一个表达式在不同输入上的行为。
