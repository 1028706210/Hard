---
id: java-collections-generics-linkedlist
title: LinkedList
concepts: [collections, data-structures]
objectives:
  - 掌握LinkedList的核心概念与使用方式。
  - 用正常、边界和失败输入验证LinkedList。
prerequisites: [java-collections-generics-arraylist]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-linkedlist.html
source_snapshot_date: 2026-08-23
---

# LinkedList

## 概念定义与适用场景

LinkedList 以双向链表组织元素，同时实现 List 和 Deque。头尾插入、移除不需要移动其余元素；按索引 get、set 或插入时，仍要从较近一端遍历定位，不能理解为任意位置操作都为 O(1)。重复使用 get(i) 遍历链表可能把一次线性任务变成平方级任务。

需要列表索引时常先考虑 ArrayList；需要栈或队列时可按 Deque 编程，并比较 ArrayDeque 的数组实现。LinkedList 支持 null，但 null 会与“空队列返回 null”的约定混淆，因此作为队列时通常避免存 null。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `[3, 2, 1]`、`3`、`1`。逐个 addFirst 会将输入顺序反转，peekFirst/peekLast 查看两端而不移除。

```java
import java.util.LinkedList;
public class Main {
    public static void main(String[] args) {
        LinkedList<Integer> values = new LinkedList<>();
        for (int value : new int[]{1, 2, 3}) values.addFirst(value);
        System.out.println(values);
        System.out.println(values.peekFirst());
        System.out.println(values.peekLast());
    }
}
```

Deque 提供两组空容器行为：poll/peek 返回 null，remove/get 系列抛 NoSuchElementException；offer/add 都用于添加，但对容量受限实现可能用不同失败方式。LinkedList 本身不是固定容量容器。

第二个独立程序输出 `a`、`b`、`null`，展示尾进头出的队列。要表达栈可用 push/pop，但不能在空栈上无检查调用 pop。

```java
import java.util.Deque;
import java.util.LinkedList;
public class Main {
    public static void main(String[] args) {
        Deque<String> queue = new LinkedList<>();
        queue.offerLast("a");
        queue.offerLast("b");
        System.out.println(queue.pollFirst());
        System.out.println(queue.pollFirst());
        System.out.println(queue.pollFirst());
    }
}
```

## 常见错误与实践建议

选择结构前写清楚操作是按索引访问、顺序扫描，还是已持有迭代位置的插入。链表的额外节点和引用也有内存成本，并非删改多就必然更快。遍历应使用 for-each 或迭代器，结构性修改需遵守相应规则；它同样不是自动线程安全的容器。

本课练习仍用 addFirst 反转逗号分隔整数，按空格连接输出反转结果。队列的空值分支与容器选择分析是扩展讲解，未改变练习的输入处理和判题契约。

参考：[Java 17 LinkedList](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/LinkedList.html)、[Deque 契约](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Deque.html)。
