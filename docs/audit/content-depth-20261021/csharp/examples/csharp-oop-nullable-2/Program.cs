using System;
using System.Collections.Generic;
using System.Linq;
#nullable enable
string? name = null;
Console.WriteLine(name?.Length ?? -1); // -1，不会解引用 null
name ??= "Li";
Console.WriteLine(name.Length);        // 2

