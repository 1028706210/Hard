---
id: java-collections-generics-data-structures
title: 数据结构
concepts: [data-structures, collections]
objectives:
  - 掌握数据结构的核心概念与使用方式。
  - 用正常、边界和失败输入验证数据结构。
prerequisites: [java-collections-generics-reflection]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-data-structures.html
source_snapshot_date: 2026-08-23
---

# 数据结构

Java 提供多种数据结构实现，包括栈、队列和链表，满足不同的存储和访问模式需求。

```java
import java.util.Stack;

public class Main {
    public static void main(String[] args) {
        Stack<Integer> s = new Stack<>();
        s.push(1); s.push(2); s.push(3);
        System.out.println(s.pop());
    }
}
```

Stack 是后进先出结构，push 入栈，pop 出栈返回栈顶元素。

```java
import java.util.ArrayDeque;
import java.util.Deque;

public class Main {
    public static void main(String[] args) {
        Deque<String> q = new ArrayDeque<>();
        q.offer("a"); q.offer("b");
        System.out.println(q.poll());
    }
}
```

Deque 作为先进先出队列，offer 入队，poll 出队返回队首元素。

## 概念定义与适用场景

数据结构解决的是数据组织与访问模式的问题。栈支持后进先出，队列支持先进先出，链表支持快速插入删除。

## 语法、API 与边界

本课使用 Stack 处理整数序列的入栈出栈操作。输入为逗号分隔整数，输出为反转序列。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

Stack 是较早的栈实现，JDK 17 并未将整个类标为弃用；其 API 推荐新代码优先采用 Deque 实现栈。选择数据结构应匹配访问模式。提交前应覆盖单元素、多元素和空序列的处理。

本次事实核对：[Java 17 官方 API](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Stack.html)。
