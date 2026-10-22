---
id: java-core-api-character
title: Character 类
concepts: [types, strings]
objectives:
  - 掌握Character 类的核心 API 与使用方式。
  - 用正常、边界和失败输入验证Character 类。
prerequisites: [java-core-api-number-math]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-character.html
source_snapshot_date: 2026-08-23
---

# Character 类

Character 类包装基本类型 char，提供字符分类和转换方法，让字符可以在需要对象的场景中使用。

```java
public class Main {
    public static void main(String[] args) {
        char ch = 'a';
        System.out.println(Character.isDigit(ch));
        System.out.println(Character.toUpperCase(ch));
    }
}

```

Character.isDigit 判断字符是否为数字，toUpperCase 将小写字母转为大写。

```java
public class Main {
    public static void main(String[] args) {
        char ch = '5';
        System.out.println(Character.isLetter(ch));
        System.out.println(Character.getNumericValue(ch));
    }
}

```

Character.isLetter 判断是否字母，getNumericValue 将数字字符转为对应数值。

## 概念定义与适用场景

Character 类解决的是单字符的判断与转换问题。它包装 char 基本类型，提供静态方法完成字符分类（isDigit、isLetter）和大小写转换。

## 语法、API 与边界

本课只使用 Character 类的静态方法处理单字符输入。输入为一个字符，输出为转换或判断结果。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

不要把 char 当作 String 处理。char 使用单引号，String 使用双引号。提交前应覆盖字母、数字和特殊字符的分类判断。
