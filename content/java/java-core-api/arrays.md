---
id: java-core-api-arrays
title: 数组
concepts: [collections, control-flow]
objectives:
  - 掌握数组的核心 API 与使用方式。
  - 用正常、边界和失败输入验证数组。
prerequisites: [java-core-api-stringbuffer]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-array.html
source_snapshot_date: 2026-08-23
---

# 数组

数组是固定长度的同类型元素序列。Java 数组通过索引访问元素，配合 for 循环完成遍历和排序等操作。

```java
public class Main {
    public static void main(String[] args) {
        int[] nums = {3, 1, 2};
        for (int i = 0; i < nums.length; i++) {
            System.out.println(nums[i]);
        }
    }
}

```

数组用索引 0 开始访问，length 属性返回元素个数，for 循环逐个遍历。

```java
import java.util.Arrays;

public class Main {
    public static void main(String[] args) {
        int[] nums = {3, 1, 2};
        Arrays.sort(nums);
        System.out.println(Arrays.toString(nums));
    }
}

```

Arrays.sort 就地排序，Arrays.toString 将数组转为可读的字符串表示。

## 概念定义与适用场景

数组解决的是固定长度同类型元素的存储与遍历问题。它通过索引提供 O(1) 随机访问，但长度不可改变。

## 语法、API 与边界

本课使用数组和 Arrays 工具类处理数值序列输入。输入为逗号分隔的整数，输出为排序或统计结果。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要混淆数组 length 属性与 String 的 length() 方法。数组索引越界会抛出异常。提交前应覆盖单元素、多元素和重复值的处理。
