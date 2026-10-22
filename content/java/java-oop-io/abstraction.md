---
id: java-oop-io-abstraction
title: 抽象类
concepts: [classes, inheritance]
objectives:
  - 掌握抽象类的核心概念与使用方式。
  - 用正常、边界和失败输入验证抽象类。
prerequisites: [java-oop-io-polymorphism]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-abstraction.html
source_snapshot_date: 2026-08-23
---

# 抽象类

## 概念定义与适用场景

抽象类以 `abstract class` 声明，不能直接 new，但可以作为变量类型。它适合表达同一类型家族的共同状态、初始化规则和部分实现。抽象方法只声明签名，由具体子类实现；抽象类也可以只有具体方法，用“不能直接实例化”表达设计意图，并非必须有抽象方法。

抽象类可拥有字段、构造方法、具体方法和静态方法。构造方法仍会在创建子类对象时参与初始化；不能因为父类抽象，就跳过它的状态约束。子类可以继续抽象，只有具体子类必须完成所有尚未实现的抽象方法。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `disk:13`。父类保存共同名称并提供 describe，子类只负责 area。具体方法调用抽象方法时仍进行实例方法动态分派。

```java
abstract class Shape {
    private final String name;
    Shape(String name) { this.name = name; }
    abstract double area();
    final String describe() { return name + ":" + Math.round(area()); }
}
class Circle extends Shape {
    private final double radius;
    Circle(String name, double radius) {
        super(name);
        if (radius < 0) throw new IllegalArgumentException("negative radius");
        this.radius = radius;
    }
    @Override double area() { return Math.PI * radius * radius; }
}
public class Main {
    public static void main(String[] args) {
        Shape shape = new Circle("disk", 2);
        System.out.println(shape.describe());
    }
}
```

`abstract` 方法不能同时是 private、static 或 final：这些修饰符与“由实例子类实现”冲突。抽象方法以分号结束；有方法体的普通方法不能仍标 abstract。抽象类可以实现接口，把部分行为留给子类。

第二个独立程序输出 `Meow!`，中间层 Animal 没有实现接口的 sound，但因其自身为 abstract 而合法。Cat 实现时要用 public，不能缩小接口方法的可见性。

```java
interface Vocal { String sound(); }
abstract class Animal implements Vocal {
    void greet() { System.out.println(sound() + "!"); }
}
class Cat extends Animal {
    public String sound() { return "Meow"; }
}
public class Main {
    public static void main(String[] args) { new Cat().greet(); }
}
```

抽象类与接口的选择应围绕关系：要共享实例状态、构造约束和家族实现时可用抽象类；仅需跨不同家族的行为契约时常用接口。一个类只能继承一个类，能实现多个接口。接口的 default 方法也能共享行为，但接口没有每个对象独立的实例字段。

## 常见错误与实践建议

不要写 `new Shape()`，应创建具体子类。共享算法调用可重写步骤时，要明确步骤的输入和输出契约；不要在构造过程中调用这些步骤，以免碰到子类未完成的初始化。final 的 describe 在本例固定描述格式，并不让整个对象自动不可变。

现有练习要求读取半径，通过抽象类计算圆面积，输出四舍五入整数。其原有测试并未覆盖抽象中间层、接口组合或所有非法修饰符；新增例子是教学扩展，未改变练习契约。

参考：[JLS 17 抽象类](https://docs.oracle.com/javase/specs/jls/se17/html/jls-8.html#jls-8.1.1.1)、[抽象方法](https://docs.oracle.com/javase/specs/jls/se17/html/jls-8.html#jls-8.4.3.1)。
