# Java 教学深度第一轮补充

日期：2026-10-21。范围仅为 `content/java/**` 与本 Java 审计目录。本轮沿用 JDK 17 教学基线；不安装工具、不修改环境、不改 API、前端、依赖、Git 状态或用户数据。共享概念清单由总控另行整合，本目录只给出建议。

## 实际改动

逐课审查全路线 57 节正文、课程来源映射和练习题面后，优先补充 20 节：

| 课程组 | 深化的课时 | 新增的关键教学内容 |
| --- | --- | --- |
| 基础 | 对象和类、基本数据类型、变量类型、文档注释 | 类/对象/引用、static 与实例状态、别名与 null、八种基本类型、数值扩大与缩小、运算提升和溢出、装拆箱、作用域、默认值、final 与 var、Javadoc 参数/返回/异常、生成命令与 HTML 边界 |
| 构造 | 构造方法 | 默认构造的生成条件、重载、this/super 链、Java 17 首语句要求、初始化顺序、构造失败与可重写方法风险 |
| 面向对象与异常 | 继承、Override 与 Overload、多态、抽象类、封装、接口、异常处理 | 访问边界、字段隐藏、重载/重写两阶段选择、类型转换、抽象中间层、default/static/private 接口方法、状态约束与防御性复制、受检异常、传播、资源关闭与抑制异常 |
| 容器与泛型 | 集合框架、ArrayList、LinkedList、HashSet、HashMap、Iterator、Object 类、泛型 | Collection/Map 分立、顺序与重复、快照和视图、容量与大小、删除重载、查找成本、相等/哈希契约、可变键风险、迭代器状态与 fail-fast、泛型类/方法、上界/下界、不变性和擦除限制 |

其中 19 节每节提供两个可分别保存为 `Main.java` 的独立示例，文档注释另提供一个独立程序及一段文档生成命令，共 39 个可运行 Java 示例，并在正文明确预期结果。所有新增说明为自行组织的中文教学内容，官方文档用于技术规则核对。原课时题目仍保持较窄练习范围，正文逐节说明练习验证不了哪些扩展主题。

另有 3 节仅作事实纠正，未算入上述深化数量：

- 数据结构：Stack 在 JDK 17 没有整类弃用；官方推荐新代码优先使用 Deque。
- 日期时间：Date、Calendar 在 JDK 17 没有整类弃用；Date 部分旧方法被弃用。
- String：length 返回 UTF-16 代码单元数，不必等于 Unicode 码点数或可见字符数。

原有“接口不提供实现”“抽象类不应有全部具体实现”“构造不能有任何 return”“泛型消除所有运行时 ClassCastException”“中间插入就应选 LinkedList”等过度概括，已在相应深化课时中纠正。

## 保留的契约

[provenance-r2.json](provenance-r2.json) 以本代理开始时的 [baseline.json](baseline.json) 为基线，保存前后 SHA-256。最终 23 个 Markdown 正文变化，34 个课时正文未变；57 份练习 JSON 和 course.yaml 的 SHA-256 均相同。Java 代理曾先将所有 frontmatter 逐字恢复（第一阶段证据见 [provenance.json](provenance.json)）；随后总控明确确认，仅在 types、classes、encapsulation、interfaces 的目标课时追加 4 个 concepts 标签。最终证据单独列出这 4 处总控改动；全部其他元数据字段、目标、稳定 ID、前置关系、XP 和来源保持不变。39 份当前代码 SHA 与对应运行清单一致，即使总控的标签整合改变了完整课文 SHA，已运行代码本身也未变化。此前已有未提交修复保留，未使用重置操作。

[mapping-suggestions.json](mapping-suggestions.json) 给出 classes、types、interfaces、encapsulation、collections、generics 六项 Java 对照建议。建议中的代码是对照面板片段，非独立程序；另列五份课时概念标签的候选调整，仅供共享文件负责人决定，Java 代理未将建议直接写入 frontmatter；最终总控整合的 4 个标签变更单独记在 provenance-r2.json。

## 覆盖矩阵与余项

[coverage-matrix.md](coverage-matrix.md) / [coverage-matrix.json](coverage-matrix.json) 逐行列出 57 节已有讲解、部分讲解和待补子主题。来源登记有 57 个 Java 条目，课程课时的来源 URL 均唯一匹配，证明映射一致；不据此推断正文与来源章节等量。

本轮是重点深度补充，完整路线 57 节整体仍为 partial，均有矩阵列出的 remaining 子主题。文档注释课原来缺少相关示例，已在本轮立即改为真实 Javadoc 教学；其高级文档组织和实际页面审阅仍待后续验证。partial 并非等于没有教学，而是仍存在未教主题。矩阵不将字符数、目录数或静态校验结果换算为课程完整率。

后续优先补充 Javadoc 文档生成与页面审阅、基础语法/控制流的完整讲解、方法参数按值传递、数组与字符串边界、真实文件/字节字符流教学、反射调用、同步/可见性/中断、离线网络示例、JDBC 资源/事务/参数绑定、Java 8/9 版本边界。邮件地址的简化正则、网络地址解析、串行求和及 JDBC 前缀检查均不能代替对应工程能力。

## 验证记录

- 文档注释修正后重新运行 `tools/content/validate.py --language java --require-complete`，退出码 0；仍为 1 门课程、57 节课、57 份练习，errors 为空。最新原始输出见 [validation-r2.stdout.txt](validation-r2.stdout.txt)、[validation-r2.stderr.txt](validation-r2.stderr.txt)，命令见 [validation-r2.json](validation-r2.json)；第一阶段 validation.* 保留。此校验不等同于 Java 编译或教学完整度认证。
- [examples.json](examples.json) 保存最初 38 个示例源码、预期 stdout 和 SHA；[documentation-example.json](documentation-example.json) 保存后补的 1 个 Javadoc 程序。清单保留提取时 prepared_not_run 状态，真实执行结果以运行产物为准。
- 总控使用 JDK 17 串行实跑：第一阶段 [example-run-001/results.json](example-run-001/results.json) 为 38/38 通过，补充阶段 [example-run-002/results.json](example-run-002/results.json) 为 1/1 通过，合计 39/39。本代理已读取两份结果，并核对全部代码 SHA 仍与当前正文相符。没有把编译运行结果扩展为所有题目、浏览器或教学完整度通过。
- [run-examples.py](run-examples.py) 先验证完整课文 SHA，要求指定 javac/java 和全新输出目录，仅允许在本审计目录内。`--manifest documentation-example.json` 可仅运行新增一例。它不执行课程 Runner、练习全套测试或外部 IO。最初 38 例清单在总控追加 concepts 标签之前提取；如需重新运行，应先建立新的当前课文快照，不能绕过 SHA 检查。
- javadoc 文档生成命令已在正文明确提供，但本轮未执行文档生成、未读生成页面；39 个程序运行通过不能替代该验证。本文故意编译失败反例以行内说明展示，不包含在成功运行示例中。

## 核对的官方规则

以下均以 Java SE 17 为版本边界，在本轮联网读取；菜鸟来源继续承担课程目录溯源，不作为 Java 规则的唯一依据。

- [JLS 4：类型、值、变量](https://docs.oracle.com/javase/specs/jls/se17/html/jls-4.html)、[JLS 5：转换与上下文](https://docs.oracle.com/javase/specs/jls/se17/html/jls-5.html)：类型/范围、字段默认值、类型变量、擦除、扩大/缩小与装拆箱。
- [JLS 6：名称与访问控制](https://docs.oracle.com/javase/specs/jls/se17/html/jls-6.html)、[JLS 8：类](https://docs.oracle.com/javase/specs/jls/se17/html/jls-8.html)、[JLS 9：接口](https://docs.oracle.com/javase/specs/jls/se17/html/jls-9.html)：继承、构造、重载/重写、接口成员和默认方法。
- [JLS 11：异常](https://docs.oracle.com/javase/specs/jls/se17/html/jls-11.html)、[JLS 12：执行](https://docs.oracle.com/javase/specs/jls/se17/html/jls-12.html)、[JLS 14：语句](https://docs.oracle.com/javase/specs/jls/se17/html/jls-14.html)、[JLS 15：表达式](https://docs.oracle.com/javase/specs/jls/se17/html/jls-15.html)：异常层次、初始化、资源关闭、局部变量、方法调用选择。
- [Object](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Object.html)、[String](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/String.html)：基础方法契约与 UTF-16 表示。
- [java.util 集合入口](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/package-summary.html)、[List](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/List.html)、[ArrayList](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/ArrayList.html)、[LinkedList](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/LinkedList.html)、[Deque](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Deque.html)、[Iterator](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Iterator.html)、[HashSet](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashSet.html)、[HashMap](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/HashMap.html)、[Map](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html)：修改能力、顺序、null、复杂度、删除与遍历契约。
- [Oracle 泛型通配符教程](https://docs.oracle.com/javase/tutorial/java/generics/wildcards.html)、[泛型限制](https://docs.oracle.com/javase/tutorial/java/generics/restrictions.html)：作为补充解释材料；该教程以 JDK 8 为背景，本课行为还对照 JLS 17。
- [JDK 17 文档注释规范](https://docs.oracle.com/en/java/javase/17/docs/specs/javadoc/doc-comment-spec.html)、[javadoc 命令](https://docs.oracle.com/en/java/javase/17/docs/specs/man/javadoc.html)：核对标签、生成和 HTML 处理边界。
- [Stack](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Stack.html)、[Date](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Date.html)、[Calendar](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Calendar.html)：核对整类弃用说法。

实际使用能力：本地文件读取/写入、内容校验工具、SHA-256 契约比对，以及联网读取 Oracle 官方资料。未调用外部文档写入、发布或消息服务。
