---
id: python-functions-iteration-type-hints
title: Python 类型注解
concepts: [types, functions]
objectives: [为函数参数和返回值添加类型注解, 理解注解不会替代运行时校验]
prerequisites: [python-functions-iteration-scope]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/python3/python-type-hints.html
source_snapshot_date: 2026-08-23
---

# 把接口意图写出来

类型注解说明函数期望接收和返回的值，便于编辑器和静态检查工具发现不一致。Python 运行时不会自动替你转换或拒绝参数，因此边界校验仍需要代码完成。

```python
def add(left: int, right: int) -> int:
    return left + right
print(add(1, 2))
```

注解应描述稳定的公共接口，而不是掩盖含糊的命名。

```python
def greeting(name: str) -> str:
    return f"Hello, {name}"
print(greeting("Hard"))
```

## 概念定义与适用场景

参数注解描述调用方应提供什么值，返回注解描述结果类型。它们支持编辑器与静态分析，但普通 Python 执行不会仅因参数写了 int 就拒绝字符串。

## 语法、API 与边界

add(left: int, right: int) -> int 仍需要真实的加法和 return。输入解析先把文本转换成整数，失败时按题意退出。挑战使用 greeting(name: str) -> str，非空校验同样由代码完成。

## 常见错误与实践建议

不要把注解当成类型转换，也不要写 int 返回注解却返回拼接的文本。运行成功只说明输出符合测试，不证明所有注解齐全或已通过静态检查；请另外核对函数签名。
