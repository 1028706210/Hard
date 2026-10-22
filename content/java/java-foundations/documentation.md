---
id: java-foundations-documentation
title: Java 文档注释
concepts: [variables, control-flow]
objectives:
  - 解释Javadoc 的公开契约在 Java 程序中的作用。
  - 用正常、边界和失败输入验证Java 文档注释。
prerequisites: []
difficulty: beginner
experience_points: 30
source_url: https://www.runoob.com/java/java-documentation.html
source_snapshot_date: 2026-08-23
---

# Java 文档注释

## 概念定义与适用场景

Javadoc 将源文件中的文档注释生成为 API 网页，帮助调用者了解方法做什么、接受什么参数、返回什么结果以及何时失败。文档注释使用 `/** ... */`，紧接在类、字段、构造或方法等声明之前；放在方法体内的普通说明不会因此成为该方法的 API 文档。`//` 和 `/* ... */` 也不会自动生成同样的 API 说明。

文档第一句话先概括行为，再解释边界。`@param` 描述参数，名称必须与声明相符；`@return` 描述返回值；`@throws` 描述失败条件及异常类型。void 方法与构造方法没有返回值，不能机械添加 @return。文档是契约说明，既不执行参数检查，也不代替代码中的 throw 或方法签名中的 throws。

## 语法、API 与边界

下面是本节唯一的独立 Java 程序，保存为 `Main.java`，使用 JDK 17 编译运行。预期输出 `9`、`rejected` 两行。平方方法只接受 0 到 46340，保证 int 乘法结果不溢出；约束同时写入文档和代码，让说明可与实现核对。

```java
/** 展示整数平方方法的公开契约。 */
public class Main {
    /**
     * 返回非负整数的平方。
     * <p>只接受能让结果放入 int 的本例范围。
     * 比较表达式可写为 {@code 0 <= value && value <= 46340}。
     *
     * @param value 范围为 0 到 46340（包含端点）的整数
     * @return value 的平方
     * @throws IllegalArgumentException value 为负数或超过 46340
     */
    public static int square(int value) {
        if (value < 0 || value > 46340) {
            throw new IllegalArgumentException("out of range");
        }
        return value * value;
    }

    /**
     * 运行一个成功调用和一个拒绝调用。
     * @param args 本示例不使用命令行参数
     */
    public static void main(String[] args) {
        System.out.println(square(3));
        try {
            square(-1);
        } catch (IllegalArgumentException error) {
            System.out.println("rejected");
        }
    }
}
```

在单独的示例目录中准备该源文件，并选择一个新的输出目录。以下是文档生成命令，不是第二段 Java 程序；在匹配的 JDK 17 工具链下运行后，打开 `api-docs/index.html`，查看 Main.square 的参数、返回值和异常区域。

```text
javadoc -encoding UTF-8 -docencoding UTF-8 -charset UTF-8 -d api-docs Main.java
```

`-encoding` 指源文件编码，`-docencoding` 指生成文档编码，`-charset` 指 HTML 字符集声明，`-d` 指输出目录。javadoc 生成 HTML，javac 编译程序，java 执行程序，三者验证的对象不同；网页存在或程序输出正确，都不能自动证明注释契约准确。

文档会解释 HTML，因此在普通描述里直接写小于号或与号可能被当作标签或实体。代码文本优先用 `{@code a < b && b > 0}`，无需手动处理其中的 HTML 特殊字符；只需显示普通字面内容可用 `{@literal List<String>}`。普通 HTML 描述中也可用 `&lt;`、`&gt;`、`&amp;` 表示相应字符。`{@link String}` 可建立 API 链接，不能把所有文本都当成可执行 HTML 插入。

源注释仍受 Java 的结束符规则约束：星号紧接斜线会关闭注释，即使出现在 code 标签中也不能直接当普通内容嵌入。标签语法、参数名和 HTML 结构可由 doclint 辅助发现常见错误，但工具不能判断“范围写错”或“失败行为说明与实现不一致”等语义问题。

## 常见错误与实践建议

不要只写“返回结果”或重复方法名，应明确单位、包含端点与失败条件。参数改名后同步 @param，异常策略变化后同步 @throws；声明异常不保证每次都会抛，文档写了异常也不会让编译器自动检查该约束。公开 API 的文档避免暴露机密、内部路径或无关实现细节。

原有代码练习仍保留原样：现有判定检查文本输出、空输入空行和非法标记失败；题面提到“Javadoc 风格前缀”，但现有参考输出没有额外前缀，本轮不为其自行发明格式。挑战题仍是 CSV 整数求和。这些输出测试都不能判断是否写了有效文档注释；本节的真正 Javadoc 示例及生成步骤属于新增教学，文档生成与页面阅读需独立验证。

参考：[JDK 17 文档注释规范](https://docs.oracle.com/en/java/javase/17/docs/specs/javadoc/doc-comment-spec.html)、[javadoc 命令](https://docs.oracle.com/en/java/javase/17/docs/specs/man/javadoc.html)。
