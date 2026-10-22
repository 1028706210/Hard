---
id: csharp-oop-structs
title: 结构体
concepts: [structs, memory]
objectives:
  - 用 struct 定义带字段和实例方法的轻量值类型。
  - 解释 struct 赋值复制整个值而 class 赋值共享引用。
prerequisites: []
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/csharp/csharp-struct.html
source_snapshot_date: 2026-08-23
---

# 结构体

## 概念定义与适用场景

struct 是值类型：把一个 struct 变量赋给另一个变量时，会复制整个数据。坐标点、金额、区间这类小而固定的数据组适合用 struct，复制成本通常较低；但若含引用字段，仍须考虑共享对象。

```csharp
struct Point
{
    public int X;
    public int Y;

    public Point(int x, int y)
    {
        X = x;
        Y = y;
    }

    public bool IsOrigin() => X == 0 && Y == 0;
}
```

## 语法、API 与边界

struct 不能从另一个 struct 或 class 继承，但可以实现接口。计算坐标差这类结果可能超出 int 范围的运算，应先把字段转换成 long 再参与运算。

```csharp
var a = new Point(1, 2);
var b = a;
b.X = 100;
Console.WriteLine(a.X);
Console.WriteLine(b.X);
```

### 复制的是字段值，不是递归复制整张对象图

struct 赋值会复制字段；字段如果是引用，复制的仍是同一引用。下面独立示例中，`Count` 各自保存，`Items` 却仍指向同一个列表：

```csharp
var first = new Snapshot { Count = 1, Items = new List<int> { 10 } };
var second = first;
second.Count = 2;
second.Items.Add(20);
Console.WriteLine(first.Count);       // 1
Console.WriteLine(first.Items.Count); // 2

struct Snapshot
{
    public int Count;
    public List<int> Items;
}
```

因此，“用 struct 就没有共享可变状态”不成立。小型、表示数值且适合复制的数据优先设计为不可变 `readonly struct`；有对象身份、需要共享修改的实体一般用 class。也不能用“struct 总在栈上、class 总在堆上”来判断语义：struct 可以是类对象或数组中的一部分，装箱后也存于托管对象中。语言层面的关键是值复制与引用复制。

`default(Point)` 使所有字段取得各自默认值，不调用用户定义的构造函数；现代 C# 允许声明公共无参 struct 构造函数，但 `default(T)` 和数组默认元素依然不能依赖它完成校验。`object boxed = point;` 对值类型装箱时保存一个副本，之后修改原值不会修改箱中的副本。

```csharp
int value = 3;
object boxed = value;
value = 9;
Console.WriteLine((int)boxed); // 3，拆箱类型必须与箱中实际类型匹配
```

本课练习只验证坐标值及计算；嵌套引用、装箱和默认初始化是本章的额外理解边界，并未由该练习自动证明。

## 常见错误与实践建议

把 struct 当 class 用是最常见的误判：修改 `b.X` 不会影响 `a`，因为赋值时已经复制。反之，如果类型包含大量字段或需要表达身份（同一个实体），应改用 class。防御溢出时先升级为 long 运算，而不是事后补救。本课练习通过方法返回计算结果，不依赖字段共享。

技术核对（2026-10-21）：[Microsoft Learn：struct](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/struct)。原 source_url 继续标识目录来源，本段链接用于语言事实核实。
