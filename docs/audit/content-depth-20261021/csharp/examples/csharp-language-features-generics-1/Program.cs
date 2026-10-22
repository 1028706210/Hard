using System;
using System.Collections.Generic;
using System.Linq;
Console.WriteLine(PickLarger(4, 9));            // 9
Console.WriteLine(Same(3, 3));                  // True
Console.WriteLine(typeof(List<int>) == typeof(List<string>)); // False

static T PickLarger<T>(T left, T right) where T : IComparable<T> =>
    left.CompareTo(right) >= 0 ? left : right;

static bool Same<T>(T left, T right) =>
    EqualityComparer<T>.Default.Equals(left, right);

