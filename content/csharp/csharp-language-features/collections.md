---
id: csharp-language-features-collections
title: 集合（Collection）
concepts: [collections, generics]
objectives:
  - 按访问模式选择 List<T>（保序、可变长）与 Dictionary<TKey,TValue>（按键映射）并完成统计类任务。
  - 说明 Dictionary 枚举顺序没有契约保证，需要输出顺序时应自己记录首次出现顺序。
prerequisites: []
difficulty: intermediate
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-collection.html
source_snapshot_date: 2026-08-23
---

# 集合（Collection）

## 概念定义与适用场景

集合是组织多个值的基础设施。`List<T>` 按顺序存放、可以随时增长，适合"逐个处理一串元素"；`Dictionary<TKey,TValue>` 把键映射到值，适合"按名字查记录、按单词数次数"。选型的判断依据是访问模式：按下标顺序遍历用 List，按键快速定位用 Dictionary，两者常常搭配出现——List 记顺序，Dictionary 记计数。

```csharp
var order = new List<string>();
var counts = new Dictionary<string, int>();

void Count(string word)
{
    if (!counts.TryGetValue(word, out var count))
    {
        counts[word] = 0;
        order.Add(word);
    }
    counts[word] += 1;
}
```

## 语法、API 与边界

`List<T>` 的常用操作：`Add` 追加、`Count` 取长度、下标读写、`FindAll(Predicate<T>)` 过滤、`ConvertAll<T>(Converter<T,T>)` 映射。`Dictionary<TKey,TValue>` 的要点：取值前用 `TryGetValue` 判断键是否存在，避免直接下标访问在缺键时抛 `KeyNotFoundException`；键类型必须正确实现相等比较，string 键按内容比较。特别注意：Dictionary 的枚举顺序没有"按插入顺序"的契约保证，同一个程序在不同运行时版本下顺序可能不同——要按首次出现顺序输出，就必须自己维护一个顺序表。容量方面 List 会自动扩容，无需预估也能正确，只是大批量插入时可传入初始容量减少重分配。

```csharp
foreach (var word in order)
{
    Console.WriteLine($"word={word} count={counts[word]}");
}
```

### 按操作选择集合，而不只记住容器名字

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

## 常见错误与实践建议

初学者常见的错误：直接用 `dict[key]` 读一个可能不存在的键，运行期才崩，应优先 `TryGetValue`；依赖 Dictionary 的枚举顺序当输出顺序，换了环境结果就变；用 `Remove` 遍历 List 的同时删元素，跳过了相邻元素，应改为倒序遍历或先收集再删除。性能上，Dictionary 按键查找接近常数时间，而"在 List 里循环找值"是线性扫描，键值语义明确时不要用 List 模拟映射。本课练习要求统计词频并按首次出现顺序输出，正是"Dictionary 记数、List 记序"的组合训练。

技术核对（2026-10-21）：[Microsoft Learn：selecting-a-collection-class](https://learn.microsoft.com/en-us/dotnet/standard/collections/selecting-a-collection-class)。原 source_url 继续标识目录来源，本段链接用于语言事实核实。
