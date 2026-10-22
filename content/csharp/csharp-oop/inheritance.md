---
id: csharp-oop-inheritance
title: 继承
concepts: [inheritance, classes]
objectives:
  - 用基类派生新类并通过 base(...) 把构造参数传给基类。
  - 用 virtual 与 override 改写继承来的行为。
prerequisites: [csharp-oop-classes]
difficulty: intermediate
experience_points: 35
source_url: https://www.runoob.com/csharp/csharp-inheritance.html
source_snapshot_date: 2026-08-23
---

# 继承

## 概念定义与适用场景

继承让派生类自动获得基类的成员，并在其上追加或改写行为。多个类型共享同一套合同（例如都"有面积"）时，把公共部分放进基类，差异部分留给派生类。

```csharp
class Shape
{
    public virtual long Area() => 0;
}

class Rectangle : Shape
{
    private readonly long _width;
    private readonly long _height;

    public Rectangle(long width, long height)
    {
        _width = width;
        _height = height;
    }

    public override long Area() => _width * _height;
}
```

## 语法、API 与边界

C# 类只支持单继承，但可以逐层形成继承链。只有基类中标记为 `virtual`、`abstract` 或 `override` 的方法才能被 `override`；派生类构造函数用 `base(...)` 调用基类构造函数完成基类部分的初始化。

```csharp
class Square : Rectangle
{
    public Square(long side) : base(side, side)
    {
    }
}
```

### 继承的初始化与访问边界

一个类最多有一个直接基类，同时可以实现多个接口。派生对象包含基类的状态，但派生类代码不能直接访问基类 private 字段，应使用基类允许的 public/protected 成员。`protected` 允许派生类型按规则访问；它不是对所有调用者开放。`internal` 的边界是程序集，不能误读为“所有子类均可见”。

构造函数不被继承：派生构造函数先通过 `base(...)` 完成基类构造，再执行自己的构造函数体。省略 `base(...)` 时隐含调用基类无参构造函数；基类没有可访问的无参构造函数时必须显式传参。

```csharp
var item = new NamedItem("pen"); // 依次输出 base:pen、derived

class Item
{
    protected string Name { get; }
    public Item(string name)
    {
        Name = name;
        Console.WriteLine("base:" + name);
    }
}

sealed class NamedItem : Item
{
    public NamedItem(string name) : base(name) => Console.WriteLine("derived");
}
```

`sealed class` 阻止进一步派生；`sealed override` 只封闭某个已重写的虚成员。派生类可以用 `base.Method()` 调用可访问的基类实现。不要在构造函数中调用可重写成员：调用可能进入派生实现，而派生构造函数体尚未完成，状态可能不满足其假设。

把公共行为交给内部对象通常比为了几行复用建立继承链简单；只有调用方可以把派生对象安全当作基类使用时，继承关系才合理。本课面积练习只覆盖构造参数传递与 virtual/override，不覆盖所有访问修饰符组合。

## 常见错误与实践建议

给派生类写了一个与基类同名的方法却忘了 `override` 关键字，得到的是新方法而不是改写，多态调用时行为会不符合预期。继承表达的是"是一种"的关系；仅仅为了复用几行代码而继承会让类型层次失去意义。本课练习把公共校验逻辑留在调用侧，类型层次只负责面积计算。

技术核对（2026-10-21）：[Microsoft Learn：inheritance](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/object-oriented/inheritance)。原 source_url 继续标识目录来源，本段链接用于语言事实核实。
