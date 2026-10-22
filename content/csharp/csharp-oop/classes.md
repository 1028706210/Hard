---
id: csharp-oop-classes
title: 类
concepts: [classes, memory]
objectives:
  - 用构造函数初始化对象状态并通过方法暴露行为。
  - 解释 class 的引用语义：两个变量可以指向同一个对象。
prerequisites: [csharp-oop-encapsulation, csharp-oop-methods]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-class.html
source_snapshot_date: 2026-08-23
---

# 类

## 概念定义与适用场景

class 把状态（字段）和行为（方法）组织成一个引用类型。`new` 表达式分配对象并运行构造函数，构造函数负责让对象一开始就处于合法状态。

```csharp
class Book
{
    private readonly string _title;
    private readonly int _price;

    public Book(string title, int price)
    {
        _title = title;
        _price = price;
    }

    public string GetTitle() => _title;

    public int GetPrice() => _price;
}
```

## 语法、API 与边界

class 变量保存的是引用：把变量赋给另一个变量后，两个名字指向同一个对象，通过任何一个修改都会被另一个看到。这一点与 struct 的复制语义正好相反。构造函数与类同名、不写返回类型，可以重载出多个版本。

```csharp
var first = new Book("CSharp", 100);
var second = first;
Console.WriteLine(ReferenceEquals(first, second));
```

### 对象身份、共享引用与按值传参

实例成员属于每个对象，`static` 成员属于类型；仅仅声明 `Book book;` 不会创建对象。赋值复制引用，而不是复制对象。下面是独立的顶级语句示例，先写执行语句，再写类型声明：

```csharp
var first = new CounterBox();
var second = first;
second.Value = 7;
Reset(second);
Console.WriteLine(first.Value);                    // 8
Console.WriteLine(ReferenceEquals(first, second)); // True

static void Reset(CounterBox box)
{
    box.Value++;             // 修改双方共享的对象
    box = new CounterBox();  // 仅替换参数中的引用副本
}

sealed class CounterBox
{
    public int Value;
}
```

普通参数传递的是变量值的副本；对于 class，该值恰好是引用。修改对象成员可以被调用方观察到，给参数重新赋值却不会替换调用方变量。只有确实需要替换调用方变量时才考虑 `ref` 参数，不能把“引用类型”当成“按引用传参”。

构造函数可以用 `this(...)` 复用本类另一构造函数；如果没有声明任何实例构造函数，普通类才由编译器补充默认无参构造函数。声明了带参数构造函数后，不能再假定 `new Book()` 合法。构造函数要校验必要的不变量，不能把“字段赋值完成”等同于“对象状态有效”。`readonly` 字段也可在字段初始化器中赋值；若字段保存可变对象的引用，readonly 只限制引用重新赋值，不会冻结对象。

本课练习聚焦构造函数保存参数和实例方法计算，不能检验所有共享引用、static 成员或参数重绑定规则；这些通过上例单独理解。

## 常见错误与实践建议

构造函数漏掉校验会让非法状态的对象流入系统，边界值（空标题、负价格）应在构造时就拒绝或规范化。`readonly` 实例字段只能在字段初始化器或声明它的类的实例构造函数中赋值，适合表达构造后不变的数据。本课练习用构造函数保存参数，用方法完成计算并输出。

技术核对（2026-10-21）：[Microsoft Learn：types](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/)；[Microsoft Learn：method-parameters](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/method-parameters)。原 source_url 继续标识目录来源，本段链接用于语言事实核实。
