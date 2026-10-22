---
id: python-modules-io-oop-classes
title: Python 面向对象
concepts: [classes, functions, methods, inheritance, polymorphism, encapsulation, operator-overloading]
objectives: [定义带状态和方法的简单类, 通过实例访问对象行为]
prerequisites: [python-modules-io-oop-exceptions]
difficulty: intermediate
experience_points: 40
source_url: https://www.runoob.com/python3/python3-class.html
source_snapshot_date: 2026-08-23
---

# 把状态和行为放在一起

类描述一组对象共享的状态与行为。`__init__` 在实例创建后初始化状态，方法通过 `self` 读取该实例的数据；应让每个方法保持清晰职责。

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

## 实例属性、类属性与方法绑定

`ClassName(...)` 创建实例，随后调用初始化方法 `__init__`；不要在其中返回另一个对象。`self` 是约定的形参名，`item.greet()` 会把 `item` 传入方法的第一个参数。类属性适合共享常量；每个对象自己的可变记录应在初始化时创建。

```python
class Notebook:
    category = "learning"

    def __init__(self, name):
        self.name = name
        self.notes = []

    def add(self, text):
        self.notes.append(text)

first, second = Notebook("A"), Notebook("B")
first.add("read")
print(first.category, first.notes, second.notes)
```

预期输出：

```text
learning ['read'] []
```

若把 `notes = []` 放在类体内，两个实例在没有同名实例属性时会找到同一个列表，向其中追加会产生共享状态。普通方法操作实例；`@classmethod` 的首参是类 `cls`，常用于替代构造入口；`@staticmethod` 不会自动接收实例或类，适合与类型紧密相关的独立工具，但简单工具也可直接写成模块函数。

## 继承、重写与多态

只有当子类确实能作为父类使用时，继承才合适；只是想复用一个对象的功能，可以把它作为属性组合进来。子类会继承未重写的属性，定义同名方法则重写父类行为。Python 按对象实际提供的方法调用，不要求先声明某个接口。

```python
class Learner:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, {self.name}"

class Mentor(Learner):
    def __init__(self, name, topic):
        super().__init__(name)
        self.topic = topic

    def greet(self):
        return f"{super().greet()} ({self.topic})"

for person in [Learner("Lin"), Mentor("Mei", "Python")]:
    print(person.greet())
print(isinstance(Mentor("Mei", "Python"), Learner))
```

预期输出：

```text
Hello, Lin
Hello, Mei (Python)
True
```

这展示了同一个 `greet()` 调用随对象类型而变化的多态。自定义子类初始化方法后，父类的初始化逻辑不会自动执行，应按需要显式调用 `super().__init__`。Python 不会按参数数量保留多个同名方法；在同一类体再次定义 `greet` 会替换之前的绑定，不等同于 Java/C# 的方法重载。

## 多继承与方法解析顺序

`class Child(Left, Right)` 允许多个基类。重名方法由方法解析顺序 MRO 决定，`super()` 从当前类之后沿实际实例类型的 MRO 查找下一实现，并不总表示“直接父类”。

```python
class Base:
    def route(self):
        return ["Base"]

class Left(Base):
    def route(self):
        return ["Left"] + super().route()

class Right(Base):
    def route(self):
        return ["Right"] + super().route()

class Child(Left, Right):
    pass

print([kind.__name__ for kind in Child.__mro__])
print(Child().route())
```

预期输出：

```text
['Child', 'Left', 'Right', 'Base', 'object']
['Left', 'Right', 'Base']
```

协作调用要求各实现兼容参数约定，并按需要继续调用 `super()`；某一层停止调用，后面的实现就不会运行。不要在菱形结构中手动逐个调用父类，容易重复执行共同基类。初学时优先单继承或组合，不为少量复用建立复杂继承树。

## 封装约定与特殊方法

`_name` 表示内部实现约定，外部仍可访问。`__name` 会进行名称改写，主要用于避免子类意外撞名，也不提供安全隔离；它与两侧都有双下划线的特殊方法不同。属性访问控制不能代替权限或输入校验。

特殊方法让自定义对象参与语言已有操作，例如 `str(obj)` 使用 `__str__`、`len(obj)` 使用 `__len__`、`a + b` 使用相应的运算协议。只在含义自然时才实现运算符重载，不必把每种操作都重写。

```python
class Points:
    def __init__(self, value):
        self.__value = value

    def __str__(self):
        return f"{self.__value} pts"

    def __add__(self, other):
        if not isinstance(other, Points):
            return NotImplemented
        return Points(self.__value + other.__value)

print(Points(2) + Points(3))
```

预期输出：

```text
5 pts
```

对不支持的操作数返回 `NotImplemented`，让解释器尝试其他运算分派；它不是要抛出的异常。若双方都不支持，表达式最终抛出 `TypeError`。`__str__` 必须返回字符串；`__repr__` 更适合开发者诊断。对象清理应使用上下文管理器，不依赖 `__del__` 的调用时机。

技术参考：[官方类教程](https://docs.python.org/3.14/tutorial/classes.html)、[对象与特殊方法协议](https://docs.python.org/3.14/reference/datamodel.html)。这些是独立教学示例，下面的现有练习只检查名称初始化与问候，不考查所有继承和运算协议。

## 概念定义与适用场景

类把状态和操作放在一起，__init__ 给每个实例建立自己的 name，greet 通过 self 读取当前对象的名称。只有存在需要一起管理的状态和行为时才需要类，不必给纯函数额外套壳。

## 语法、API 与边界

普通题的空名称使用 Learner，这是明确的默认规则。挑战输入恰好两行，分别创建两个对象，空白行也各自使用 Learner；对象创建完成后再按顺序问候，检查实例状态是否独立。

## 常见错误与实践建议

把 name 写成全局变量或在构造时不断修改类属性，可能使所有对象读取最后一个名称。挑战要使用两个不同名称来发现这种错误；自动判题检查结果，不证明所有面向对象设计都正确。
