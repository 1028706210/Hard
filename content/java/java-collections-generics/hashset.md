---
id: java-collections-generics-hashset
title: HashSet
concepts: [collections, generics]
objectives:
  - 掌握HashSet的核心概念与使用方式。
  - 用正常、边界和失败输入验证HashSet。
prerequisites: [java-collections-generics-linkedlist]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-hashset.html
source_snapshot_date: 2026-08-23
---

# HashSet

## 概念定义与适用场景

HashSet 用于唯一性存储和成员查询，不保留可依赖的迭代顺序。元素先按 hashCode 定位候选，再由 equals 确认是否相等。哈希分布合理时，基本添加、查询和移除通常具有常量时间性能；不能把它承诺为任何输入下都绝对 O(1)。

相等对象必须有相等哈希码；哈希码相同不代表相等。String 已实现值相等语义，自定义类若仅使用 Object 默认 equals，则按对象身份区分，两个字段相同的实例也可能成为两个元素。具体契约见 Object 类课。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `true`、`false`、`true`、`1`。add 返回是否真正新增，remove 返回是否实际删除，不是返回元素本身。

```java
import java.util.HashSet;
import java.util.Set;
public class Main {
    public static void main(String[] args) {
        Set<String> values = new HashSet<>();
        System.out.println(values.add("a"));
        System.out.println(values.add("a"));
        values.add("b");
        System.out.println(values.remove("b"));
        System.out.println(values.size());
    }
}
```

第二个独立程序输出 `true`、`false`、`true`。HashSet 允许一个 null；`Set.of` 的 null 规则则不同。为得到稳定排序的展示结果，可以显式复制到 TreeSet，但本例的 null 不适合直接放入使用自然顺序的 TreeSet。

```java
import java.util.HashSet;
import java.util.Set;
public class Main {
    public static void main(String[] args) {
        Set<String> values = new HashSet<>();
        values.add(null);
        values.add("Ada");
        System.out.println(values.contains(null));
        System.out.println(values.contains("ada"));
        System.out.println(values.contains("Ada"));
    }
}
```

插入后不要修改参与 equals/hashCode 的字段，否则元素仍在按旧哈希放置的位置，contains/remove 可能无法正常找到。需要变更标识时，可在变更前移除再重新插入，或优先使用不可变值作为标识。要求插入顺序用 LinkedHashSet，要求排序用 TreeSet，并确认其比较规则。

## 常见错误与实践建议

不要断言 HashSet.toString 的某个固定顺序，也不要仅重写 equals 而保留不一致的 hashCode。大小写是否相同属于业务规则；默认 String.equals 区分大小写，若需规范化应在输入阶段制定一致策略。HashSet 不自动解决并发修改问题。

本课练习继续将逗号分隔字符串去重，输出唯一元素数量。它不检查自定义对象哈希实现、顺序、null 或并发安全，不能把计数正确当成这些子主题已经验证。

参考：[Java 17 HashSet](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashSet.html)、[Object.equals/hashCode](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Object.html)。
