---
id: python-core-types-conversion
title: Python 数据类型转换
concepts: [types, variables]
objectives:
  - 使用 int、float 和 str 进行显式类型转换。
  - 在转换前识别可能无效的输入格式。
prerequisites: [python-core-types-data-types]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/python3/python3-type-conversion.html
source_snapshot_date: 2026-08-23
---

# 把数据变成需要的形状

输入通常先以文本到达程序。显式调用转换函数能把意图写出来，也让失败位置更容易定位。不要假设每段文本都能变成数字，先约定输入格式。

```python
text_count = "12"
count = int(text_count)
print(count + 1)
```

转换为字符串常用于组合展示信息；它不会改变原变量，只产生一个新值。

```python
score = 95
message = "Score: " + str(score)
print(message)
```

## 数值转换与文本解析的区别

`int`、`float` 和 `str` 分别构造整数、浮点数和文本。对数值调用 `int` 是向零截断，不能当成四舍五入；对字符串调用 `int` 要求符合整数文本规则，`"3.8"` 不会被自动截断。`float` 可以解析小数与指数文本，但浮点值通常是二进制近似值。

```python
print(int(3.8), int(-3.8))
print(float("2.5"), float("1e2"))
print(int("101", 2), int("0xff", 0))
print(str(12) + "1", 12 + 1)
```

预期输出：

```text
3 -3
2.5 100.0
5 255
121 13
```

指定 `base` 时输入应为字符串、字节串或字节数组，而不是已经是数值的浮点数。`int("12.0")` 触发 `ValueError`，`int(None)` 触发 `TypeError`；应分别判断输入格式错误和不支持的对象类型。`float("nan")` 和 `float("inf")` 可以成功，要求有限数值的业务还需使用 `math.isfinite` 另行验证。

## 容器转换、真假与字节编码

容器转换处理迭代元素：`list` 保留顺序，`set` 去重但不保证顺序，`tuple` 生成固定序列。它们通常不递归复制内部对象；字典转换则需要键值对。

```python
print(list("ab"), tuple([2, 3]))
print(sorted(set([3, 1, 3])))
print(dict([("name", "Lin"), ("level", 2)]))
print(bool("False"), bool(""))
text = "你好"
encoded = text.encode("utf-8")
print(type(encoded).__name__, encoded.decode("utf-8"))
```

预期输出：

```text
['a', 'b'] (2, 3)
[1, 3]
{'name': 'Lin', 'level': 2}
True False
bytes 你好
```

`bool` 检查真假，不解析文本里写的是 `"True"` 还是 `"False"`；解析配置布尔值应明确允许的字符串。`str(b"hi")` 返回字节串的展示形式，不等同于文本解码。`encode` 与 `decode` 要约定相同编码，解码错误不应悄悄忽略。不要用 `eval` 把输入当作代码执行来完成“转换”。

技术参考：[官方转换函数](https://docs.python.org/3.14/library/functions.html#int)、[文本与二进制序列](https://docs.python.org/3.14/library/stdtypes.html)。现有练习只接受可由 `int(text)` 解析的十进制整数文本，不能为了演示更宽泛转换而放宽练习输入。

## 概念定义与适用场景

int 把整数文本转换成可计算的整数，转换后的加一是数值运算。直接拼接字符串会把 12 变成 121，不能代替转换后的 13。

## 语法、API 与边界

本题先 strip 去掉首尾空白，再调用 int。零、负数和带正号的整数有效；空文本、字母和小数文本转换时触发 ValueError。失败分支必须在输出之前结束，并使用退出码 1。

## 常见错误与实践建议

可以用 try 包住 value = int(text)，在 except ValueError 中写 raise SystemExit(1)，成功后再计算。不要用 int(float(text)) 接受题目排除的小数，也不要把失败输入默认为零。
