---
id: java-collections-generics-arraylist
title: ArrayList
concepts: [collections, control-flow]
objectives:
  - 掌握ArrayList的核心概念与使用方式。
  - 用正常、边界和失败输入验证ArrayList。
prerequisites: [java-collections-generics-collections-framework]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-arraylist.html
source_snapshot_date: 2026-08-23
---

# ArrayList

## 概念定义与适用场景

ArrayList 是可调整容量的数组列表。它保存元素的顺序，允许重复和 null，适合按索引访问、顺序遍历和尾部追加。`get`、`set` 为常量时间；尾部 add 为均摊常量时间，个别扩容操作需要复制。中间插入、删除通常要移动后续元素，花费随元素数量增长。

size 是实际元素数，capacity 是底层可用空间。`new ArrayList<>(100)` 仅预留空间，size 仍为 0，不能直接 get(0)。预设容量是已知规模时的优化，不是每次创建列表都必须做的步骤。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `0`、`[a, c, b]`、`c`。add(index,value) 可在 0 到 size 之间插入；get/set 的索引则必须在 0 到 size-1 之间。set 替换已有元素，不改变长度。

```java
import java.util.ArrayList;
import java.util.List;
public class Main {
    public static void main(String[] args) {
        List<String> values = new ArrayList<>(10);
        System.out.println(values.size());
        values.add("a");
        values.add("b");
        values.add(1, "c");
        System.out.println(values);
        System.out.println(values.set(1, "d"));
    }
}
```

Integer 列表的两个 remove 重载易混淆：`remove(int)` 按索引删并返回旧元素；`remove(Object)` 按相等值删第一个匹配项并返回是否删除。第二个独立程序输出 `1`、`true`、`[3, 2]`。

```java
import java.util.ArrayList;
import java.util.List;
public class Main {
    public static void main(String[] args) {
        List<Integer> values = new ArrayList<>(List.of(3, 1, 2, 1));
        System.out.println(values.remove(1));
        System.out.println(values.remove(Integer.valueOf(1)));
        System.out.println(values);
    }
}
```

`contains` 和按值删除通常需要线性查找。频繁在中间插入并不自动意味着 LinkedList 更合适：若每次仍按索引寻找节点，查找本身可能是线性成本，还要考虑内存和访问模式。两端队列优先考虑 Deque 接口；性能选择应围绕真实操作，而非只看某一次插入的理论成本。

## 常见错误与实践建议

遍历时通过 list.remove 结构性修改列表，可能使迭代器失效；需要删除时可用支持删除的 Iterator 或 removeIf，详细边界见 Iterator 课。ArrayList 不自动同步，不能把“偶尔没报错”当成并发安全。不可修改的 List.of 不是 ArrayList，必要时先创建可变副本。

本课练习仍读取逗号分隔整数，用 ArrayList 保存后输出元素数量；重复元素计数，不能改用 Set。现有题目不检查所有索引操作、容量或删除重载，本文补充内容没有增加原题输出要求。

参考：[Java 17 ArrayList](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/ArrayList.html)、[List.remove 重载](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/List.html#remove(int))。
