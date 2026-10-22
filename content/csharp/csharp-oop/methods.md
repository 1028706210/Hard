---
id: csharp-oop-methods
title: 方法
concepts: [methods, functions]
objectives:
  - 把重复逻辑提取成带参数和返回值的方法并在边界输入下验证。
  - 解释重载按方法名与参数列表解析，而与返回值类型无关。
prerequisites: [csharp-oop-encapsulation]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-methods.html
source_snapshot_date: 2026-08-23
---

# 方法

## 概念定义与适用场景

方法是一段有名字、可带参数、可返回值的逻辑单元。同一段计算被两个以上位置使用时，提取成方法可以让规则只写一次，边界条件也只需要验证一次。

```csharp
static int MaxOfThree(int a, int b, int c)
{
    var largest = a;
    if (b > largest) largest = b;
    if (c > largest) largest = c;
    return largest;
}
```

## 语法、API 与边界

同一个类里可以定义多个同名方法，只要参数列表（参数个数或类型）不同，这叫重载。编译器在调用点按实参类型选择最匹配的版本，返回值类型不参与这个判断。

```csharp
static string Label(int value) => "int:" + value;
static string Label(string value) => "text:" + value;
```

## 常见错误与实践建议

只把返回值类型改成不同写法的两个同名方法不是合法重载，编译会直接失败。方法内部应先处理参数的边界值（例如 0、负数、上限），再写主干逻辑；本课练习统一从标准输入读入、从标准输出写出，解析失败按约定返回非零退出码。
