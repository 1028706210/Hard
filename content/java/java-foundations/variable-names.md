---
id: java-foundations-variable-names
title: Java 变量命名规则
concepts: [variables, control-flow]
objectives:
  - 解释合法标识符和语义命名在 Java 程序中的作用。
  - 用正常、边界和失败输入验证Java 变量命名规则。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-variable-naming-rules.html
source_snapshot_date: 2026-08-23
---

# Java 变量命名规则

## 概念定义与适用场景

合法字符只是命名的第一步，还应避开关键字并表达用途。使用JDK的检查函数可减少自己维护字符表的错误；上下文关键字和业务可读性仍需单独判断。

## 语法、API 与边界

读取并trim一段文本。使用SourceVersion.isIdentifier并排除SourceVersion.isKeyword(text, RELEASE_17)，输出它是否是JDK17可用标识符形状。空文本为false；关键字、字面量true/false/null和单独下划线不允许；Unicode名称可由该API识别。本题不检查名称语义，也不覆盖所有上下文相关限制。

```java
import java.nio.charset.StandardCharsets;
import javax.lang.model.SourceVersion;
public class Main {

    public static void main(String[] args) throws Exception {
        String text = new String(System.in.readAllBytes(), StandardCharsets.UTF_8).trim();
        boolean valid = SourceVersion.isIdentifier(text) && !SourceVersion.isKeyword(text, SourceVersion.RELEASE_17);
        System.out.println(valid);
    }
}
```

## 常见错误与实践建议

先确认输入与边界，再计算并输出。 编译通过只代表语法与类型检查通过，不能代替输出验证；自动判题也不能评价注释质量或完整设计。

## 形状合法仍可能是关键字

下列是独立语法片段，方法内语句放入 main 中观察；类声明片段用于说明字段结构。

```java
boolean shape = javax.lang.model.SourceVersion.isIdentifier("class");
boolean keyword = javax.lang.model.SourceVersion.isKeyword("class");
System.out.println(shape && !keyword); // false
```
