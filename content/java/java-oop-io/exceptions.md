---
id: java-oop-io-exceptions
title: 异常处理
concepts: [exceptions, control-flow]
objectives:
  - 掌握异常处理的核心概念与使用方式。
  - 用正常、边界和失败输入验证异常处理。
prerequisites: [java-oop-io-files-io]
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-exceptions.html
source_snapshot_date: 2026-08-23
---

# 异常处理

## 概念定义与适用场景

异常将失败信息从发生点传给能处理它的调用者；抛出后，当前路径中未执行的后续语句被跳过，并逐层寻找匹配 catch。`throw` 抛出一个异常对象，`throws` 在方法签名声明可能传播的异常，它本身不处理错误，也不表示每次调用都会失败。

异常对象属于 Throwable 层次。RuntimeException 及其子类和 Error 及其子类属于非受检异常；其余异常属于受检异常，编译器要求在可能传播的位置捕获或声明。例如 IOException 是受检异常，NumberFormatException 是非受检异常。通常不应捕获 Error 来当作普通业务失败继续运行。

## 语法、API 与边界

以下独立 `Main.java` 程序依次输出 `OK:12`、`done`、`ERROR`、`done`。catch 只处理解析失败，finally 在本例两条正常离开 try/catch 的路径中都会执行。用 parseInt 并捕获 NumberFormatException 处理外部文本是合理的，不需要为避免异常而重新实现整数解析器。

```java
public class Main {
    static void parse(String text) {
        try {
            int value = Integer.parseInt(text);
            System.out.println("OK:" + value);
        } catch (NumberFormatException error) {
            System.out.println("ERROR");
        } finally {
            System.out.println("done");
        }
    }
    public static void main(String[] args) {
        parse("12");
        parse("abc");
    }
}
```

有多个 catch 时应先具体子类、后更一般父类；否则前面的父类 catch 已截获后续类型，编译器会报告不可达。`catch (IOException | IllegalArgumentException e)` 可合并不具有父子包含关系的候选。捕获后要恢复、转换或传播，不能悄悄吞掉错误而输出成功结果。

资源应优先采用 try-with-resources。资源实现 AutoCloseable 后会在离开语句时关闭；多个资源按声明的反序关闭。第二个独立程序不访问外部文件，输出 `work`、`close:B`、`close:A`、`caught:failed`。

```java
class Resource implements AutoCloseable {
    private final String name;
    Resource(String name) { this.name = name; }
    public void close() { System.out.println("close:" + name); }
}
public class Main {
    public static void main(String[] args) {
        try (Resource first = new Resource("A");
             Resource second = new Resource("B")) {
            System.out.println("work");
            throw new IllegalStateException("failed");
        } catch (IllegalStateException error) {
            System.out.println("caught:" + error.getMessage());
        }
    }
}
```

若主体抛异常而 close 也失败，关闭异常通常记为主体异常的 suppressed 异常，可用 getSuppressed 检查；不能简单认为只会留最后一个失败。finally 也不是在进程退出、被强制终止等情况下都保证执行。尤其不要在 finally 返回值或再抛新异常而掩盖原错误。

## 常见错误与实践建议

已知集合边界用条件判断，不要故意越界再 catch 作为遍历结束方式；但外部文本解析失败本就是 API 的异常契约。只在能做出有效处理的位置捕获。包装异常时保留 cause，例如 `new IllegalStateException("load failed", error)`，并避免将凭证或敏感输入放进错误消息。

现有练习仍是读取字符串，解析成功输出 `OK:值`，失败输出 `ERROR`。资源关闭、受检异常声明和多层传播不在原有代码题的完整验收范围内，不能把简单解析测试当成异常处理全覆盖。

参考：[JLS 17 异常种类与检查](https://docs.oracle.com/javase/specs/jls/se17/html/jls-11.html)、[try 语句与资源管理](https://docs.oracle.com/javase/specs/jls/se17/html/jls-14.html#jls-14.20)。
