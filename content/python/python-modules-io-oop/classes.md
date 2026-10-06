---
id: python-modules-io-oop-classes
title: Python 面向对象
concepts: [classes, functions]
objectives: [定义带状态和方法的简单类, 通过实例访问对象行为]
prerequisites: [python-modules-io-oop-exceptions]
difficulty: intermediate
experience_points: 40
source_url: https://www.runoob.com/python3/python3-class.html
source_snapshot_date: 2026-08-23
---

# 把状态和行为放在一起

类描述一组对象共享的状态与行为。构造函数建立实例状态，方法通过 `self` 读取该实例的数据；应让每个方法保持清晰职责。

```python
class Learner:
    def __init__(self, name):
        self.name = name
```

实例调用方法时，行为作用于自己的状态。

```python
class Learner:
    def greet(self):
        return "Hello"
print(Learner().greet())
```

## 概念定义与适用场景

类把相关状态和操作封装为对象；`__init__` 建立实例不变量，实例方法通过 `self` 读写该实例。适合有生命周期的实体，例如学习者、订单或文档，而不是为了给每个纯函数套一层名字。

## 语法、API 与边界

类属性由所有实例共享，实例属性由每个对象拥有；继承应表达真正的“是一个”关系。父类初始化通常用 `super()` 完成，方法返回值和可变属性要有明确合同。构造函数中不应启动网络、线程或不可回滚的副作用。

## 常见错误与实践建议

避免把可变默认值放在类属性上，避免子类绕过父类不变量。测试要创建至少两个实例确认状态隔离，并验证状态转换、继承重写以及无效构造参数的失败路径。
