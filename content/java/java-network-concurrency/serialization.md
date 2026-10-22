---
id: java-network-concurrency-serialization
title: 序列化
concepts: [io, memory]
objectives:
  - 掌握序列化的核心概念与使用方式。
  - 用正常、边界和失败输入验证序列化。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-serialization.html
source_snapshot_date: 2026-08-23
---

# 序列化

序列化将对象状态转为字节流，反序列化从字节流恢复对象。Java 通过 Serializable 接口标记可序列化类。

```java
import java.io.*;

class Person implements Serializable {
    String name; int age;
    Person(String n, int a) { name = n; age = a; }
}
public class Main {
    public static void main(String[] args) throws Exception {
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        new ObjectOutputStream(bos).writeObject(new Person("Alice", 30));
        System.out.println(bos.size() > 0);
    }
}
```

Serializable 接口标记类可序列化，ObjectOutputStream 将对象写入字节流。

```java
import java.io.*;

class Point implements Serializable {
    int x, y;
    Point(int x, int y) { this.x = x; this.y = y; }
}
public class Main {
    public static void main(String[] args) throws Exception {
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(bos);
        oos.writeObject(new Point(3, 4));
        ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(bos.toByteArray()));
        Point p = (Point) ois.readObject();
        System.out.println(p.x + "," + p.y);
    }
}
```

序列化到内存再反序列化恢复对象，字段值保持一致。

## 概念定义与适用场景

序列化解决的是对象状态持久化与传输的问题。它将对象转为字节流，可写入文件或通过网络发送，接收端反序列化恢复对象。

## 语法、API 与边界

本课模拟序列化格式处理对象数据输入。输入为名称和年龄，输出为序列化表示。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要序列化敏感字段（用 transient 标记）。序列化版本应声明 serialVersionUID。提交前应覆盖正常对象、边界值和反序列化恢复的验证。
