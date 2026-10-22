using System;
using System.Collections.Generic;
using System.Linq;
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

