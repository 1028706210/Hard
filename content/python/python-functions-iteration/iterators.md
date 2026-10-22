---
id: python-functions-iteration-iterators
title: Python 迭代器与生成器
concepts: [collections, functions]
objectives: [识别可迭代对象和迭代器的区别, 使用生成器逐步产生值]
prerequisites: [python-flow-collections-while-loop]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/python3/python3-iterator-generator.html
source_snapshot_date: 2026-08-23
---

# 按需取得下一个值

可迭代对象可被 `for` 遍历，迭代器负责给出下一个值。生成器函数通过 `yield` 延迟产生数据，适合不必一次保存全部结果的场景。

```python
for value in [1, 2]:
    print(value)
```

生成器的每次恢复都从上一次 `yield` 后继续。

```python
def steps():
    yield 1
    yield 2
print(list(steps()))
```

## 可迭代对象不等于迭代器

`iter(source)` 取得迭代器，`next(iterator)` 推进一个位置；耗尽后抛出 `StopIteration`，也可用 `next(iterator, default)` 提供结束值。列表可产生多个独立迭代器，迭代器本身通常只保存一次遍历的当前位置。

```python
values = [4, 7]
cursor = iter(values)
print(next(cursor))
print(list(cursor))
print(next(cursor, "end"))
print(list(values))
```

预期输出：

```text
4
[7]
end
[4, 7]
```

`for` 会取得迭代器并持续推进，在正常耗尽时结束循环。自定义迭代器通常实现 `__iter__` 返回自身，`__next__` 返回下一值或抛出 `StopIteration`。下面的类定义会在面向对象课展开；这里先观察协议，也可学完类后回读，不影响先使用列表和生成器。

```python
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        result = self.current
        self.current -= 1
        return result

cursor = Countdown(3)
print(list(cursor))
print(list(cursor))
```

预期输出：

```text
[3, 2, 1]
[]
```

## 生成器的暂停、耗尽与延迟计算

函数体包含 `yield` 后，调用函数先创建生成器；推进它才执行函数体。局部状态会跨暂停保存。普通 `return` 表示结束，生成器内部不应手动抛出 `StopIteration`，否则可能转成 `RuntimeError`。

```python
def squares(limit):
    for value in range(limit):
        print("produce", value)
        yield value * value

cursor = squares(3)
print("created")
print(next(cursor))
print(list(cursor))
```

预期输出：

```text
created
produce 0
0
produce 1
produce 2
[1, 4]
```

`(value * value for value in range(3))` 是生成器表达式，`[value * value for value in range(3)]` 立即构建列表。延迟计算可减少中间结果占用，但不保证整个程序恒定内存：若再调用 `list`，仍会保存所有结果；生成器引用的大对象也可能一直存活。无限生成器必须由调用方限制消费数量，不可直接 `list` 化。需要第二次遍历时应重新创建生成器，或在数据量可控时显式保存结果。

技术参考：[官方迭代器与生成器教程](https://docs.python.org/3.14/tutorial/classes.html#iterators)。现有练习仅检查同一生成器的首次消费与耗尽结果，不要求实现自定义迭代器类。

## 概念定义与适用场景

可迭代对象可以提供迭代器，迭代器保存当前消费位置。生成器是迭代器的一种，yield 暂停执行并交出一个值，下次继续时从暂停处恢复。

## 语法、API 与边界

调用 steps(n) 得到生成器对象，并不立即执行整个函数。第一次 list 消费全部值，第二次消费同一个对象得到空列表；重新调用 steps(n) 则创建新的对象。耗尽时 next 会抛出 StopIteration，for 和 list 会正常处理它。

## 常见错误与实践建议

本题必须保留同一个对象来观察一次性消费，不能两次调用 steps(n)。使用 return 提前返回会结束生成器，遗漏 yield 或 range 的右端点也会改变结果。
