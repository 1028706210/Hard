---
id: java-capstone-quiz
title: Java 测验
concepts: [types, control-flow]
objectives:
  - 掌握Java 测验的核心概念与使用方式。
  - 用正常、边界和失败输入验证Java 测验。
prerequisites: [java-capstone-examples]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/quiz/java-quiz.html
source_snapshot_date: 2026-08-23
---

# Java 测验

Java 测验通过知识题和代码题验证对语言核心特性的理解。覆盖类型系统、控制流、集合和异常等主题。

```java
public class Main {
    public static void main(String[] args) {
        boolean[] answers = {true, true, false};
        int score = 0;
        for (boolean a : answers) if (a) score++;
        System.out.println(score);
    }
}
```

遍历布尔数组统计正确答案数量，是测验评分的基本模式。

```java
public class Main {
    public static void main(String[] args) {
        String[] qs = {"类型", "控制流", "集合"};
        for (int i = 0; i < qs.length; i++)
            System.out.println((i + 1) + ". " + qs[i]);
    }
}
```

格式化输出测验题目列表，索引从 1 开始更符合人类阅读习惯。

## 概念定义与适用场景

Java 测验解决的是语言知识掌握程度验证的问题。它通过知识题检查概念理解，通过代码题验证实践能力，覆盖类型系统、控制流和集合等主题。

## 语法、API 与边界

本课使用布尔数组统计处理答案序列输入。输入为逗号分隔 T/F，输出为正确答案数。空输入有明确结果，非法标记触发失败分支。

## 常见错误与实践建议

测验应覆盖不同难度层次。知识题答案位置不能全部相同。提交前应覆盖全对、全错和混合答案的评分验证。
