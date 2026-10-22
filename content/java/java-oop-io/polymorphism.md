---
id: java-oop-io-polymorphism
title: 多态
concepts: [polymorphism, inheritance]
objectives:
  - 掌握多态的核心概念与使用方式。
  - 用正常、边界和失败输入验证多态。
prerequisites: [java-oop-io-override-overload]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-polymorphism.html
source_snapshot_date: 2026-08-23
---

# 多态

## 概念定义与适用场景

多态让一段调用代码依赖共同的父类型或接口，处理不同的具体实现。变量的声明类型决定编译时可调用哪些成员，实际对象类型决定被重写的实例方法执行哪个版本。`Shape s = new Circle(2)` 不会把 Circle 变成 Shape 对象，也不会复制或删去子类数据。

例如面积汇总只需要 `area()`，调用者无需判断每个元素究竟是圆还是方形。新形状满足 Shape 契约后可以接入同一循环，但这并不保证所有需求变化都不需要修改调用者；输入解析或展示方式仍可能需要扩展。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `13`、`9`。接口方法的实现必须为 public，循环中的 shape 始终按 Shape 类型检查，调用时执行各自实现。

```java
interface Shape { double area(); }
class Circle implements Shape {
    private final double radius;
    Circle(double radius) { this.radius = radius; }
    public double area() { return Math.PI * radius * radius; }
    double radius() { return radius; }
}
class Square implements Shape {
    private final double side;
    Square(double side) { this.side = side; }
    public double area() { return side * side; }
}
public class Main {
    public static void main(String[] args) {
        Shape[] shapes = {new Circle(2), new Square(3)};
        for (Shape shape : shapes) System.out.println(Math.round(shape.area()));
    }
}
```

向上转型通常隐式完成，不要求强转。通过 Shape 引用不能直接调用 Circle 专有的 radius 方法，因为编译器只承诺 Shape 的成员。向下转型仅改变编译时的看待方式，运行时对象必须兼容，否则抛 `ClassCastException`。

第二个独立程序使用 JDK 17 的 instanceof 模式，输出 `5`、`not text`、`not text`。检查失败时不进入变量 text 的有效分支；null 也不匹配。将 Integer 强转为 String 不会把数字转成文字，需要字符串转换方法。

```java
public class Main {
    static void showLength(Object value) {
        if (value instanceof String text) {
            System.out.println(text.length());
        } else {
            System.out.println("not text");
        }
    }
    public static void main(String[] args) {
        showLength("hello");
        showLength(3);
        showLength(null);
    }
}
```

## 常见错误与实践建议

不要为已有共同实例方法反复写 instanceof 分支；多态能让行为随实现走。确实需要类型专有能力时，先检查类型再转换是合理的，不能一概禁止 instanceof。字段访问、static 方法和重载选择不遵循这里的运行时重写规则。

本课练习仍只接受 `circle 半径` 或 `square 边长`，输出四舍五入的面积整数。教学例子不改变原有输入校验及判题条件。本文扩展的向下转型、null 与数组中多实现分派，不等于已有面积输出测试已覆盖这些行为。

参考：[JLS 17 引用转换](https://docs.oracle.com/javase/specs/jls/se17/html/jls-5.html#jls-5.1.6)、[运行时方法选择](https://docs.oracle.com/javase/specs/jls/se17/html/jls-15.html#jls-15.12.4.4)。
