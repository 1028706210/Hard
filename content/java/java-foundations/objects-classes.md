---
id: java-foundations-objects-classes
title: Java 对象和类
concepts: [variables, control-flow, classes]
objectives:
  - 解释字段、方法和对象状态在 Java 程序中的作用。
  - 用正常、边界和失败输入验证Java 对象和类。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-object-classes.html
source_snapshot_date: 2026-08-23
---

# Java 对象和类

## 概念定义与适用场景

类定义一种对象有哪些状态和行为；对象是类的一个实例。`Learner` 是类型，`new Learner("Ada")` 创建实例，变量 `first` 保存该实例的引用。字段保存状态，方法读取或改变状态，构造方法负责初始化。不要把类、对象和引用变量当成三个同义词。

实例字段每个对象各有一份；`static` 字段属于类，在同一运行时类的实例间共享。姓名应属于学员实例，总人数才可能属于类。实例方法中的 `this` 指向当前对象，`this.name = name` 左边是字段、右边是参数。静态方法没有当前实例，不能直接使用 `this`。

## 语法、API 与边界

以下两个程序分别保存为 `Main.java`，在 JDK 17 下独立运行。第一个输出 `Hello, Ada`、`Hello, Lin`、`2` 三行，说明独立姓名和共享计数可以同时存在。

```java
class Learner {
    private final String name;
    private static int count;
    Learner(String name) { this.name = name; count++; }
    String greet() { return "Hello, " + name; }
    static int count() { return count; }
}
public class Main {
    public static void main(String[] args) {
        Learner first = new Learner("Ada");
        Learner second = new Learner("Lin");
        System.out.println(first.greet());
        System.out.println(second.greet());
        System.out.println(Learner.count());
    }
}
```

赋值引用不会复制对象。下面 `alias` 和 `original` 指向同一个 `Counter`，修改后输出 `7`。`original = null` 只改变该变量，`alias` 仍可访问原对象，第二行仍是 `7`。垃圾回收并不按某一个变量是否为 null 判断对象能否回收，而要看对象是否仍可达。

```java
class Counter { int value; }
public class Main {
    public static void main(String[] args) {
        Counter original = new Counter();
        Counter alias = original;
        alias.value = 7;
        System.out.println(original.value);
        original = null;
        System.out.println(alias.value);
    }
}
```

`new Counter()` 创建对象并调用构造；只写 `Counter c;` 不创建对象，而且局部变量未赋值前不能读取。引用可以为 `null`，调用其实例方法或访问字段会抛出 `NullPointerException`。基本类型赋值复制数值，引用类型赋值复制引用，二者都不是隐式深拷贝。

## 常见错误与实践建议

不要将每个学员的姓名声明为 `static`，也不要因为引用为 `final` 就认定对象内部永远不变。先建立有效初始状态，再通过有意义的方法提供行为；不需要为每个字段机械增加 setter。将对象传给方法时，传入的也是引用值的副本，方法能修改它指向的对象，但重新绑定参数不会重绑调用者变量。

本课练习仍只读取恰好两个名称，创建两个 `Learner` 后按顺序输出问候；名称字段必须独立。不是两个名称时无输出并以退出码 1 结束。新增的共享计数、别名和 null 讲解不属于该练习的额外输出要求，练习通过也不能证明所有对象生命周期知识已掌握。

参考：[JLS 17 对象和引用](https://docs.oracle.com/javase/specs/jls/se17/html/jls-4.html#jls-4.3.1)、[字段与方法](https://docs.oracle.com/javase/specs/jls/se17/html/jls-8.html#jls-8.3)。
