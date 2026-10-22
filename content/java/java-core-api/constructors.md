---
id: java-core-api-constructors
title: 构造方法
concepts: [classes, functions]
objectives:
  - 掌握构造方法的核心 API 与使用方式。
  - 用正常、边界和失败输入验证构造方法。
prerequisites: [java-core-api-methods]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-constructor.html
source_snapshot_date: 2026-08-23
---

# 构造方法

## 概念定义与适用场景

构造方法参与建立对象的有效初始状态，名称必须与类名相同，不能声明返回类型，连 void 也不能写。`void Person()` 是普通方法，不是构造方法。`new Person(...)` 创建对象并选择相应构造，不能将构造当成普通方法再次调用。

只有完全没有声明构造方法时，编译器才会提供默认无参构造；声明了有参构造后，不会额外自动补无参版本。构造可重载，但不会被继承，也不会被重写。若父类无可访问的无参构造，子类必须显式选择可访问的父类构造。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `guest:0`、`Ada:18`。无参构造将默认值交给有参构造统一校验，避免两套初始化逻辑；`this.name` 是字段，右侧 name 是形参。

```java
class Person {
    private final String name;
    private final int age;
    Person() { this("guest", 0); }
    Person(String name, int age) {
        if (name == null || name.isBlank() || age < 0) {
            throw new IllegalArgumentException("invalid person");
        }
        this.name = name;
        this.age = age;
    }
    String describe() { return name + ":" + age; }
}
public class Main {
    public static void main(String[] args) {
        System.out.println(new Person().describe());
        System.out.println(new Person("Ada", 18).describe());
    }
}
```

本课程采用 Java 17：显式的 `this(...)` 或 `super(...)` 必须是构造体第一条语句；两者不能同时作为同一个构造体的显式调用。this 链最终要调用父类构造，不能循环调用自己。没有显式调用时，编译器尝试插入 `super()`，它不一定能通过访问和参数检查。

第二个独立程序输出 `base`、`field`、`body`，展示本例的初始化顺序。对象字段先获得默认值；父类构造完成后，才执行本类实例字段初始化和构造体其余语句。静态初始化属于另一层类初始化，不应与每个实例构造混为一谈。

```java
class Base {
    Base() { System.out.println("base"); }
}
class Child extends Base {
    int value = initialValue();
    private static int initialValue() {
        System.out.println("field");
        return 1;
    }
    Child() { super(); System.out.println("body"); }
}
public class Main {
    public static void main(String[] args) { new Child(); }
}
```

构造失败时可以抛异常，让调用者知道没有成功获得有效对象。不要在父类构造中调用可重写方法：它可能执行到子类实现，而子类字段尚未完成显式初始化。构造内可以使用不带值的 `return;` 提前结束，但不能返回一个值；通常让校验和赋值顺序清楚比提前 return 更易读。

## 常见错误与实践建议

不要把每个参数不加判断地复制到字段，也不要为了“方便”创建一个长期处于非法状态的空对象。初始化约束应跟实际业务一致；本节示例拒绝负年龄是教学模型，不是对既有练习增加新判题条件。

现有练习仅要求读取“名称 年龄”，构造 Person 后输出 `Name:名称 Age:年龄`。其原有测试与输入处理契约保持不变；构造链、初始化顺序和异常校验需要结合本文示例学习，不能仅凭练习通过声称已全部验证。

参考：[JLS 17 构造声明及默认构造](https://docs.oracle.com/javase/specs/jls/se17/html/jls-8.html#jls-8.8)、[实例创建过程](https://docs.oracle.com/javase/specs/jls/se17/html/jls-12.html#jls-12.5)。
