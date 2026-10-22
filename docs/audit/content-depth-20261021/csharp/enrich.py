"""Narrow, idempotence-guarded authoring pass; never rewrites exercise files."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "content/csharp"
OUT = Path(__file__).parent
if OUT.joinpath('baseline-sha256.json').exists():
    raise SystemExit('This one-time pass already has a baseline; refusing to overwrite evidence.')
before = {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in BASE.rglob('*') if p.is_file()}
OUT.joinpath('baseline-sha256.json').write_text(json.dumps(before, indent=2), encoding='utf-8')

additions = {
"csharp-oop/classes": r'''### 对象身份、共享引用与按值传参

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
''',
"csharp-oop/structs": r'''### 复制的是字段值，不是递归复制整张对象图

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
''',
"csharp-oop/inheritance": r'''### 继承的初始化与访问边界

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
''',
"csharp-oop/polymorphism": r'''### override、new 与 abstract 的可观察区别

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
''',
"csharp-oop/interfaces": r'''### 接口与抽象类如何选择

接口适合跨类型声明能力，抽象类适合在同一继承体系中共享状态、构造流程及部分实现。一个类可以实现多个接口，但只能继承一个类；struct 也能实现接口，却不能继承抽象类。先只需要调用能力时，定义一个小接口通常已足够，不必额外建立抽象基类。

传统接口中没有方法体的成员隐含 public，普通隐式实现必须是 public。另有“显式接口实现”：成员带接口限定名，不写 public，并且只能通过接口视图调用，适合同名能力需要不同实现的情况。

```csharp
var report = new Report();
IPrintable view = report;
Console.WriteLine(view.Print()); // report
// report.Print();               // 编译失败：只能通过接口访问

interface IPrintable
{
    string Print();
}

sealed class Report : IPrintable
{
    string IPrintable.Print() => "report";
}
```

现代 C# 的接口也能提供默认实现及部分静态成员，因此“接口永远没有实现”不准确；带实现的成员可以有其他访问级别。这些能力不改变接口不能包含实例字段、实例构造函数的边界。本章以传统实例合同为主，暂不展开默认接口成员的冲突规则或静态抽象接口成员。

调用接口成员仍会在运行期找到实际实现；接口变量只公开合同允许的成员。现有练习检查三种文本变换通过同一接口调用，显式实现与抽象类选型属于额外教学，不应当冒称已经被该练习覆盖。
''',
"csharp-oop/nullable": r'''### 缺失、零与空字符串是不同状态

`int?` 默认值是 null；`int` 默认值是 0。`GetValueOrDefault()` 返回底层类型默认值，所以会把缺失与真实的 0 合并；如果业务需要区分二者，必须先用 `HasValue` 或模式匹配保留这个区别。`??` 只对 null 回退，不会替换空字符串。

```csharp
int? missing = null;
int? zero = 0;
Console.WriteLine(missing ?? -1); // -1
Console.WriteLine(zero ?? -1);    // 0
Console.WriteLine((missing + 2) is null); // True，可空算术传播 null
Console.WriteLine(missing < zero);       // False，不能据此认定 missing >= zero
string? empty = "";
Console.WriteLine((empty ?? "fallback").Length); // 0
```

对可空数值做 `<`、`>` 等关系比较时，只要有一边缺失，结果为 false；相等比较规则不同，两个 null 相等。不要把缺失数据排序、计算的业务规则偷偷交给这些默认行为。

```csharp
#nullable enable
string? name = null;
Console.WriteLine(name?.Length ?? -1); // -1，不会解引用 null
name ??= "Li";
Console.WriteLine(name.Length);        // 2
```

可空引用分析需要在项目或文件中启用；它给出编译诊断，不能阻止外部代码在运行期传入 null。`name!` 只是抑制警告，不会插入校验或创建对象。对不可信边界仍要检查 null。这里的 `?.` 表达式只在接收者非 null 时访问成员，后面的 `??` 再给出缺失时的结果。

本课练习区分空输入、解析失败及合法值；它没有验证全部提升运算规则或可空编译诊断，代码示例不能替代这些额外检查。
''',
"csharp-language-features/properties": r'''### get、private set 与 init 的边界

只有 get 的自动属性可以在声明它的类型的构造函数中初始化；private set 允许该类型在后续方法中继续赋值；init 允许在构造阶段、对象初始化器等初始化上下文中赋值，此后普通赋值会编译失败。只读属性返回可变列表时，列表仍可能被修改，不能把“无法重新赋值属性”当作深度不可变。

```csharp
var badge = new Badge { Name = "Lin" };
Console.WriteLine(badge.Caption); // Hello, Lin
// badge.Name = "Chen";            // 编译失败：初始化后不可再写 init 属性

sealed class Badge
{
    public string Name { get; init; } = "guest";
    public string Caption => "Hello, " + Name;
}
```

计算属性不必存储后备字段；`Caption` 每次读取都会计算。完整 set 中的隐式参数 `value` 是本次写入值。若写成 `set => Age = value;`，访问器会递归调用自己直到栈耗尽，正确目标应是后备字段。规则可以选择拒绝负数或钳制到边界，但必须与公开合同一致，不能悄悄混用。

属性可以同时有 get/set、只有 get，或仅有 set；表达式体 get 也不等于自动属性。示例 Account 的构造赋值只演示语法，实际余额模型还需拒绝非法初始值并考虑金额溢出。本课账户练习的输入边界与预期输出由题目约定，此处没有更改它们。字段改为属性通常保留源代码调用形式，但不是二进制兼容保证：对外发布的库仍需重新评估使用方。
''',
"csharp-language-features/indexer": r'''### 带参数访问与二维读写

索引器参数不限定为整数，`this[string key]` 可以按名称查数据，多个参数可以表达网格坐标。下例是独立的二维读写示例；其存储与边界来自内部二维数组，写入值通过 set 的 `value` 接收。

```csharp
var grid = new Grid();
grid[1, 0] = 7;
Console.WriteLine(grid[1, 0]); // 7
Console.WriteLine(grid[0, 0]); // 0，数组默认值

sealed class Grid
{
    private readonly int[,] _cells = new int[2, 2];
    public int this[int row, int column]
    {
        get => _cells[row, column];
        set => _cells[row, column] = value;
    }
}
```

这里有效行列都是 0 或 1，`grid[2, 0]` 抛出 IndexOutOfRangeException。普通自定义集合也可以显式抛 ArgumentOutOfRangeException，关键是事先说明合同。返回空串表示缺键时可能与“实际存储空串”混淆，需要无歧义地表达缺失时，可另提供 TryGet 方法。

索引器没有自动实现形式，必须提供访问器实现；它本身也不保证线程安全或快速查找。PhoneBook 复制输入数组可隔离外部数组槽位的修改；若元素是可变对象，浅复制仍然共享对象。当前练习只要求一维只读电话簿与约定的越界处理；二维读写、字符串键和可变元素所有权未被该题验证。
''',
"csharp-language-features/delegates": r'''### 多播不是管道，委托也不会自动异步

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
''',
"csharp-language-features/events": r'''### 订阅的生命周期与同步异常

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
''',
"csharp-language-features/generics": r'''### 类型参数的能力由约束决定

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
''',
"csharp-language-features/collections": r'''### 按操作选择集合，而不只记住容器名字

| 需要的操作 | 优先考虑 | 易错边界 |
| --- | --- | --- |
| 按位置访问、追加 | List<T> | Count 是元素数，Capacity 是已分配容量；中间插删会搬移元素 |
| 唯一键到值的映射 | Dictionary<TKey,TValue> | Add 遇重复键抛异常，下标写入会新增或覆盖 |
| 去重或成员判断 | HashSet<T> | 不表达排序或重复次数，比较规则影响“相同” |
| 先进先出 | Queue<T> | Dequeue 取走最早入队元素，空队列需检查或 TryDequeue |
| 后进先出 | Stack<T> | Pop 取走栈顶，Peek 只观察，空栈需检查或 TryPop |

旧式 ArrayList、Hashtable 在旧项目中会出现，依赖 object 存储，使用时需要处理强转及值类型装箱。新代码一般优先选择泛型集合；需要按键排序再枚举可考虑 SortedDictionary，不能靠 Dictionary 的实现细节得到排序。

```csharp
var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
Console.WriteLine(seen.Add("Hard")); // True
Console.WriteLine(seen.Add("hard")); // False，同一比较规则下重复
var queue = new Queue<int>();
queue.Enqueue(2);
queue.Enqueue(5);
Console.WriteLine(queue.Dequeue()); // 2
var stack = new Stack<int>();
stack.Push(2);
stack.Push(5);
Console.WriteLine(stack.Pop());     // 5
```

键或集合元素若参与哈希判断，其相等与哈希码应保持一致；对象放入哈希集合后再修改影响哈希的状态，会导致查找失效。只需遍历的参数可使用 IEnumerable<T> 暴露意图，但它不保证集合不可变、不保证重复枚举没有成本。List 的 foreach 枚举期间修改元素集合通常使枚举器失效；删除匹配项可用 RemoveAll，而不是一边 foreach 一边 Remove。

本课词频题只覆盖 Dictionary 计数与 List 保序，HashSet/Queue/Stack 的选型和枚举失效规则未由该题全面测试。容器选型需要的操作越少，越应复用标准库已有能力。
''',
"csharp-language-features/anonymous-methods": r'''### 闭包捕获变量，不是冻结当时的数值

```csharp
int factor = 2;
Func<int, int> scale = value => value * factor;
factor = 3;
Console.WriteLine(scale(4)); // 12

var actions = new List<Action>();
for (int index = 0; index < 2; index++)
{
    int captured = index; // 每轮独立变量
    actions.Add(() => Console.WriteLine(captured));
}
foreach (var action in actions) action(); // 依次 0、1
```

若 for 循环直接捕获 index，两次延后调用都会读到结束后的 2。现代 foreach 的迭代变量每轮独立，不能把这条 for 的规则原样套用到 foreach。需要无捕获函数时可使用 static lambda，编译器会阻止它捕获外部局部变量。

表达式 lambda 可在合适上下文中转换为表达式树，表达式树描述代码而不是直接作为委托调用；语句体 lambda 则不能转换为表达式树。本章先掌握委托形式即可，不要求引入表达式树基础设施。本课过滤平方练习只验证立即过滤和转换，闭包生命周期与查询表达式树没有纳入题目合同。
'''
}

sources = {
"csharp-oop/classes": ["fundamentals/types/", "language-reference/keywords/method-parameters"],
"csharp-oop/structs": ["language-reference/builtin-types/struct"],
"csharp-oop/inheritance": ["fundamentals/object-oriented/inheritance"],
"csharp-oop/polymorphism": ["fundamentals/object-oriented/polymorphism", "language-reference/keywords/abstract"],
"csharp-oop/interfaces": ["fundamentals/types/interfaces"],
"csharp-oop/nullable": ["language-reference/builtin-types/nullable-value-types", "nullable-references"],
"csharp-language-features/properties": ["programming-guide/classes-and-structs/properties"],
"csharp-language-features/indexer": ["programming-guide/indexers/"],
"csharp-language-features/delegates": ["programming-guide/delegates/"],
"csharp-language-features/events": ["programming-guide/events/"],
"csharp-language-features/generics": ["fundamentals/types/generics"],
"csharp-language-features/collections": ["https://learn.microsoft.com/en-us/dotnet/standard/collections/selecting-a-collection-class"],
"csharp-language-features/anonymous-methods": ["language-reference/operators/lambda-expressions"],
"csharp-io-metadata/preprocessor-directives": ["language-reference/preprocessor-directives"],
"csharp-io-metadata/reflection": ["https://learn.microsoft.com/en-us/dotnet/fundamentals/reflection/reflection"],
}

fixes = {
"csharp-oop/classes": [('`readonly` 字段只能在构造时赋值', '`readonly` 实例字段只能在字段初始化器或声明它的类的实例构造函数中赋值')],
"csharp-oop/structs": [('复制成本低的同 时避免了共享可变状态', '复制成本通常较低；但若含引用字段，仍须考虑共享对象')],
"csharp-oop/interfaces": [('接口成员隐式为 public，实现类必须用 public 实现这些成员。', '本例无方法体的接口成员隐含 public；普通隐式实现必须是 public，也可以使用后文的显式接口实现。')],
"csharp-oop/polymorphism": [('用派生类型声明变量再调用方法体现不了多态；要让循环代码保持稳定，应把变量声明为基类型。', '基类引用最便于展示统一调用；派生类型变量调用虚方法时同样遵循虚分派规则。')],
"csharp-language-features/anonymous-methods": [('lambda 不能赋给普通委托变量以外的表达式树类型（`Expression<Func<...>>`）再按方法调用。', '表达式 lambda 可以转换为表达式树（`Expression<Func<...>>`），但表达式树不能直接像委托一样调用，需要先 Compile 为委托；语句体 lambda 不支持该转换。'), ('`FindAll`（原地谓词过滤，返回 List）', '`FindAll`（立即生成新的 List，原列表不变）'), ('现代 for/foreach 语义下尤其要当心', 'for 与现代 foreach 对迭代变量的规则不同，见后文对照')],
"csharp-language-features/generics": [('存入要装箱、取出要强转', '值类型存入要装箱、取出通常要强转'), ('泛型类型参数只存在于编译与元数据层面，同一个 `List<int>` 与 `List<string>` 在运行期是不同的封闭类型。', '泛型类型信息也保留在运行期，`List<int>` 与 `List<string>` 是不同的封闭类型，可用反射区分。')],
"csharp-language-features/delegates": [('支持多播、异步与协变返回', '支持多播及兼容的协变返回；普通调用仍同步执行')],
"csharp-language-features/events": [('订阅者拿到的是快照而非共享可变状态', '本例每次创建参数对象且 int 属性只能初始化，因此发布后不再修改该数值；这并不自动保证所有 EventArgs 都是不可变快照')],
"csharp-io-metadata/preprocessor-directives": [('`#define` 必须出现在文件最前面（只允许前面有 using 与注释）', '`#define` 必须出现在该文件的任何普通 C# 代码之前，包括 using 指令之前；前面可以有空白、注释或其他预处理器指令')],
"csharp-io-metadata/reflection": [('也是读取自定义特性的唯一途径', '也能用于在运行期读取自定义特性；编译器和源码生成器还可在构建时分析特性'), ('`typeof(T)` 在编译期确定类型', '`typeof(具体类型名)` 根据源码中的类型名取得 Type 对象，`typeof(T)` 则取得当前泛型类型实参的 Type 对象')],
}

for key in sorted(set(additions) | set(fixes)):
    path = BASE / (key + '.md')
    original = path.read_text(encoding='utf-8')
    text = original
    for old, new in fixes.get(key, []):
        assert old in text, (key, old)
        text = text.replace(old, new)
    if key in additions:
        heading = '## 常见错误与实践建议'
        assert additions[key].splitlines()[0] not in text, key
        text = text.replace(heading, additions[key].strip() + '\n\n' + heading)
    urls = [s if s.startswith('https:') else 'https://learn.microsoft.com/en-us/dotnet/csharp/' + s for s in sources[key]]
    text = text.rstrip() + '\n\n技术核对（2026-10-21）：' + '；'.join(f'[Microsoft Learn：{u.rstrip("/").split("/")[-1]}]({u})' for u in urls) + '。原 source_url 继续标识目录来源，本段链接用于语言事实核实。\n'
    path.write_text(text, encoding='utf-8', newline='\n')

changed = [str(p.relative_to(ROOT)).replace('\\','/') for p in BASE.rglob('*') if p.is_file()
           and before.get(str(p.relative_to(ROOT)).replace('\\','/')) != hashlib.sha256(p.read_bytes()).hexdigest()]
OUT.joinpath('changed-files.json').write_text(json.dumps(changed, indent=2), encoding='utf-8')
assert all(p.endswith('.md') for p in changed)
print(f'Updated {len(changed)} lesson bodies; exercises and front matter retained.')
