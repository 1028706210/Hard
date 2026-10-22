---
id: python-functions-iteration-functions
title: Python 函数
concepts: [functions, variables]
objectives: [定义带参数的函数, 用返回值传递计算结果]
prerequisites: [python-functions-iteration-with]
difficulty: beginner
experience_points: 35
source_url: https://www.runoob.com/python3/python3-function.html
source_snapshot_date: 2026-08-23
---

# 给可复用行为命名

函数将一段单一职责的行为命名。参数是函数的输入，`return` 让调用方接收结果；打印适合展示，而返回适合继续计算。

```python
def add(left, right):
    return left + right
print(add(2, 3))
```

明确的参数名比位置猜测更易读。

```python
def greet(name):
    return f"Hello, {name}"
print(greet("Hard"))
```


## 参数如何绑定

默认参数允许省略常用选项，关键字实参让调用意图更清楚。普通参数可按位置或名字传入；`/` 前的参数只能按位置传，`*` 后的参数只能按名字传。

```python
def format_score(name, /, score=0, *, suffix="pts"):
    return f"{name}: {score} {suffix}"

print(format_score("Lin"))
print(format_score("Mei", score=8, suffix="points"))
```

预期输出：

```text
Lin: 0 pts
Mei: 8 points
```

`format_score(name="Lin")` 因位置专用参数而失败，`format_score("Lin", 8, "pts")` 则因关键字专用参数而失败，都会抛出 `TypeError`。同一参数不能同时由位置和关键字重复提供。

`*args` 把额外的位置实参收集成元组，`**kwargs` 把额外的关键字实参收集成字典；名字可自选，星号决定语义。调用处的星号恰好用于展开已有容器。

```python
def total(*values, start=0):
    return start + sum(values)

values = [2, 3]
options = {"start": 10}
print(total(*values, **options))
```

预期输出：

```text
15
```

## 对象、默认值与返回值

实参传入的是对象，形参是指向该对象的局部名称。修改可变对象会被调用方观察到；给形参重新赋值只改变当前函数里的绑定。默认表达式在执行 `def` 时求值一次，不能把可变默认列表误当成“每次调用的新列表”。需要独立列表时使用 `None` 哨兵。

```python
def add_note(note, notes=None):
    if notes is None:
        notes = []
    notes.append(note)
    return notes

print(add_note("read"))
print(add_note("test"))
shared = []
print(add_note("code", shared), shared)
```

预期输出：

```text
['read']
['test']
['code'] ['code']
```

`return left, right` 返回的是一个元组，调用方可解包；没有 `return` 或只写 `return` 都会得到 `None`。不要将 `print` 的返回值当成计算结果。递归函数也必须有结束条件，每次调用要向结束条件推进；普通的长序列遍历通常直接用循环，Python 不保证尾递归优化。

技术参考：[官方函数定义与参数教程](https://docs.python.org/3.14/tutorial/controlflow.html#defining-functions)。本课现有加法练习只覆盖两个整数参数和返回值，不要求把所有参数形式引入答案。

## 概念定义与适用场景

定义函数时，`left`、`right` 是形参；调用 `add(2, 3)` 时，2、3 是实参。函数体只有调用时才执行。`return` 把值交给调用者并结束本次调用；如果只打印而没有返回，调用者拿到的是 `None`，不能把打印结果继续用于加法。

## 语法、API 与边界

本课练习把输入解析与计算分开：先用 `sys.stdin.read().split()` 分出两个值，用 `int` 转换后调用 `add`。整数可以为零或负数。不是恰好两个整数时，用 `raise SystemExit(1)` 结束；不要为非法输入打印伪造的计算结果。

## 常见错误与实践建议

不要写成 `print(left + right)` 却期待函数返回和；应写 `return left + right`，在调用处打印。用 2 与 3、0 与 -4 检查结果是否分别为 5、-4，再检查空输入与非整数能否被拒绝。不要把固定输出 5 当成加法函数。
