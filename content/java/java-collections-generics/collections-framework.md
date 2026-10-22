---
id: java-collections-generics-collections-framework
title: 集合框架
concepts: [collections, generics]
objectives:
  - 掌握集合框架的核心概念与使用方式。
  - 用正常、边界和失败输入验证集合框架。
prerequisites: [java-collections-generics-data-structures]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-collections.html
source_snapshot_date: 2026-08-23
---

# 集合框架

## 概念定义与适用场景

集合框架以接口表达存取契约，以实现类提供不同代价和顺序保证。`Collection<E>` 是 List、Set、Queue 等接口的共同上层；`Map<K,V>` 表示键值映射，不是 Collection 的子接口。工具类 `Collections` 与接口 Collection 也不是同一个类型。

| 需求 | 常用接口与实现 | 顺序和重复规则 |
| --- | --- | --- |
| 按位置存储、允许重复 | List / ArrayList | 保留列表顺序，可用索引 |
| 只保留唯一值 | Set / HashSet | 去重，不保证迭代顺序 |
| 唯一值且排序 | Set / TreeSet | 按自然顺序或 Comparator 排序 |
| 按键查找值 | Map / HashMap | 键唯一，值可重复，不保证顺序 |
| 先进先出或后进先出 | Deque / ArrayDeque | 用两端操作表达队列或栈 |

优先按接口声明变量，例如 `List<String> names = new ArrayList<>()`。接口类型决定调用者依赖哪些能力，具体实现决定复杂度、null 支持及并发行为。不能因两者都叫“集合”就假设操作、顺序和修改能力相同。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `[a, b, c]`、`[a, b, c]`。复制 List.of 的内容到 ArrayList 后可排序；TreeSet 同时去重并按自然顺序排列。

```java
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;
public class Main {
    public static void main(String[] args) {
        List<String> names = new ArrayList<>(List.of("c", "a", "b"));
        Collections.sort(names);
        Set<String> unique = new TreeSet<>(List.of("c", "a", "a", "b"));
        System.out.println(names);
        System.out.println(unique);
    }
}
```

`List.of` 返回不可修改列表，不能 add、remove 或 set，且拒绝 null。不可修改只约束容器操作，不代表元素对象也被冻结。某些列表是固定大小但可替换元素，某些是原集合的视图；使用前要读其具体契约。

第二个独立程序输出 `[a]`、`[a, b]`。`List.copyOf` 在此保存快照，而 `Collections.unmodifiableList` 包装的视图仍能看到原列表后续变化。

```java
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
public class Main {
    public static void main(String[] args) {
        List<String> source = new ArrayList<>(List.of("a"));
        List<String> snapshot = List.copyOf(source);
        List<String> view = Collections.unmodifiableList(source);
        source.add("b");
        System.out.println(snapshot);
        System.out.println(view);
    }
}
```

TreeSet 的排序比较结果为 0 时视作同一个元素；若比较规则与 equals 不一致，可能出现调用者意外的去重结果。HashSet/HashMap 依赖 equals 和 hashCode。容器类型应先满足顺序与等价关系，再考虑性能。

## 常见错误与实践建议

不要因为集合框架存在就全部改成复杂结构；小规模顺序数据通常从 ArrayList 起步。不要将 HashSet 的偶然输出顺序当成契约，也不要笼统称 Vector“总是性能差”。ArrayList、HashMap 等常用可变实现并非自动线程安全，跨线程共享修改需另行协调。

本课练习继续使用 TreeSet 处理逗号分隔字符串，按排序后的唯一值用空格连接输出。它不要求实现框架全部接口，也不能由该题通过推断已掌握视图、快照或线程安全。

参考：[Java 17 集合框架入口](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/package-summary.html)、[List 契约](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/List.html)。
