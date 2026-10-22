---
id: java-collections-generics-hashmap
title: HashMap
concepts: [collections, data-structures]
objectives:
  - 掌握HashMap的核心概念与使用方式。
  - 用正常、边界和失败输入验证HashMap。
prerequisites: [java-collections-generics-hashset]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-hashmap.html
source_snapshot_date: 2026-08-23
---

# HashMap

## 概念定义与适用场景

HashMap 将每个唯一键关联到一个值，适合按键查询、频次统计和建立索引。同一键再次 put 替换其值，键数量不增加；不同键可以拥有相同值。它不是 Collection，也不保证迭代顺序。哈希分布合理时，基本 get/put 通常有常量时间性能。

键的 equals/hashCode 决定是否为同一键，其契约与 HashSet 相同。插入后修改参与键比较的字段会破坏可查找性，优先选择 String 等不可变键。HashMap 允许一个 null 键和多个 null 值，但这不是所有 Map 实现的共同保证。

## 语法、API 与边界

以下独立 `Main.java` 程序输出 `null`、`10`、`20`、`1`。put 返回之前的值；首次插入返回 null。这里没有存 null 值，所以可把首次 null 理解为此前不存在；一般场景还需 containsKey 区分。

```java
import java.util.HashMap;
import java.util.Map;
public class Main {
    public static void main(String[] args) {
        Map<String, Integer> scores = new HashMap<>();
        System.out.println(scores.put("Ada", 10));
        System.out.println(scores.put("Ada", 20));
        System.out.println(scores.get("Ada"));
        System.out.println(scores.size());
    }
}
```

get 对不存在的键返回 null，`containsKey` 能判断是否存在映射。`getOrDefault(k,d)` 只在不存在映射时给默认值；若已映射到 null，仍返回 null。将该结果自动拆箱为 int 可能抛 NullPointerException。

第二个独立程序输出 `2`、`1`、`2`。默认值 0 表示尚未出现，更新后保存次数。HashMap 中数据无序，但按确定的键查询得到确定输出；若需要按键排序整张表，可使用 TreeMap。

```java
import java.util.HashMap;
import java.util.Map;
public class Main {
    public static void main(String[] args) {
        Map<String, Integer> counts = new HashMap<>();
        for (String word : new String[]{"a", "b", "a"}) {
            counts.put(word, counts.getOrDefault(word, 0) + 1);
        }
        System.out.println(counts.get("a"));
        System.out.println(counts.get("b"));
        System.out.println(counts.size());
    }
}
```

遍历键值对可用 entrySet；只需要键或值时分别用 keySet、values。它们是关联原映射的视图，不是独立快照。需要输出顺序时应明确选择 LinkedHashMap 的插入顺序或 TreeMap 的排序规则，不能依赖某次运行的 HashMap 顺序。

## 常见错误与实践建议

不要把“唯一词数”与“每个词出现次数”混为一谈：前者为 map.size，后者为每个键对应的值。HashMap 不自动同步，`getOrDefault` 后再 put 的复合统计也不是并发原子更新；并发需求应单独设计。

本课练习仍读取逗号分隔字符串，经 HashMap 统计后只输出唯一词数，不增加频率明细。null、视图与多线程更新属于教学边界，原有计数测试不能证明这些行为都已掌握。

参考：[Java 17 HashMap](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html)、[Map 契约](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html)。
