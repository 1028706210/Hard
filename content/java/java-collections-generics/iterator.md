---
id: java-collections-generics-iterator
title: Iterator
concepts: [collections, control-flow]
objectives:
  - 掌握Iterator的核心概念与使用方式。
  - 用正常、边界和失败输入验证Iterator。
prerequisites: [java-collections-generics-hashmap]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-iterator.html
source_snapshot_date: 2026-08-23
---

# Iterator

## 概念定义与适用场景

Iterator 表示遍历过程中的当前位置，让调用者不依赖容器内部存储方式。hasNext 检查是否还有元素，next 返回下一个元素并前进；hasNext 不消耗元素。没有元素仍调用 next 会抛 NoSuchElementException，不能把 next 当成能返回 null 的空队列操作。

增强 for 遍历实现 Iterable 的集合时使用迭代机制，数组的增强 for 则不需要 Iterator。迭代器通常一次向前消费，需要重新遍历时获取新的迭代器，不应假设能自动回到开头。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `6`、`false`。每轮仅调用一次 next，将取出的值用于求和；若在打印或判断中额外调用 next，可能意外跳过元素。

```java
import java.util.Iterator;
import java.util.List;
public class Main {
    public static void main(String[] args) {
        Iterator<Integer> iterator = List.of(1, 2, 3).iterator();
        int total = 0;
        while (iterator.hasNext()) {
            int value = iterator.next();
            total += value;
        }
        System.out.println(total);
        System.out.println(iterator.hasNext());
    }
}
```

支持 remove 的迭代器可删除最近一次 next 返回的元素；每次 next 后最多 remove 一次。尚未 next 就 remove，或连续 remove 两次会产生 IllegalStateException。remove 属于可选操作，不可修改列表的迭代器不支持删除。

第二个独立程序输出 `[1, 3]`。删除发生在当前迭代器上，游标语义与底层列表保持一致。也可用 removeIf 表达简单谓词删除，但不必为了此题重写现有练习。

```java
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
public class Main {
    public static void main(String[] args) {
        List<Integer> values = new ArrayList<>(List.of(1, 2, 3, 4));
        Iterator<Integer> iterator = values.iterator();
        while (iterator.hasNext()) {
            if (iterator.next() % 2 == 0) iterator.remove();
        }
        System.out.println(values);
    }
}
```

许多普通可变集合的迭代器采用 fail-fast 检查：遍历期间经集合自身方法结构性修改，可能抛 ConcurrentModificationException，即使仅有一个线程也可能出现。它是尽力发现错误的机制，不能依赖必定抛异常来保障业务正确，更不是线程同步方案。并发集合可能具有不同遍历契约，不能把同一规则无条件套到所有实现。

## 常见错误与实践建议

不要在增强 for 中直接 list.remove 后假设剩余遍历仍安全；使用当前迭代器删除、removeIf 或先收集后修改。是否可以替换元素、是否结构性修改，要依据实现契约，不能笼统说“遍历时完全不能修改任何值”。

本课原题只用 Iterator 遍历逗号分隔整数并求和，不要求删除。本文新增游标状态、可选 remove 和 fail-fast 机制的解释；练习输出正确不等于这些状态与错误分支都经过测试。

参考：[Java 17 Iterator](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Iterator.html)、[ArrayList 迭代器契约](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/ArrayList.html)。
