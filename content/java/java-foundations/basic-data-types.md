---
id: java-foundations-basic-data-types
title: Java 基本数据类型
concepts: [variables, control-flow, types]
objectives:
  - 解释int、boolean、char 与范围在 Java 程序中的作用。
  - 用正常、边界和失败输入验证Java 基本数据类型。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-basic-datatypes.html
source_snapshot_date: 2026-08-23
---

# Java 基本数据类型

## 概念定义与适用场景

Java 的八种基本类型是 `byte`、`short`、`int`、`long`、`char`、`float`、`double`、`boolean`。类、接口、数组属于引用类型；`String` 不是基本类型。类型决定可表示的值、可执行的操作以及赋值是否兼容，不能只按“占多少内存”选择类型。

| 类型 | 值域或用途 |
| --- | --- |
| byte / short / int / long | 8 / 16 / 32 / 64 位有符号整数，范围均为 -2^(位数-1) 到 2^(位数-1)-1 |
| char | 0 到 65535 的无符号 UTF-16 代码单元 |
| float / double | 32 / 64 位二进制浮点值，有限精度，另有无穷与 NaN |
| boolean | 仅 true、false，不能与数字互转；语言规范不规定其存储大小 |

`long` 字面量通常加 `L`，`float` 字面量加 `F`，如 `3_000_000_000L`、`1.5F`。单引号声明 `char`，双引号声明 `String`。部分 Unicode 字符需要两个 char，不能把字符串长度一律解释为用户看到的字符数。

## 语法、API 与边界

扩大转换通常无需强制转换，例如 `int` 到 `long`；但扩大不保证精度完全保留，`int` 到 `float` 可能舍入。缩小转换通常要写 `(目标类型)`；它不负责业务范围校验。以下独立 `Main.java` 程序依次输出 `2147483648`、`-2147483648`、`16777216`、`3`。

```java
public class Main {
    public static void main(String[] args) {
        long wide = 2147483648L;
        int narrowed = (int) wide;
        int precise = 16777217;
        float rounded = precise;
        System.out.println(wide);
        System.out.println(narrowed);
        System.out.println((int) rounded);
        System.out.println((int) 3.9);
    }
}
```

整数缩小可能丢失高位；有限且在目标范围内的浮点数转整数向零截断，不是四舍五入。将 long 放入 int 前，应先比较 `Integer.MIN_VALUE`、`Integer.MAX_VALUE`，再转换。赋值还允许某些可表示的常量直接缩小，例如 `byte b = 10`，不能推导出任意 int 变量都能直接赋给 byte。

表达式先按操作数的类型计算，再赋给目标。下面第二个独立程序输出 `-1794967296`、`2500000000`、`2`、`2.5`；将已溢出的 int 结果赋给 long 不会恢复原值。

```java
public class Main {
    public static void main(String[] args) {
        int a = 50_000;
        long tooLate = a * a;
        long correct = (long) a * a;
        System.out.println(tooLate);
        System.out.println(correct);
        System.out.println(5 / 2);
        System.out.println(5 / 2.0);
    }
}
```

`byte`、`short`、`char` 参与常见算术运算时通常提升为 int，故 `byte a = 1; byte b = a + 1;` 不能直接编译。数值类型有固定范围，整数溢出通常不会自动抛异常；需要检测时可选 `Math.addExact` 等方法。二进制浮点不能精确表示很多十进制小数，金额应按需求使用整数最小货币单位或 `BigDecimal`。

## 常见错误与实践建议

包装类型 `Integer` 等是引用类型，可用于泛型；装箱把基本值变成包装对象，拆箱提取数值。`Integer boxed = null; int n = boxed;` 会在拆箱时抛 `NullPointerException`，不能将包装类型当作总有数值的 int。`==` 比较包装对象引用也不是可靠的数值比较。

本课练习仍是读取 long 范围整数，判断能否无损放入 int，输出 `true` 或 `false`；long 越界、非整数和空输入无输出并以退出码 1 结束。它不要求实现所有类型转换，也不覆盖浮点误差和拆箱异常。

参考：[JLS 17 类型和值](https://docs.oracle.com/javase/specs/jls/se17/html/jls-4.html)、[转换与数值上下文](https://docs.oracle.com/javase/specs/jls/se17/html/jls-5.html)。
