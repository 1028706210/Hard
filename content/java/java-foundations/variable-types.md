---
id: java-foundations-variable-types
title: Java 变量类型
concepts: [variables, control-flow]
objectives:
  - 解释局部变量、成员变量和生命周期在 Java 程序中的作用。
  - 用正常、边界和失败输入验证Java 变量类型。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-variable-types.html
source_snapshot_date: 2026-08-23
---

# Java 变量类型

## 概念定义与适用场景

这里的“变量类型”既要区分 int、String 等数据类型，也要区分变量出现的位置：实例字段属于每个对象，静态字段属于类，局部变量属于一次方法执行，形参接收一次调用传入的值。声明类型约束能存什么，声明位置决定作用域、初始化规则及共享方式。

字段和数组元素有默认值：数值为零、boolean 为 false、引用为 null；局部变量没有可直接读取的默认值，必须先确定赋值。块内声明的局部变量在块外不可见。对象可达性、资源是否关闭和局部名字的作用域是不同问题，不应将“离开大括号”理解为对象立刻销毁。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `0`、`6`、`5`、`2`。`this.value` 明确选择字段，构造参数 value 与字段同名也不会自动赋值；静态字段 created 在两个对象间共享。

```java
class Counter {
    int value;
    static int created;
    Counter() { created++; }
    Counter(int value) { this.value = value; created++; }
}
public class Main {
    public static void main(String[] args) {
        Counter empty = new Counter();
        Counter counter = new Counter(5);
        int value = 6;
        System.out.println(empty.value);
        System.out.println(value);
        System.out.println(counter.value);
        System.out.println(Counter.created);
    }
}
```

`final` 禁止变量再次赋值，不自动冻结对象。下面第二个独立程序输出 `[9, 2]`、`2`。若写 `values = new int[]{3};` 则编译失败，但修改原数组元素合法。

```java
import java.util.Arrays;
public class Main {
    public static void main(String[] args) {
        final int[] values = {1, 2};
        values[0] = 9;
        var size = values.length;
        System.out.println(Arrays.toString(values));
        System.out.println(size);
    }
}
```

JDK 17 的 `var` 可从初始化表达式推断局部变量的静态类型；此处 size 仍是 int，不是动态类型。它不能替代字段类型、普通方法形参类型，也不能写 `var x = null`。声明越靠近首次使用越容易检查初始化和作用域；是否使用 var 应以读者能否看清类型为准。

## 常见错误与实践建议

避免 `value = value` 这样的自赋值；需要赋给字段时写 `this.value = value`。不要为了让静态 main 访问方便，就把所有状态改成 static。引用局部变量已经初始化为 null，不表示可以调用其方法。`final` 也不提供可变对象的自动线程安全。

本课练习继续使用 Counter 保存输入 n，另声明 main 的局部 value 为 n+1，先输出局部值再输出字段值。范围是 -1000000 到 1000000；非法输入无输出、退出码 1。静态计数、var 和 final 数组只用于补充学习，不增加练习输出。

参考：[JLS 17 变量与初始值](https://docs.oracle.com/javase/specs/jls/se17/html/jls-4.html#jls-4.12)、[局部变量声明](https://docs.oracle.com/javase/specs/jls/se17/html/jls-14.html#jls-14.4)。
