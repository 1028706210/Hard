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

## 转发参数并保留函数身份

`@decorator` 在执行函数定义时应用，等价于把原函数传给装饰器，再将返回对象绑定到原名称；包装器的函数体则在后续调用时执行。装饰器不一定返回函数，但返回对象必须满足调用方的使用约定。

```python
from functools import wraps

def announce(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        return "run " + func(*args, **kwargs)
    return wrapped

@announce
def task(name, *, suffix="!"):
    return name + suffix

print(task("learn", suffix="?"))
print(task.__name__)
print(task.__wrapped__("learn"))
```

预期输出：

```text
run learn?
task
learn!
```

`*args` 和 `**kwargs` 让包装器接收并转发位置与关键字实参。`wraps` 维护名称、文档和 `__wrapped__` 等元数据，不负责参数校验、异常恢复或自动转发返回值。上例刻意只包装返回字符串的函数；对数值函数直接添加文本前缀会违反它的结果约定。

## 装饰器工厂与叠加顺序

带参数的装饰器多一层工厂：先接受配置，返回真正的装饰器，再接收函数。配置可由闭包保存，不需要额外的全局变量。

```python
from functools import wraps

def prefix(text):
    def decorate(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            return text + func(*args, **kwargs)
        return wrapped
    return decorate

@prefix("outer ")
@prefix("inner ")
def task():
    return "task"

print(task())
```

预期输出：

```text
outer inner task
```

这里先应用下方装饰器，再应用上方装饰器，即 `prefix("outer ")(prefix("inner ")(task))`。实际调用时先进入外层包装器。包装器若多次调用原函数，会重复其副作用；若捕获全部异常后返回默认值，会改变失败语义。缓存、重试、异步函数的包装还各有约束，不能用这个字符串包装器直接推导其正确性。

技术参考：[官方函数定义语义](https://docs.python.org/3.14/reference/compound_stmts.html#function-definitions)、[functools.wraps](https://docs.python.org/3.14/library/functools.html#functools.wraps)。现有练习仍只检查约定的文本前缀与函数名。

## 概念定义与适用场景

装饰器接收函数并返回包装后的函数，@announce 等价于 task = announce(task)。本题有意给返回值添加前缀，所以这是明确约定的行为变化，不能把任意返回值修改都称为透明包装。

## 语法、API 与边界

wraps(func) 将原函数的名称、文档等元数据复制到包装器，并设置 __wrapped__。包装器仍需显式转发参数与返回结果；wraps 本身不会帮你调用原函数。本题第二行打印 task.__name__ 来观察名称保留。

## 常见错误与实践建议

漏掉 wraps 常使函数名变成 wrapped，漏掉 return 会让调用方得到 None。__invalid__ 只是普通非空名称，没有特殊拒绝意义。自动判题观察输出与函数名，不等同于全面验证元数据和所有调用形式。
