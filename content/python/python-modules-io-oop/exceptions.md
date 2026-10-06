---
id: python-modules-io-oop-exceptions
title: Python 错误和异常
concepts: [exceptions, functions]
objectives: [用 try 和 except 处理可预期失败, 避免吞掉未知异常]
prerequisites: [python-modules-io-oop-os]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/python3/python3-errors-execptions.html
source_snapshot_date: 2026-08-23
---

# 只处理知道如何恢复的错误

异常表示正常流程之外的失败。捕获具体异常并给出明确恢复方式，比宽泛捕获所有错误更安全；未知失败应保留诊断路径。

```python
try:
    value = int("x")
except ValueError:
    value = 0
print(value)
```

`finally` 用于不论成功与否都要执行的有限清理动作。

```python
try:
    print("work")
finally:
    print("done")
```

## 概念定义与适用场景

异常表示当前函数不能按正常合同完成工作。`ValueError` 常用于值格式不合法，`KeyError` 常用于缺少映射键，`OSError` 常用于资源操作失败；把它们分开处理，调用方才能选择正确的恢复策略。

## 语法、API 与边界

`try` 包住最小可能失败的语句，`except SpecificError` 只恢复已知问题，`else` 放成功路径，`finally` 放必须清理的资源。可以用 `raise ... from error` 保留原因链；不要用裸 `except:` 吞掉取消、退出或程序错误。

## 常见错误与实践建议

“返回 0”只适用于业务明确规定的降级结果，不能拿来掩盖全部错误。为正常转换、可恢复格式错误和不可恢复错误分别写测试，并在日志中提供安全的上下文而不是私密输入。
