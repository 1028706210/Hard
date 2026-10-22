---
id: csharp-language-features-generics
title: 泛型（Generic）
concepts: [generics, classes]
objectives:
  - 声明泛型类与泛型方法，理解类型参数在编译期保证元素类型安全、取出无需强转。
  - "用 where T : IComparable<T> 这类约束让泛型代码调用类型实参的能力，并说明其相比 object 方案的优势。"
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-generic.html
source_snapshot_date: 2026-08-23
---

# 泛型（Generic）

## 概念定义与适用场景

泛型把"类型"变成类和方法的一个参数。写一个 `MyStack<T>`，栈里元素的类型由使用处决定：`new MyStack<int>()` 就只装整数，塞字符串直接编译失败。数据结构与算法因此只需实现一次，却在每个具体类型上保持完全的类型安全——这是 List<T>、Dictionary<TKey,TValue> 能够统一替代 object 容器的根本原因。

```csharp
sealed class MyStack<T>
{
    private readonly List<T> _items = new();

    public int Count => _items.Count;

    public void Push(T item) => _items.Add(item);

    public T Pop()
    {
        if (_items.Count == 0) throw new InvalidOperationException();
        var item = _items[^1];
        _items.RemoveAt(_items.Count - 1);
        return item;
    }
}
```

## 语法、API 与边界

类型参数写在类名或方法名后：`class MyStack<T>`、`T Pick<T>(List<T> source)`。约束用 `where` 声明，常用形式有 `where T : IComparable<T>`（可比较）、`where T : class`（引用类型）、`where T : new()`（有无参构造）。有了 `IComparable<T>` 约束，泛型代码内部就能直接调用 `a.CompareTo(b)` 实现与具体类型无关的"取最大值"。对比旧式 object 方案：值类型存入要装箱、取出通常要强转，类型错误拖到运行期才爆炸；泛型在编译期就把这些错误拦下，值类型还免去了装箱开销。泛型类型信息也保留在运行期，`List<int>` 与 `List<string>` 是不同的封闭类型，可用反射区分。

```csharp
static T MaxOf<T>(T first, T second) where T : IComparable<T> =>
    first.CompareTo(second) >= 0 ? first : second;
```

### 类型参数的能力由约束决定

没有约束的 T 不承诺具有 CompareTo 或无参构造函数；约束是给调用者和编译器的共同合同。泛型方法通常可从实参推断类型，返回类型本身不能代替参数提供这种推断。

```csharp
Console.WriteLine(PickLarger(4, 9));            // 9
Console.WriteLine(Same(3, 3));                  // True
Console.WriteLine(typeof(List<int>) == typeof(List<string>)); // False

static T PickLarger<T>(T left, T right) where T : IComparable<T> =>
    left.CompareTo(right) >= 0 ? left : right;

static bool Same<T>(T left, T right) =>
    EqualityComparer<T>.Default.Equals(left, right);
```

`where T : struct` 限制非可空值类型；`where T : class` 限制引用类型；`where T : new()` 要求非抽象类型具有公共无参构造函数，组合时放在约束列表末尾。没有实际 new T() 的需要，就不必添加构造约束。相等比较优先用 EqualityComparer<T>.Default，不应为调用一个通用比较器而强制所有类型实现某个接口。

泛型信息在 .NET 运行期仍然存在，可由反射检查；List<int> 与 List<string> 是不同的封闭类型。object 容器存引用类型时不会装箱，存值类型时才发生装箱；泛型集合保存其具体值类型元素通常避免该开销，但若又把 T 转为 object 或接口，仍可能装箱。“泛型永不装箱”并不成立。

另一个常见误判是认为继承关系能直接传递到所有泛型容器：即使 Cat 派生自 Animal，List<Cat> 也不能当作 List<Animal>，否则调用者便能把别的 Animal 放入猫列表。协变/逆变只适用于允许它的接口与委托，本课暂不展开其声明规则。

MyStack<T> 是学习类型参数的练习；日常栈需求应先考虑标准库 Stack<T>。现有练习只验证泛型栈命令及空栈路径，不证明已掌握约束、运行期类型或方差。

## 常见错误与实践建议

初学者常见的错误：给泛型类的方法参数用 object"兜底"，破坏了类型安全的初衷；在泛型代码里对 T 用 `==` 与具体值比较——没有约束时 T 只能和 null 比较，需要相等语义应约束为 `IEquatable<T>` 或调用 `EqualityComparer<T>.Default`；把约束写在调用处而不是声明处，编译器不会买账。设计上，类型参数应名副其实（`TKey`/`TValue` 比 `T`/`U` 更可读），约束越少越好，只在确实调用其能力时才加。本课练习要求实现泛型栈并驱动一组命令，覆盖入栈、弹出、窥视与计数四类操作及空栈异常路径。

技术核对（2026-10-21）：[Microsoft Learn：generics](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/generics)。原 source_url 继续标识目录来源，本段链接用于语言事实核实。
