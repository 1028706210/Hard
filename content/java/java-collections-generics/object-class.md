---
id: java-collections-generics-object-class
title: Object 类
concepts: [classes, functions]
objectives:
  - 掌握Object 类的核心概念与使用方式。
  - 用正常、边界和失败输入验证Object 类。
prerequisites: [java-collections-generics-iterator]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-object-class.html
source_snapshot_date: 2026-08-23
---

# Object 类

## 概念定义与适用场景

Object 是类层次的根，数组也是对象并支持相应基础方法；基本类型 int 本身不是 Object 的子类，装箱后的 Integer 才是对象。常用基础方法包括 equals、hashCode、toString 和 getClass，它们的契约会影响日志、集合和类型判断。

Object 默认 equals 按对象身份判断，与引用的 == 一致。子类可以重写为领域中的值相等，例如 String 比较文本内容；因此不能笼统说“任意 equals 都比较字段内容”。== 对引用检查同一个对象或同为 null，不是永远错误，而是要与值比较区分。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `false`、`true`、`true`、`java.lang.String`。两个不同 String 对象内容相等；Objects.equals 为可能为 null 的引用提供安全比较。

```java
import java.util.Objects;
public class Main {
    public static void main(String[] args) {
        String first = new String("Ada");
        String second = new String("Ada");
        System.out.println(first == second);
        System.out.println(first.equals(second));
        System.out.println(Objects.equals(null, null));
        System.out.println(first.getClass().getName());
    }
}
```

equals 应满足自反、对称、传递、一致，并对 null 返回 false；相等对象必须返回相同 hashCode，反向不成立，不同对象可能哈希碰撞。只重写其中一个会破坏 HashSet/HashMap 的查找或去重。标识字段在入集合后变化同样危险。

第二个独立程序输出 `true`、`1`、`User:7`。final 的 User 用不可变 id 定义相等，并配套 hashCode；这个简单值对象不需为没有需求的字段提供 setter。

```java
import java.util.HashSet;
import java.util.Set;
final class User {
    private final int id;
    User(int id) { this.id = id; }
    @Override public boolean equals(Object other) {
        if (this == other) return true;
        if (!(other instanceof User user)) return false;
        return id == user.id;
    }
    @Override public int hashCode() { return Integer.hashCode(id); }
    @Override public String toString() { return "User:" + id; }
}
public class Main {
    public static void main(String[] args) {
        User first = new User(7);
        User second = new User(7);
        Set<User> users = new HashSet<>();
        users.add(first);
        users.add(second);
        System.out.println(first.equals(second));
        System.out.println(users.size());
        System.out.println(first);
    }
}
```

`toString` 供人阅读，不宜作为持久化协议；默认表示也不是可靠的内存地址。`getClass` 获得实际运行时类，与 instanceof 判断是否兼容某父类型不同。Object 的 clone 不会自动提供业务需要的深拷贝；wait/notify 属于监视器协作，需要并发契约，不因所有对象都有这些方法就可随意调用。资源释放不应依赖 finalize。

## 常见错误与实践建议

equals 的参数要写 Object，误写为 `equals(User)` 只是重载，不能替代集合调用的 Object.equals。用 `@Override` 帮助编译器检查。toString 避免输出密码或令牌；比较策略应清晰稳定，继承层次中的值相等尤其需要谨慎设计。

现有练习仍读取两个以空格分隔的字符串，使用 equals 输出布尔结果。自定义值对象、哈希集合及 getClass 是新增教学示例，原题没有对这些行为做全量验证。

参考：[Java 17 Object 方法契约](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Object.html)、[JLS 17 引用类型](https://docs.oracle.com/javase/specs/jls/se17/html/jls-4.html#jls-4.3)。
