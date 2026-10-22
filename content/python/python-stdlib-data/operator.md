---
id: python-stdlib-data-operator
title: Python operator
concepts: [operators, functions]
objectives: [使用 operator 表达基本运算, 选择可读的函数式操作]
prerequisites: [python-stdlib-data-builtins]
difficulty: intermediate
experience_points: 25
source_url: https://www.runoob.com/python3/python-operator.html
source_snapshot_date: 2026-08-23
---

# 具名运算

operator 将常用运算符提供为函数，适合传给排序和映射 API。它应提高调用的表达力，而非替代直观的普通表达式。

```python
import operator
print(operator.add(2, 3))
```

比较函数也返回布尔结果。

```python
import operator
print(operator.gt(3, 2))
```

## 概念定义与适用场景

operator 把运算符表示为可传递的函数，例如 operator.add 对应加法。需要把运算作为回调交给其他函数时，它比包装一层无意义函数更直接。

## 语法、API 与边界

add 的行为取决于参数类型，两个整数相加，两个字符串则拼接。支架先完成整数转换，确保这里表达的是数值加法；错误输入先退出。

## 常见错误与实践建议

不要用 operator.mul 或把整数重新转换为字符串。负数与零都是正常操作数；在线测试检查计算结果，不能单凭通过证明答案使用了指定 API。
