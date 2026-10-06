---
id: python-functions-iteration-decorators
title: Python 装饰器
concepts: [functions, tooling]
objectives: [理解函数可以作为对象传递, 用最小装饰器包装调用行为]
prerequisites: [python-functions-iteration-lambda]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/python3/python-decorators.html
source_snapshot_date: 2026-08-23
---

# 在调用外增加行为

装饰器接收函数并返回一个新函数。它适合日志、校验等横切行为，但包装层应保持透明，避免意外改变原函数的输入输出约定。

```python
def announce(func):
    def wrapped():
        return "run " + func()
    return wrapped
```

把小包装单独测试，可以确认它没有吞掉返回值。

```python
@announce
def task():
    return "task"
print(task())
```

## 概念定义与适用场景

装饰器是“接收可调用对象并返回可调用对象”的高阶函数，适合为多个函数统一附加计时、权限检查、缓存或审计等横切行为。它不应承担业务函数本身的决策，也不应悄悄改变调用方已经依赖的返回值合同。

## 语法、API 与边界

`@decorate` 等价于把函数交给 `decorate` 再绑定回来。包装器通常接收 `*args, **kwargs` 并把结果原样返回；`functools.wraps` 保留名称、文档和可检查的元数据。带参数的装饰器还多一层工厂函数，最容易在闭包变量捕获上出错。

## 常见错误与实践建议

避免在装饰器定义时执行昂贵操作，也不要吞掉底层异常后伪造成功。为包装前后各写一个断言：参数是否转发、返回值是否保留、异常是否仍能观察；这样日志或鉴权层不会替代核心行为。
