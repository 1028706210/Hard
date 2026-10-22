---
id: java-oop-io-inheritance
title: 继承
concepts: [inheritance, classes]
objectives:
  - 掌握继承的核心概念与使用方式。
  - 用正常、边界和失败输入验证继承。
prerequisites: [java-oop-io-exceptions]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-inheritance.html
source_snapshot_date: 2026-08-23
---

# 继承

## 概念定义与适用场景

`class Dog extends Animal` 声明 Dog 是 Animal 的一种，可在需要 Animal 的地方提供 Dog。一个类只能直接继承一个类，但可实现多个接口。继承应表达可替换的类型关系；“汽车有发动机”宜用字段组合，不宜让汽车继承发动机。只为少写两行而建立父子类通常得不偿失。

子类能使用哪些成员还取决于访问权限和所在包。父类 private 成员不会作为可访问成员被子类继承，但父类部分仍有自己的私有状态，可通过父类提供的方法访问。包级成员只在同包可访问；protected 的跨包访问还有接收者限制，不能理解为任何位置都公开。构造方法不被继承。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `Rex:Woof`、`.../Woof`。父类构造初始化父类状态，子类重写实例方法改变行为；`super.speak()` 明确调用父类版本，不会再次动态调回当前重写方法。

```java
class Animal {
    private final String name;
    Animal(String name) { this.name = name; }
    String getName() { return name; }
    String speak() { return "..."; }
}
class Dog extends Animal {
    Dog(String name) { super(name); }
    @Override String speak() { return "Woof"; }
    String compare() { return super.speak() + "/" + speak(); }
}
public class Main {
    public static void main(String[] args) {
        Dog dog = new Dog("Rex");
        System.out.println(dog.getName() + ":" + dog.speak());
        System.out.println(dog.compare());
    }
}
```

Java 17 子类构造若不显式写 super 或 this，会尝试隐式 `super()`；父类本例只有有参构造，所以删除 `super(name)` 会编译失败。`final` 类不能再扩展，`final` 实例方法不能重写，private 方法也不是供子类重写的扩展点。

字段隐藏与实例方法重写不同。第二个独立程序输出 `base`、`child`：表达式 `reference.label` 按变量声明类型选字段，`reference.describe()` 按实际对象选实例方法。

```java
class Base {
    String label = "base";
    String describe() { return label; }
}
class Child extends Base {
    String label = "child";
    @Override String describe() { return label; }
}
public class Main {
    public static void main(String[] args) {
        Base reference = new Child();
        System.out.println(reference.label);
        System.out.println(reference.describe());
    }
}
```

## 常见错误与实践建议

尽量不使用同名字段隐藏父类字段，它容易让调用者误以为字段也会动态分派。重写时加 `@Override`，让编译器发现签名拼错；不要在父类构造调用可重写方法。`super` 是访问父类实现的语法，不是另造一个父类对象。

现有练习仍要求读取名称，用 Dog 输出 `Dog:名称:Woof`；其判题主要观察结果。本文还讲访问边界、构造衔接和字段隐藏，不代表原题已对这些子知识点全部验收。

参考：[JLS 17 类成员和继承](https://docs.oracle.com/javase/specs/jls/se17/html/jls-8.html#jls-8.2)、[访问控制](https://docs.oracle.com/javase/specs/jls/se17/html/jls-6.html#jls-6.6)。
