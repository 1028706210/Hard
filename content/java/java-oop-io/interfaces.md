---
id: java-oop-io-interfaces
title: 接口
concepts: [classes, polymorphism, interfaces]
objectives:
  - 掌握接口的核心概念与使用方式。
  - 用正常、边界和失败输入验证接口。
prerequisites: [java-oop-io-encapsulation]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-interfaces.html
source_snapshot_date: 2026-08-23
---

# 接口

## 概念定义与适用场景

接口用 `interface` 定义可依赖的行为契约，类用 `implements` 承诺实现。接口让不属于同一类家族的对象也能被统一调用，例如加法和减法都可视为 Calculator。具体类必须提供尚未由继承或默认实现完成的抽象方法；抽象类可以留待具体子类实现。

普通接口方法 `int calc(int a, int b);` 隐含 public abstract，具体实现必须 public。接口字段隐含 public static final，属于常量而非实例状态。接口可 extends 多个接口，类可 implements 多个接口，但类仍只能 extends 一个父类。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `7`、`-1`。调用者依赖 Calculator，具体算法由实现类负责；这比在调用处散布操作字符串判断更适合行为有多处调用的场景。

```java
interface Calculator { int calc(int a, int b); }
class Add implements Calculator {
    public int calc(int a, int b) { return a + b; }
}
class Subtract implements Calculator {
    public int calc(int a, int b) { return a - b; }
}
public class Main {
    public static void main(String[] args) {
        Calculator[] operations = {new Add(), new Subtract()};
        for (Calculator operation : operations) {
            System.out.println(operation.calc(3, 4));
        }
    }
}
```

Java 17 接口并非“只能声明签名”。Java 8 起支持带方法体的 default 实例方法和 static 方法，Java 9 起可有 private 辅助方法。static 方法按接口名调用，不通过实例继承；private 方法供接口内部复用，不是实现类的公共能力。

第二个独立程序输出 `Hello, Ada`、`2`。Printable 的 default 方法调用抽象的 text，再调用 private format；静态 version 独立于对象状态。

```java
interface Printable {
    String text();
    default String print() { return format(text()); }
    private String format(String value) { return "Hello, " + value; }
    static int version() { return 2; }
}
class Label implements Printable {
    public String text() { return "Ada"; }
}
public class Main {
    public static void main(String[] args) {
        System.out.println(new Label().print());
        System.out.println(Printable.version());
    }
}
```

如果两个无继承关系的接口提供同签名 default 方法，实现类通常必须显式重写以消除冲突；重写中可用 `First.super.method()` 选择某个直接父接口默认实现。父类的可继承具体实例方法优先于接口默认方法。默认方法不能解决所有多继承设计问题，更不提供多份父类实例状态。

只有一个抽象方法契约的函数式接口可作为 Lambda 目标；default、static 和 private 方法不因此增加抽象方法数量。后续 Java 8 课会使用这项能力，本课不把 Lambda 作为完成练习的前置要求。

## 常见错误与实践建议

不要漏写实现方法的 public，也不要给简单接口取与 JDK 标准类型冲突的名字，例如把求最大值工具命名为 Comparable。不要为所有类机械创建接口；出现明确的替换实现或调用边界时再引入。默认方法要保持契约一致，不能任意改变原有调用语义。

现有练习仍读取 `add a b` 或 `sub a b` 并输出结果。它没有要求新增接口版本号、格式化输出、默认方法冲突处理；输出测试也不能单独证明使用了接口多态。

参考：[JLS 17 接口成员与方法](https://docs.oracle.com/javase/specs/jls/se17/html/jls-9.html#jls-9.4)、[函数式接口](https://docs.oracle.com/javase/specs/jls/se17/html/jls-9.html#jls-9.8)。
