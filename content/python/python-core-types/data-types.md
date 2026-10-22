---
id: python-core-types-data-types
title: Python 基本数据类型
concepts: [types, variables]
objectives:
  - 区分整数、浮点数、布尔值和字符串的基本用途。
  - 使用 type 函数观察一个值的运行时类型。
prerequisites: [python-core-types-basic-syntax]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-data-type.html
source_snapshot_date: 2026-08-23
---

# 值和类型一起工作

类型说明一个值可以参与哪些操作。整数适合计数，浮点数适合近似量，布尔值表达真假，而字符串保留文本。先看清值的类型，再决定怎样处理它。

```python
count = 3
ratio = 0.5
enabled = True
```

`type` 是观察工具，不是转换工具。它帮助我们验证变量是否拿到了预期的数据。

```python
label = "Hard"
print(type(label).__name__)
```

## 类型属于对象，名称绑定对象

除数字、布尔和文本外，常用类型还有列表 `list`、元组 `tuple`、字典 `dict`、集合 `set`、字节串 `bytes`，以及表示缺少结果的 `None`。变量名可以重新绑定不同类型的对象，并不意味着一个对象的类型随赋值而改变。

| 类型 | 典型用途 | 是否可变 |
| --- | --- | --- |
| `int`、`float`、`bool` | 计数、近似数值、真假 | 否 |
| `str`、`bytes` | Unicode 文本、原始字节 | 否 |
| `list`、`dict`、`set` | 可更新的序列、映射、唯一成员 | 是 |
| `tuple`、`frozenset` | 固定序列、不可变成员集合 | 否 |

`type(value)` 查看准确类型，`isinstance(value, Type)` 还接受子类。`bool` 是 `int` 的子类，所以检查“整数但不是布尔值”需要明确排除布尔；这也是本项目 JSON 输入校验中的常见边界。

```python
print(type(True).__name__, isinstance(True, int))
print(type(True) is int)
print(None is None, bool(None))
print(bool([]), bool("False"))
```

预期输出：

```text
bool True
False
True False
False True
```

空容器、空文本、数值零和 `None` 通常是假；非空的 `"False"` 是真。`None` 与 `0`、`False`、空列表表示不同的值，检查缺失结果时用 `is None`，不要一律写 `if not value`。

## 相等、同一对象与可变性

`==` 比较值是否相等，`is` 检查是否为同一个对象。赋值不会复制可变对象；两个名称引用同一个列表时，一处修改可由另一处观察到。不可变元组也可能引用可变列表，因此不可变不表示整个嵌套结构都被冻结。

```python
first = [1]
alias = first
copy = first.copy()
print(first == copy, first is copy, first is alias)
alias.append(2)
print(first, copy)
```

预期输出：

```text
True False True
[1, 2] [1]
```

别用 `is` 判断两个数字或字符串的值相等；解释器可能复用某些对象，这种实现现象不能当作程序契约。后续集合章节会进一步讨论浅复制及可哈希限制。

技术参考：[官方内建类型](https://docs.python.org/3.14/library/stdtypes.html)、[type 与 isinstance](https://docs.python.org/3.14/library/functions.html#isinstance)。下方现有练习特意只接受四种 JSON 标量，教学表格里的其他类型不会自动变成合法练习输入。

## 概念定义与适用场景

type(value).__name__ 返回 Python 类型名。字符串 "8" 和整数 8 外观相近，类型却不同；布尔值也有自己的 bool 类型。本练习观察值的类型，不做猜测或强制转换。

## 语法、API 与边界

练习用 JSON 作为传入值的格式：文本需要双引号，布尔值写 true 或 false。起始代码用 json.loads 安全解析并限制为 int、float、bool、str；这部分不要求自行实现，也不应改用 eval。空字符串 "" 是有效文本，而空输入不是一个值。

## 常见错误与实践建议

不要只输出示例的 str，也不要对尚未解析的原始输入调用 type，那样永远只能看到字符串。用整数、小数、布尔值和空字符串分别检查；列表、对象和 null 不属于本题接受的类型。
