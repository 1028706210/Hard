using System;
using System.Collections.Generic;
using System.Linq;
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

