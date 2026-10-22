---
id: java-collections-generics-generics
title: 泛型
concepts: [generics, collections]
objectives:
  - 掌握泛型的核心概念与使用方式。
  - 用正常、边界和失败输入验证泛型。
prerequisites: [java-collections-generics-object-class]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-generics.html
source_snapshot_date: 2026-08-23
---

# 泛型

## 概念定义与适用场景

泛型用类型参数表达“算法相同、数据类型可变”，让编译器检查容器和调用是否兼容。`List<String>` 的 get 返回 String，不需要调用者重复强转；泛型提升类型安全，但不能保证所有运行时类型错误消失，原始类型、未检查转换和反射等仍可能破坏约束。

类型参数用于引用类型，所以写 `List<Integer>`，不能写 `List<int>`。尖括号中的 T 是类型位置，不能当成普通数值使用。泛型类在类名后声明参数，泛型方法在返回类型前声明自己的 `<T>`；静态方法不能直接使用所属泛型类的实例类型参数。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `Ada`、`7`。Box 使用类型参数存取数据，max 用上界保证 T 有可调用的 compareTo。这里将比较契约写为 `Comparable<? super T>`，也允许比较能力定义在 T 的父类型上。

```java
class Box<T> {
    private final T value;
    Box(T value) { this.value = value; }
    T get() { return value; }
}
public class Main {
    static <T extends Comparable<? super T>> T max(T a, T b) {
        return a.compareTo(b) >= 0 ? a : b;
    }
    public static void main(String[] args) {
        Box<String> name = new Box<>("Ada");
        System.out.println(name.get());
        System.out.println(max(3, 7));
    }
}
```

泛型通常不协变：`List<Integer>` 不能赋给 `List<Number>`。否则调用者可能把 Double 放入本来只应有 Integer 的列表。需要读取不同数字列表，可用 `List<? extends Number>`；读取值至少是 Number，但不能安全加入任意 Number。需要写入 Integer，可用 `List<? super Integer>`；读回时一般只能保证 Object。

第二个独立程序输出 `3.0`、`[7]`。上界用于读数，下界用于写数；`?` 表示某个未知类型，不表示“任意类型都能安全添加”。

```java
import java.util.ArrayList;
import java.util.List;
public class Main {
    static double sum(List<? extends Number> values) {
        double result = 0;
        for (Number value : values) result += value.doubleValue();
        return result;
    }
    static void addSeven(List<? super Integer> target) { target.add(7); }
    public static void main(String[] args) {
        System.out.println(sum(List.of(1, 2)));
        List<Number> numbers = new ArrayList<>();
        addSeven(numbers);
        System.out.println(numbers);
    }
}
```

通配符扩展视图不等于把原集合冻结；持有原始可变列表的其他引用仍可修改它。`List<?>` 可以读取 Object，但不能安全添加任意非 null 元素。

类型擦除意味着运行时通常不能检查 `instanceof List<String>`，可检查 `instanceof List<?>`。不能直接 `new T()`、`T.class` 或 `new T[10]`；确需运行时类型时可显式传入 Class 等信息。擦除也会让某些看似不同的重载冲突，例如 `f(List<String>)` 与 `f(List<Integer>)` 不能仅靠元素类型区分。

## 常见错误与实践建议

避免原始类型 `List`，也不要用 `@SuppressWarnings` 隐藏尚未理解的类型风险。泛型参数、通配符和上界是不同角色；只有确需关联多个位置的类型时才声明 T，不必把简单方法都泛型化。包装值可能为 null，比较时仍需遵守空值契约。

原有练习仅通过泛型方法求逗号分隔整数的最大值，保留现有输入与输出契约；它没有全面覆盖泛型类、通配符、擦除或未检查转换。本文示例 max 的参数假设为非 null，这不是对原题新增判题要求。

参考：[JLS 17 类型变量与擦除](https://docs.oracle.com/javase/specs/jls/se17/html/jls-4.html#jls-4.4)、[Oracle 通配符](https://docs.oracle.com/javase/tutorial/java/generics/wildcards.html)、[泛型限制](https://docs.oracle.com/javase/tutorial/java/generics/restrictions.html)。
