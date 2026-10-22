---
id: csharp-oop-encapsulation
title: 封装
concepts: [encapsulation, classes]
objectives:
  - 用 private 字段和公开方法把对象状态保护起来。
  - 区分封装与把字段直接声明为 public 的差别。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/csharp/csharp-encapsulation.html
source_snapshot_date: 2026-08-23
---

# 封装

## 概念定义与适用场景

封装指把数据和对数据的操作收进一个类型里，外部只能通过类型公开的方法访问状态。当某个值有取值规则（例如余额不能为负）时，把它设为 private 并提供受控入口，规则才有唯一的执行位置。

```csharp
class Counter
{
    private int _value;

    public void Increase() => _value++;
    public int Read() => _value;
}
```

## 语法、API 与边界

`private` 修饰的成员只能在声明它的类型内部访问；方法名不加修饰符时默认 private。本课只用字段、方法与布尔返回值表达访问控制。

```csharp
class Wallet
{
    private int _cents;

    public bool TrySpend(int cents)
    {
        if (cents < 0 || cents > _cents) return false;
        _cents -= cents;
        return true;
    }
}
```

## 常见错误与实践建议

把字段声明成 public 只是公开了存储位置，没有表达任何约束，调用方可以写出任意非法状态。判断封装是否到位的简单标准是：外部代码是否可能让对象进入无效状态。本课练习从标准输入读取数据、向标准输出写入判定结果，不访问文件或网络。
