---
id: csharp-language-features-events
title: 事件（Event）
concepts: [events, delegates]
objectives:
  - 在发布者类中声明事件，在满足条件的方法里触发，并由外部订阅者用 lambda 订阅收集通知。
  - 说明事件与公共委托字段的封装差异：外部只能 += / -=，触发权保留在发布者类内部。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-event.html
source_snapshot_date: 2026-08-23
---

# 事件（Event）

## 概念定义与适用场景

事件是"订阅-通知"关系的语言级支持：温度越过阈值、进度走完一步、用户点了按钮，发布者只管喊一声"事情发生了"，谁在听、听到后做什么，它一概不关心。这个反转把发布者与订阅者解耦——监控类不需要知道统计逻辑，按钮类不需要知道业务代码，双方只通过事件签名连接。

```csharp
sealed class AlertArgs : EventArgs
{
    public int Value { get; init; }
}

sealed class TemperatureMonitor
{
    private readonly int _threshold;

    public TemperatureMonitor(int threshold) => _threshold = threshold;

    public event EventHandler<AlertArgs>? Alert;

    public void Observe(int value)
    {
        if (value >= _threshold)
        {
            Alert?.Invoke(this, new AlertArgs { Value = value });
        }
    }
}
```

## 语法、API 与边界

事件声明的惯用形式是 `public event EventHandler<TArgs>? 名称;`，`EventHandler<TArgs>` 是现成的委托类型，约定第一个参数是发布者、第二个是携带数据的 `EventArgs` 子类。事件对外只开放 `+=` 与 `-=`：订阅者不能调用、覆盖或清空事件，`Alert = null` 在类外直接编译失败——这是 event 关键字相对公共委托字段的核心封装价值，触发权只属于发布者类内部。触发前用 `Alert?.Invoke(...)` 判空，没有订阅者时安全跳过。自定义参数类继承 `EventArgs`，用 init 或只读属性承载数据，本例每次创建参数对象且 int 属性只能初始化，因此发布后不再修改该数值；这并不自动保证所有 EventArgs 都是不可变快照。

```csharp
var monitor = new TemperatureMonitor(30);
var alerts = new List<int>();
monitor.Alert += (_, args) => alerts.Add(args.Value);
monitor.Observe(25);
monitor.Observe(41);
Console.WriteLine(alerts.Count);
```

### 订阅的生命周期与同步异常

发布者保存处理器委托，处理器可能间接保持订阅者对象存活。长生命周期的发布者遇到短生命周期的订阅者时，要在订阅者结束使用时退订。需要退订的 lambda 应先保存成同一个委托实例，不能期待重新写一遍 lambda 就能删除原来的订阅。

```csharp
var monitor = new TemperatureMonitor(30);
EventHandler<AlertArgs> handler = (_, args) => Console.WriteLine(args.Value);
monitor.Alert += handler;
monitor.Observe(31); // 31
monitor.Alert -= handler;
monitor.Observe(40); // 无输出，已经退订
```

普通事件处理器在发布者调用线程上同步运行。一个处理器未捕获的异常会回到发布者调用处，并中断后续处理器；事件不是自动的后台消息队列。`?.Invoke` 避免空委托调用，但不会让订阅者对象状态、处理器执行或整个发布流程自动具备线程安全性。取到委托快照后发生退订，也不能取消已经开始的这次调用。

只读或 init 数据可防止本例的告警数值被订阅者修改，但若 EventArgs 中含可变对象，仍可能共享其内部状态；“继承 EventArgs”本身不会产生不可变快照。基类事件需要供派生类发布时，通常由基类提供 protected 的触发方法，派生类不能直接调用基类声明的事件。

当前练习只检验阈值通知与统计；退订、生命周期管理和处理器异常策略属于额外边界，尚未由现有题目验证。

## 常见错误与实践建议

初学者常见的错误：在订阅者代码里试图给事件赋值或直接调用，被编译器拦下才意识到封装边界；发布者写成 `if (Alert != null) Alert(...)`，在判空与第二次读取事件之间可能发生全部退订。`Alert?.Invoke(...)` 或先保存局部委托快照再判空调用可以避免空委托竞态，但不会自动同步处理器内部状态。用公共委托字段替代事件，外部一句 `monitor.Alert = null` 就能清空所有订阅。参数传递上，不要让订阅者任意修改后续处理器还要读取的同一个参数对象。本课练习要求实现阈值监控，事件在越界读数上触发，订阅者统计首末与最大告警值。

技术核对（2026-10-21）：[Microsoft Learn：events](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/events/)。原 source_url 继续标识目录来源，本段链接用于语言事实核实。
