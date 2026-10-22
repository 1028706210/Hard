# Java 全路线教学深度矩阵

日期：2026-10-21。逐课阅读 57 节本地正文与练习题面，结合课程 source_coverage、sources 清单及 Java SE 17 官方规则审查。这里不将目录映射等同于正文等量，也未逐页比对菜鸟全文。

covered / partial / remaining 是子主题状态：covered 表示所列内容已有明确解释；partial 表示有内容但深度或示例不足；remaining 表示尚未充分教学。57 节路线整体均为 partial，均有 remaining 子主题。20 节本轮深化（含审计后立即修正的文档注释）、3 节仅纠正事实、34 节本轮未改；不产生完整率百分比。

| 课时 | 本轮处理 / 路线状态 | covered：已有明确讲解 | partial：尚不足处 | remaining：后续子主题 |
| --- | --- | --- | --- | --- |
| [Java 教程](../../../../content/java/java-foundations/tutorial.md) | not_changed / partial | Main/字节码/问候输入输出 | 编译运行链仅简述 | 命令行编译诊断；源文件与类路径；最小程序分步导读 |
| [Java 简介](../../../../content/java/java-foundations/introduction.md) | not_changed / partial | 静态类型；long 边界；JVM 简述 | Java 平台概况只点到为止 | JDK/JRE/JVM 区别；用途与限制；编译执行流程 |
| [Java 开发环境配置](../../../../content/java/java-foundations/environment.md) | not_changed / partial | javac/java 分工；版本记录不是本机证据 | 练习仅比较版本号 | 安装与工具链路径检查；JAVA_HOME/PATH；编译运行排错 |
| [Java 基础语法](../../../../content/java/java-foundations/basic-syntax.md) | not_changed / partial | main 框架；类型声明；分号；局部初始化 | 示例集中于 n+1 | 标识符与关键字；大小写；语句/代码块；类/文件组织 |
| [Java 注释](../../../../content/java/java-foundations/comments.md) | not_changed / partial | 行/块/文档注释用途；单位约束 | 代码主要展示行注释 | 三类注释真实语法；块注释不能嵌套；注释与代码同步 |
| [Java 对象和类](../../../../content/java/java-foundations/objects-classes.md) | depth_pass / partial | 类/对象/引用；实例与 static；this；构造；别名；null；引用按值传递 | 练习只验证两实例姓名 | 成员/局部/匿名类；详细可达性与 GC；对象建模练习 |
| [Java 基本数据类型](../../../../content/java/java-foundations/basic-data-types.md) | depth_pass / partial | 八种基本类型；位宽值域；引用类型；扩/缩转换；精度；提升；溢出；装/拆箱 | 浮点特殊值仅概述 | NaN/无穷运算；浮点转整数极值规则；BigDecimal 实用 |
| [Java 变量类型](../../../../content/java/java-foundations/variable-types.md) | depth_pass / partial | 字段/局部/形参/static；默认值；this；作用域；final 可变对象；var 静态推断 | 练习主要观察局部与字段 | 捕获变量 effectively final；复杂 definite-assignment 分支 |
| [Java 变量命名规则](../../../../content/java/java-foundations/variable-names.md) | not_changed / partial | 标识符 API；关键字排除；Unicode；上下文限制提示 | 语义命名仅提示 | 大小写约定与常量/类/包命名；上下文关键字实例 |
| [Java 修饰符](../../../../content/java/java-foundations/modifiers.md) | not_changed / partial | private/public/final/static；getter；线程安全边界提示 | 访问控制未形成完整矩阵 | 包级/protected；跨包接收者规则；abstract/synchronized/transient/volatile |
| [Java 运算符](../../../../content/java/java-foundations/operators.md) | not_changed / partial | 余数符号；除零检查；短路简述 | 题目聚焦余数 | 算术/关系/逻辑/位运算；移位；优先级；自增；三元；复合赋值 |
| [Java 循环结构](../../../../content/java/java-foundations/loops.md) | not_changed / partial | for/while；边界；累加；防止空循环 | 仅两类循环演示 | do-while；break/continue；嵌套循环；增强 for；带标签跳转 |
| [Java 条件语句](../../../../content/java/java-foundations/conditions.md) | not_changed / partial | if/else；阈值归属；合法未通过与非法区分 | 单一成绩分支 | else-if；嵌套；复合布尔条件；分支穷尽与可读性 |
| [Java switch case](../../../../content/java/java-foundations/switch.md) | not_changed / partial | switch 表达式；箭头；default；整数映射 | 传统贯穿仅一句对比 | 冒号/break；String/enum 分支；yield；null 行为与类型限制 |
| [Java 文档注释](../../../../content/java/java-foundations/documentation.md) | depth_pass / partial | 真实 /** */ 位置与用途；@param/@return/@throws 与公开契约；独立示例与异常边界；javadoc 生成命令与编码选项；HTML 实体、code/literal/link 和注释结束符边界；doclint 与语义验证区别 | 生成文档与页面阅读尚未由本代理执行；原输出练习不能评价注释质量 | 继承文档与 inheritDoc；包/模块文档；链接失效检查与大型 API 文档组织 |
| [Number 与 Math 类](../../../../content/java/java-core-api/number-math.md) | not_changed / partial | Math.max/abs/PI/round；整数与浮点除法 | Number 层次仅概述 | 包装 API/parse/valueOf；Number 转换；abs 最小值；round 负半数/NaN 边界 |
| [Character 类](../../../../content/java/java-core-api/character.md) | not_changed / partial | char 包装；isDigit/isLetter；toUpperCase；数值转换 | 只演示 BMP 中简单字符 | 码点与代理对；int 重载；大小写映射限制；非 ASCII 数字 |
| [String 类](../../../../content/java/java-core-api/string.md) | factual_correction / partial | 不可变；equals/==；substring；length 已纠正为 UTF-16 单元 | 字符与码点边界尚无实例 | 码点操作；编码；split 正则与空字段；查找/替换/连接；常量池边界 |
| [StringBuffer 类](../../../../content/java/java-core-api/stringbuffer.md) | not_changed / partial | 可变序列；append/reverse；charAt；StringBuilder 对照 | 线程安全表述未解释复合操作 | capacity/length；insert/delete/setCharAt；链式调用；复合操作同步边界 |
| [数组](../../../../content/java/java-core-api/arrays.md) | not_changed / partial | 固定长度；0 基索引；遍历；Arrays.sort/toString | 只展示一维数组 | 默认值；别名/复制；多维/不规则数组；Arrays.equals；引用数组协变风险 |
| [日期时间](../../../../content/java/java-core-api/date-time.md) | factual_correction / partial | LocalDate parse/of/plusDays；不可变；跨年；纠正旧类弃用说法 | LocalTime/LocalDateTime 只列名称 | Instant/ZonedDateTime；时区/夏令时；Period/Duration；格式化/严格解析 |
| [正则表达式](../../../../content/java/java-core-api/regex.md) | not_changed / partial | Pattern/Matcher；find 与 matches；Java 双重转义提示 | 分组仅列名称 | 量词/锚点/字符类；group；replaceAll；Pattern.quote；回溯成本 |
| [方法](../../../../content/java/java-core-api/methods.md) | not_changed / partial | static 方法；参数/返回；递归和终止条件 | 按值传递仅一句话 | 引用参数重绑与对象修改；可变参数；实例/static 对比；方法签名/重载流程 |
| [构造方法](../../../../content/java/java-core-api/constructors.md) | depth_pass / partial | 同名无返回类型；默认构造条件；重载/this/super；初始化顺序；失败；return 边界 | 练习主要初始化字段并格式化 | 类初始化完整顺序；复杂继承构造诊断；静态工厂取舍 |
| [Scanner 类](../../../../content/java/java-core-api/scanner.md) | not_changed / partial | token；hasNextInt/nextInt；next；资源提醒 | 多行与混合类型未完整演示 | nextLine 混读；分隔符/Locale；非法 token 消费；关闭 System.in 所有权 |
| [Stream/File/IO](../../../../content/java/java-oop-io/files-io.md) | not_changed / partial | Path.of；文件名/父目录/组件数 | 没有实际流读取或文件内容读写 | 字节流/字符流；UTF-8；缓冲；资源关闭；Files 实读写；IO 错误 |
| [异常处理](../../../../content/java/java-oop-io/exceptions.md) | depth_pass / partial | Throwable 分层；受检/非受检；throw/throws；传播；catch 顺序；finally 限制；资源关闭/抑制异常 | 受检异常与 suppressed 仅解释，未真实失败双异常示范 | 自定义异常；复杂异常链；受检声明编译反例；真实 IO 恢复策略 |
| [继承](../../../../content/java/java-oop-io/inheritance.md) | depth_pass / partial | is-a/组合；单类多接口；访问边界；super 构造/方法；final/private；字段隐藏 | 跨包 protected 接收者限制仅提示 | 跨包多文件实例；sealed 类型层次；替换原则系统练习 |
| [Override 与 Overload](../../../../content/java/java-oop-io/override-overload.md) | depth_pass / partial | 编译期重载/运行期重写；签名；协变；权限/受检异常约束；装箱优先级；null 歧义 | 复杂重载规则未穷尽 | 可变参数重载；泛型桥接；受检异常和协变返回编译反例 |
| [多态](../../../../content/java/java-oop-io/polymorphism.md) | depth_pass / partial | 声明/实际类型；多实现循环；向上/下转换；instanceof 模式；null；字段/static 边界 | 练习仅面积计算 | 替换契约设计；多层分派诊断；接口组合进阶 |
| [抽象类](../../../../content/java/java-oop-io/abstraction.md) | depth_pass / partial | 不能直接实例化；共享状态/构造/实现；可无抽象方法；具体/抽象中间层；修饰符冲突；接口取舍 | 几何练习验证范围窄 | 多层模板方法设计；抽象类演化兼容性；sealed 组合 |
| [封装](../../../../content/java/java-oop-io/encapsulation.md) | depth_pass / partial | 状态约束；行为优于机械 setter；先校验后修改；复制/快照；浅复制边界；final 非深冻结 | 实际业务权限/并发只说明边界 | 可变嵌套对象深复制取舍；并发状态维护；领域失败策略 |
| [接口](../../../../content/java/java-oop-io/interfaces.md) | depth_pass / partial | implements/extends；隐含 public/字段常量；default/static/private；冲突；函数式接口条件 | 冲突解决与 Lambda 仅解释 | 多接口 default 冲突编译练习；函数式接口适配；接口演化 |
| [枚举](../../../../content/java/java-oop-io/enums.md) | not_changed / partial | 常量；构造字段；values/valueOf；ordinal | 稳定业务编码与 ordinal 尚未区分 | 显式编码持久化；enum 方法覆写；EnumSet/EnumMap；valueOf 异常 |
| [Package](../../../../content/java/java-oop-io/packages.md) | not_changed / partial | package；import；全限定名；包名提取 | 练习仅字符串截取包名 | 目录/编译类路径；包级访问；static import；同名冲突；模块与包区别 |
| [NIO Files](../../../../content/java/java-oop-io/nio-files.md) | not_changed / partial | Path/Paths；文件名扩展名提取 | 标题 Files，实际没有 Files 操作 | Files.readString/writeString；exists/属性；walk 关闭；normalize/resolve；IO 边界 |
| [反射](../../../../content/java/java-collections-generics/reflection.md) | not_changed / partial | Class.forName；getSimpleName；getMethods | 无动态构造/调用示例 | getDeclared* 对照；Constructor/Method.invoke；异常包装；模块访问边界 |
| [数据结构](../../../../content/java/java-collections-generics/data-structures.md) | factual_correction / partial | Stack push/pop；Deque 队列；已纠正 Stack 整类弃用说法 | 结构取舍仍简略 | ArrayDeque 栈；空栈/队列契约；优先队列；复杂度；旧容器背景 |
| [集合框架](../../../../content/java/java-collections-generics/collections-framework.md) | depth_pass / partial | Collection 与 Map 分立；接口/实现；顺序/重复；TreeSet；可变/不可修改；快照/视图；比较契约 | 高级容器只定位用途 | Comparator 代码；Navigable/Sorted；集合批量操作；并发容器实践 |
| [ArrayList](../../../../content/java/java-collections-generics/arraylist.md) | depth_pass / partial | size/capacity；复杂度；索引；add/get/set；remove 重载；复制；真实访问模式选型 | 性能未做测量，线程安全仅边界 | subList 关联视图；批量操作；容量增长实现细节不作为契约 |
| [LinkedList](../../../../content/java/java-collections-generics/linkedlist.md) | depth_pass / partial | 双向链表；List/Deque；两端/索引成本；避免 get(i) 遍历；poll/peek 与 remove/get；null | ListIterator 已定位修改未演示 | ListIterator 修改；ArrayDeque 对照实测；集合视图 |
| [HashSet](../../../../content/java/java-collections-generics/hashset.md) | depth_pass / partial | 唯一性；add/remove 返回；哈希碰撞；equals/hashCode；null；顺序；可变键风险 | 自定义值对象示例在 Object 课 | 自定义键变更反例；容量/负载；批量集合代数操作 |
| [HashMap](../../../../content/java/java-collections-generics/hashmap.md) | depth_pass / partial | 键唯一值可重复；put 旧值；null/containsKey/getOrDefault；词频；视图；顺序；并发非原子边界 | entrySet 只解释未示范 | merge/compute；可变键反例；排序/插入序 Map 实例 |
| [Iterator](../../../../content/java/java-collections-generics/iterator.md) | depth_pass / partial | 游标消费；hasNext/next；异常；remove 次数/可选；增强 for 数组区别；fail-fast 不能当同步 | 并发容器仅边界提醒 | ListIterator 双向；forEachRemaining；不同一致性模型对照 |
| [Object 类](../../../../content/java/java-collections-generics/object-class.md) | depth_pass / partial | Object 与装箱；身份/值相等；equals 五条；hashCode；自定义不可变键；toString/getClass；clone/监视器边界 | clone/监视器仅定位，未教授完整协议 | 深/浅复制实例；wait/notify 需并发课；继承值相等策略 |
| [泛型](../../../../content/java/java-collections-generics/generics.md) | depth_pass / partial | 泛型类/方法；上界；类型安全限制；包装类型；不变性；extends/super；擦除/限制；重载冲突 | 复杂捕获/桥接只留边界 | 通配符捕获；交叉上界；堆污染与安全可变参数；桥接方法 |
| [序列化](../../../../content/java/java-network-concurrency/serialization.md) | not_changed / partial | Serializable；内存对象流写入/恢复；transient/UID 提示 | 代码练习仅文本模拟 Person 格式 | 不可信反序列化风险与过滤；对象图；UID 兼容；资源关闭；transient 非加密 |
| [网络编程](../../../../content/java/java-network-concurrency/networking.md) | not_changed / partial | URL 主机/路径；InetAddress loopback；Socket 名称 | 代码练习是 URL 本地解析，不是网络通信 mock | TCP/HTTP 真正协议流程；超时/关闭；编码；离线可验证本地通信设计 |
| [发送邮件](../../../../content/java/java-network-concurrency/sending-email.md) | not_changed / partial | 简化地址正则；字符串拆分；SMTP 角色提示 | 只验证简化格式，不代表邮件格式标准或可达性 | 邮件 API/依赖；身份验证/TLS；发件与收件模型；失败与重试 |
| [多线程](../../../../content/java/java-network-concurrency/multithreading.md) | not_changed / partial | Thread/Runnable；start/join；共享状态需要同步提示 | 原题串行求和不能证明并发正确 | 竞态实际例子；synchronized/Lock；可见性；中断；执行器；死锁 |
| [Applet 基础](../../../../content/java/java-network-concurrency/applet-basics.md) | not_changed / partial | 历史技术提示；模拟 init/start/stop/destroy | 固定模拟序列不等于实际回调保证 | 生命周期可多次 start/stop 的历史行为；JDK17 弃用移除标记；迁移方向 |
| [Java 8 新特性](../../../../content/java/java-modern-ecosystem/java8-features.md) | not_changed / partial | Lambda；Stream filter/sorted/mapToInt；方法引用 | Optional 仅列名；示例含 Java9 List.of | 函数式接口；Optional；惰性/终端；Collector；版本来源说明 |
| [Java 9 新特性](../../../../content/java/java-modern-ecosystem/java9-features.md) | not_changed / partial | List.of/Map.of；模块与私有接口方法名称 | 模块没有声明实例；不可修改与深不可变未区分 | module-info requires/exports；Set/Map 重复/null；Map.ofEntries；JShell |
| [MySQL 连接](../../../../content/java/java-modern-ecosystem/mysql-connect.md) | not_changed / partial | JDBC URL 前缀；SQL ? 字面占位说明 | 字符串检查没有真实 JDBC 与注入防护执行 | Connection/PreparedStatement/ResultSet；绑定参数；事务/资源；驱动与机密管理 |
| [常用类库](../../../../content/java/java-modern-ecosystem/libraries.md) | not_changed / partial | 库用途分类；依赖成本/许可证提示 | 只输出库名和 switch 分类 | 依赖管理；版本/来源验证；最小真实库调用；标准库替代判断 |
| [Java 实例](../../../../content/java/java-capstone/examples.md) | not_changed / partial | 数组偶数计数；文本命令解析 | 单次小题不能代替项目集成 | 组合类型/集合/异常小项目；输入契约；模块边界；可解释测试 |
| [Java 测验](../../../../content/java/java-capstone/quiz.md) | not_changed / partial | T/F 数量统计；题目序号展示 | 代码题偏计数，不能代表全部 Java 能力 | 多主题迁移题；编译错误分析；解释型问题；实践能力分层评估 |
