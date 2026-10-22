---
id: csharp-language-features-delegates
title: 委托（Delegate）
concepts: [delegates, methods]
objectives:
  - 声明自定义委托类型，把方法绑定到委托实例并作为参数传递、延迟调用。
  - 用 += 组合多播委托，说明调用按加入顺序同步进行、整体返回值取链上最后一次调用的结果。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-delegate.html
source_snapshot_date: 2026-08-23
---

# 委托（Delegate）

## 概念定义与适用场景

委托是"方法的类型"：它规定了一组参数与一个返回值，任何签名匹配的方法都能装进同类型的委托变量里。有了委托，"调用哪个方法"这件事就从编译期推迟到了运行期——排序的比较规则、过滤的判断条件、事件的响应动作，都可以作为参数传进通用算法，算法本身不必为每个具体规则重写一遍。

```csharp
delegate int Transformer(int x);

static class TransformOps
{
    public static int Square(int x) => x * x;
    public static int Negate(int x) => -x;
}
```

## 语法、API 与边界

声明形式是 `delegate 返回类型 名称(参数列表)`；实例化用方法组转换 `Transformer t = TransformOps.Square;`，调用写作 `t(3)`。`+=` 把方法追加到调用链形成多播委托：调用一次，链上每个方法按加入顺序依次同步执行，整体表达式的返回值来自最后一个方法。遍历调用链可用 `GetInvocationList()`，每个元素单独拿到返回值，实现"输出依次流过每个方法"的管道写法。委托实例是不可变的，`+=` 实际是创建新链再赋回变量；在 null 链上调用会抛 `NullReferenceException`，触发前应判空或用 `?.Invoke`。

```csharp
Transformer chain = TransformOps.Square;
chain += TransformOps.Negate;
var value = 4;
foreach (Transformer step in chain.GetInvocationList())
{
    value = step(value);
}
Console.WriteLine(value);
```

### 多播不是管道，委托也不会自动异步

下面沿用前文的 Transformer 与 TransformOps，直接多播与显式管道的结果不同。两个处理器在直接调用时都收到 4；不会把 16 自动传给 Negate。

```csharp
Transformer operations = TransformOps.Square;
operations += TransformOps.Negate;
Console.WriteLine(operations(4)); // -4：最后一个处理器返回值
var piped = 4;
foreach (Transformer operation in operations.GetInvocationList())
    piped = operation(piped);
Console.WriteLine(piped);        // -16：手工传递中间结果
```

`Action<T>` 表示无返回值的处理，`Func<T, TResult>` 表示返回一个结果的处理；没有额外语义时优先使用这些现成委托。方法组与 lambda 都可以绑定到匹配的委托类型。

```csharp
Func<int, int> twice = number => number * 2;
Action<string> log = Console.WriteLine;
log(twice(3).ToString()); // 6
```

普通委托调用同步执行，调用者会等待方法返回；异步工作需要独立的 Task/async 设计，不是使用委托就自动启用。多播链中某个处理器抛出未捕获异常时，后面的处理器不会继续执行。若业务确实要求分别收集结果或隔离失败，需要显式遍历并制定异常策略，不能假设运行时会自动聚合。

本课练习刻意使用调用链遍历实现管道，只验证顺序转换；它不等于多播调用默认语义，也不涵盖异步回调。

## 常见错误与实践建议

初学者容易混淆两件事：多播委托"每个方法收到相同实参"，与"上一步输出作为下一步输入"的顺序管道——后者必须自己循环调用链逐步累算，直接调用多播委托只会拿到最后一次的返回值。第二类错误是忘记判空：没有订阅者或没有绑定任何方法时调用会崩溃。第三类是把委托当函数指针类比到底——委托是类型安全的对象，支持多播及兼容的协变返回；普通调用仍同步执行。本课练习要求把若干操作按输入顺序组成委托链，再把整数依次流过整条链，训练方法组转换与调用链遍历。

技术核对（2026-10-21）：[Microsoft Learn：delegates](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/delegates/)。原 source_url 继续标识目录来源，本段链接用于语言事实核实。
