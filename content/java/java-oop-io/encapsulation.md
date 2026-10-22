---
id: java-oop-io-encapsulation
title: 封装
concepts: [classes, security, encapsulation]
objectives:
  - 掌握封装的核心概念与使用方式。
  - 用正常、边界和失败输入验证封装。
prerequisites: [java-oop-io-abstraction]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-encapsulation.html
source_snapshot_date: 2026-08-23
---

# 封装

## 概念定义与适用场景

封装的重点是让状态只能经过维护约束的操作改变，而不是给每个字段自动生成 getter 和 setter。账户余额可提供 deposit 行为，不一定允许调用者随意 setBalance。private 限制直接访问，构造方法和公开方法共同维护状态始终有效。

访问控制是代码结构边界，不自动等同于加密、权限系统或线程安全。即使字段是 private，如果 getter 返回可变对象的原引用，调用者仍可能绕过方法约束修改内部数据。final 引用同样只能阻止重新赋值，不能冻结其指向对象。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `true`、`false`、`100`。存款先检查再修改，失败返回 false，余额不变；Math.addExact 检测整数溢出，避免默默破坏非负余额约束。

```java
class Account {
    private int balance;
    boolean deposit(int amount) {
        if (amount <= 0) return false;
        balance = Math.addExact(balance, amount);
        return true;
    }
    int getBalance() { return balance; }
}
public class Main {
    public static void main(String[] args) {
        Account account = new Account();
        System.out.println(account.deposit(100));
        System.out.println(account.deposit(-5));
        System.out.println(account.getBalance());
    }
}
```

第二个独立程序输出 `1`。构造时复制传入列表，读取时返回不可修改的快照，所以外部清空 original 不会影响对象。`List.copyOf` 不接受 null 元素，本例使用 Integer 等不可变元素；仅复制容器不会深复制其中的可变对象。

```java
import java.util.ArrayList;
import java.util.List;
class Scores {
    private final List<Integer> values;
    Scores(List<Integer> values) { this.values = new ArrayList<>(values); }
    List<Integer> snapshot() { return List.copyOf(values); }
}
public class Main {
    public static void main(String[] args) {
        List<Integer> original = new ArrayList<>(List.of(90));
        Scores scores = new Scores(original);
        original.clear();
        System.out.println(scores.snapshot().size());
    }
}
```

选择“拒绝并返回标记”还是“抛出异常”应与调用契约一致，不能让调用者误以为操作成功。不可变设计适用于状态创建后无需变化的值对象；需要变化的业务对象则应提供少量清晰操作。涉及并发修改时还要另行设计同步，不能仅依靠 private。

## 常见错误与实践建议

不要让 setter 先写入非法值再校验。对集合字段，说明返回的是快照、视图还是直接引用；快照和深拷贝不是一回事。getter 也不是越多越好，应仅暴露调用者实际需要的数据。

现有练习只读取整数金额：正数输出 `DEPOSITED:金额`，否则输出 `REJECTED`。本节 Account 示例用于讲状态保护，不改变该题的输出格式或原有判题输入范围。防御性复制和溢出处理尚需额外练习才能验证。

参考：[JLS 17 访问控制](https://docs.oracle.com/javase/specs/jls/se17/html/jls-6.html#jls-6.6)、[List.copyOf 契约](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/List.html#copyOf(java.util.Collection))。
