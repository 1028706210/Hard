using System;
using System.Collections.Generic;
using System.Linq;
Func<int, int> twice = number => number * 2;
Action<string> log = Console.WriteLine;
log(twice(3).ToString()); // 6

