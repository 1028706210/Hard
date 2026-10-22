---
id: csharp-oop-operator-overloading
title: 运算符重载
concepts: [operator-overloading, operators]
objectives:
  - 用 public static operator 方法为自定义类型定义 + 运算符。
  - 区分运算符重载与方法重载的语法约束。
prerequisites: [csharp-oop-methods]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/csharp/csharp-operator-overloading.html
source_snapshot_date: 2026-08-23
---

# 运算符重载

## 概念定义与适用场景

运算符重载让自定义类型支持 `+` 这类运算符写法。向量、矩阵、金额这类"数学对象"用 `a + b` 表达求和，比调用 `Add(a, b)` 更接近问题本身的语言。

```csharp
struct Vector
{
    public long X;
    public long Y;

    public Vector(long x, long y)
    {
        X = x;
        Y = y;
    }

    public static Vector operator +(Vector left, Vector right)
    {
        return new Vector(left.X + right.X, left.Y + right.Y);
    }
}
```

## 语法、API 与边界

运算符重载必须声明为 `public static`，用 `operator` 关键字后跟运算符符号，至少一个参数是所在类型。定义 `operator ==` 时必须同时定义 `operator !=`，否则编译器报错。运算符重载与方法重载一样在编译期按操作数类型选择，与运行期多态无关。

```csharp
var a = new Vector(1, 2);
var b = new Vector(3, 4);
var sum = a + b;
Console.WriteLine(sum.X + " " + sum.Y);
```

## 常见错误与实践建议

把运算符重载写成实例方法、或漏掉 static 关键字，是两种最常见的编译错误。重载应保持直觉语义：向量 `+` 就该是分量相加，违反直觉的重载比没有重载更糟。本课练习只重载 `+`，并要求分量运算在 long 范围内完成。
