using System;
using System.Collections.Generic;
using System.Linq;
int? missing = null;
int? zero = 0;
Console.WriteLine(missing ?? -1); // -1
Console.WriteLine(zero ?? -1);    // 0
Console.WriteLine((missing + 2) is null); // True，可空算术传播 null
Console.WriteLine(missing < zero);       // False，不能据此认定 missing >= zero
string? empty = "";
Console.WriteLine((empty ?? "fallback").Length); // 0

