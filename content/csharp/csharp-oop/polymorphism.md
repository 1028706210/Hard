---
id: csharp-oop-polymorphism
title: 多态
concepts: [polymorphism, inheritance]
objectives:
  - 通过基类引用的数组统一调用各派生类的 override 实现。
  - 区分运行期多态分派与编译期方法重载解析。
prerequisites: [csharp-oop-inheritance]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/csharp/csharp-polymorphism.html
source_snapshot_date: 2026-08-23
---

# 多态

## 概念定义与适用场景

多态让调用方只面向基类编程：同一个 `shape.Area()` 调用，运行期按对象的真实类型分派到 Rectangle 或 Square 的实现。新增一种形状时，调用侧的循环代码不需要改动。

```csharp
Shape[] shapes = { new Rectangle(2, 3), new Square(4) };
long total = 0;
foreach (var shape in shapes)
{
    total += shape.Area();
}
Console.WriteLine(total);
```

## 语法、API 与边界

多态分派发生在运行期，依据对象的实际类型；方法重载的选择发生在编译期，依据参数的静态类型，二者机制不同。派生类没有 override 时，virtual 调用会落到基类实现，不会报错，但这往往意味着遗漏。

```csharp
Base item = new Derived();
Console.WriteLine(item.Describe()); // derived

class Base
{
    public virtual string Describe() => "base";
}

class Derived : Base
{
    public override string Describe() => "derived";
}

```

### override、new 与 abstract 的可观察区别

`override` 接入已有虚方法的运行期分派；`new` 明确隐藏同名成员，按引用的静态类型选择成员。下面是一个可独立运行的完整对照：

```csharp
Animal animal = new Cat();
Console.WriteLine(animal.Speak());       // meow
Console.WriteLine(animal.Label());       // animal
Console.WriteLine(((Cat)animal).Label()); // cat

class Animal
{
    public virtual string Speak() => "sound";
    public string Label() => "animal";
}

class Cat : Animal
{
    public override string Speak() => "meow";
    public new string Label() => "cat";
}
```

把变量改成派生类型并不会让虚分派消失：调用虚成员时仍有运行期选择。基类类型的变量只是更直观地展示了“声明类型不同于实际类型”的作用。

当基类不能给出合理的默认行为时，用抽象成员强制具体派生类补全，避免 `Area() => 0` 掩盖遗漏：

```csharp
Figure figure = new UnitSquare();
Console.WriteLine(figure.Area()); // 1

abstract class Figure
{
    public abstract int Area();
    public string Unit => "square-unit";
}

sealed class UnitSquare : Figure
{
    public override int Area() => 1;
}
```

抽象类不能直接 `new`，但可以有字段、构造函数及完整实现，也允许没有抽象成员。抽象方法不写方法体、也不再写 virtual；具体派生类必须实现它，否则编译失败。重载则按参数列表和调用处的静态类型选择，与上述虚成员分派属于不同步骤。

本课现有练习使用 Shape 数组做虚方法面积汇总。abstract/new 示例用于辨析语义；练习合同没有改成要求抽象基类，也不能用通过汇总题证明掌握了成员隐藏。

## 常见错误与实践建议

基类引用最便于展示统一调用；派生类型变量调用虚方法时同样遵循虚分派规则。逐行解析外部输入时，任何一行非法都应让整体失败，而不是跳过后继续累计。本课练习用 Shape 数组承载混合类型并输出总和。

技术核对（2026-10-21）：[Microsoft Learn：polymorphism](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/object-oriented/polymorphism)；[Microsoft Learn：abstract](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/abstract)。原 source_url 继续标识目录来源，本段链接用于语言事实核实。
