---
id: python-functions-iteration-scope
title: Python 命名空间与作用域
concepts: [variables, functions]
objectives: [区分局部和全局名称, 避免函数意外修改外层状态]
prerequisites: [python-functions-iteration-name-main]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/python3/python3-namespace-scope.html
source_snapshot_date: 2026-08-23
---

# 名称在边界内生效

函数内部创建的名称默认是局部名称，只在调用期间可见。优先用参数和返回值传递状态，能减少全局变量带来的隐藏依赖。

```python
value = "outer"
def show():
    value = "inner"
    return value
print(show())
```

同名名称在不同作用域中可以独立存在。

```python
name = "Hard"
def local_name():
    name = "Learner"
    return name
print(local_name())
```

## 从名称查找到闭包

命名空间保存名称到对象的绑定，作用域决定某处代码能按哪些规则查找它。函数中的普通名称通常按 LEGB 顺序查找：当前局部、包围它的函数、模块全局、内建。不要把变量命名为 `list`、`str` 或 `sum`，否则会遮蔽常用内建名称。

```python
label = "module"

def make_reader():
    label = "enclosing"

    def read():
        return label

    return read

reader = make_reader()
print(reader())
print(label)
```

预期输出：

```text
enclosing
module
```

内部函数即使在外层调用结束后仍可读取被捕获的绑定，这称为闭包。捕获的是绑定，不是函数定义时自动冻结的值；在循环里创建回调后统一调用，可能都读到同一个最终循环值。需要冻结每轮值时，可以在创建函数时用默认参数绑定它。

## 赋值、global 与 nonlocal

如果函数体中对一个名称赋值，且没有 `global` 或 `nonlocal` 声明，该名称通常在整个函数体中被视为局部名称，即使读取发生在赋值语句前面。此时不会退回模块查找，会抛出 `UnboundLocalError`。

```python
count = 10

def broken():
    count += 1

try:
    broken()
except UnboundLocalError:
    print("local name is unbound")
print(count)
```

预期输出：

```text
local name is unbound
10
```

`global count` 会把该函数中 `count` 的绑定目标指向所在模块。`nonlocal` 则修改最近一层已存在的外层函数绑定；它不能用来创建模块变量，也不能指向不存在的外层绑定。

```python
def make_counter():
    count = 0

    def next_count():
        nonlocal count
        count += 1
        return count

    return next_count

counter = make_counter()
print(counter(), counter())
```

预期输出：

```text
1 2
```

普通 `if`、`for` 和 `with` 不创建函数式的独立局部作用域；Python 3 的推导式循环变量通常有自己的作用域。类体的命名空间也不是实例方法的外层函数作用域，方法访问实例数据应写 `self.name`。优先传参和返回值，只有确实需要共享闭包状态时再使用 `nonlocal`。

技术参考：[官方命名空间与作用域说明](https://docs.python.org/3.14/tutorial/classes.html#python-scopes-and-namespaces)。本课练习只检查局部名称不会改写模块名称，上述闭包和声明是进一步的教学内容。

## 概念定义与适用场景

函数内赋值默认创建局部名称，局部 value 与模块 value 可以同时存在。名称查找通常遵循局部、外层函数、全局、内建顺序；同名不等于共享同一绑定。

## 语法、API 与边界

show 接收参数、创建局部 value 并返回它。模块随后读取自己的 value，应该仍为第一行输入。global 会改变赋值目标，本题不需要；nonlocal 用于外层函数绑定，也不是这里的模块场景。

## 常见错误与实践建议

只打印 show 的结果无法观察外层是否被意外修改，所以本题打印两行。测试两种不同名称，避免相同文本掩盖作用域错误；不要在赋值前读取尚未绑定的局部变量。
