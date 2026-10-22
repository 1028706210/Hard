---
id: java-oop-io-override-overload
title: Override 与 Overload
concepts: [polymorphism, functions]
objectives:
  - 掌握Override 与 Overload的核心概念与使用方式。
  - 用正常、边界和失败输入验证Override 与 Overload。
prerequisites: [java-oop-io-inheritance]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-override-overload.html
source_snapshot_date: 2026-08-23
---

# Override 与 Overload

## 概念定义与适用场景

重载是在可见的方法集中出现同名但参数表不同的方法，不限于“同一个类内”；继承来的方法也可能参与重载。编译器根据方法名、实参的编译期类型等选择适用签名。仅改变返回类型不能构成重载，参数名字不同也不能区分签名。

重写是子类为继承的实例方法提供新实现。选定实例方法签名后，运行时再按接收者的实际类型决定执行哪个重写版本。因此“编译时重载选择”和“运行时实例方法分派”要分开判断。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `sub-object`、`sub-string`。第一次实参 text 的声明类型是 Object，即使内容是 String，也先选 `show(Object)`；接收者实际为 Sub，故运行 Sub 的 Object 版本。

```java
class Base {
    String show(Object value) { return "base-object"; }
    String show(String value) { return "base-string"; }
}
class Sub extends Base {
    @Override String show(Object value) { return "sub-object"; }
    @Override String show(String value) { return "sub-string"; }
}
public class Main {
    public static void main(String[] args) {
        Base printer = new Sub();
        Object text = "hi";
        System.out.println(printer.show(text));
        System.out.println(printer.show("hi"));
    }
}
```

重写的参数类型必须满足相应签名规则；返回引用类型可协变为更具体的类型，返回基本类型不能任意改变。不能缩小访问权限，也不能扩大受检异常的允许范围。static 方法是隐藏而非实例重写，private 方法不是重写目标，final 方法禁止重写。

第二个独立程序输出 `long`、`integer`，说明简单的基本类型扩大转换可比装箱更先适用。不要用大量相近的重载制造调用歧义。

```java
public class Main {
    static String choose(long value) { return "long"; }
    static String choose(Integer value) { return "integer"; }
    public static void main(String[] args) {
        System.out.println(choose(1));
        System.out.println(choose(Integer.valueOf(1)));
    }
}
```

若同时定义 `show(String)` 和 `show(Integer)`，调用 `show(null)` 没有唯一更具体的候选，会编译失败。若定义 `show(Object)` 和 `show(String)`，null 可选择更具体的 String 版本。强转实参可改变重载选择，但不应靠复杂强转来掩盖含糊的 API 设计。

## 常见错误与实践建议

重写时保留 `@Override`；如果把参数 String 改成 Object 而误以为还在重写，它能帮助发现错误。先看变量和实参声明类型，再看对象实际类型，不要只追踪运行时内容。不要用不同返回类型表达完全不同业务却保留同名同参方法。

现有代码练习只读取“类型 值”，int 输出 `number:值`、str 输出 `text:值`。这是一项方法分派的小练习，输出正确本身不能证明学员采用了重载，也不能验证协变返回、受检异常或 null 歧义；这些是正文扩展的学习边界。

参考：[JLS 17 重写与重载](https://docs.oracle.com/javase/specs/jls/se17/html/jls-8.html#jls-8.4.8)、[方法调用选择](https://docs.oracle.com/javase/specs/jls/se17/html/jls-15.html#jls-15.12)。
