# C# 逐章深度核对（2026-10-21）

42 个目录入口均已有对应课时。本轮对 13 个密集章节补充第一轮深度，并修正 2 篇事实表述。下面每行均为 partial：已有覆盖子项和明确剩余项同时存在，不声称任一整章已穷尽。状态依据正文语义核对，不依据课时数、练习数或字数。

| 课时 | 已覆盖子项 | 仍部分覆盖 | 明确剩余 |
| --- | --- | --- | --- |
| csharp-foundations-tutorial | 输入→处理→输出、顶级语句问候程序 | 空输入与空白/大小写练习建议 | 命令行运行步骤与编译/运行失败对照 |
| csharp-foundations-introduction | C#/.NET分工、静态类型、编译与执行区别 | 程序集到运行时的解释较简短 | CLR/IL/JIT关系与不同应用类型的具体比较 |
| csharp-foundations-environment | SDK/项目/源码、build/run分工、离线环境约定 | 仅概述固定运行模板 | 最小csproj结构、SDK与运行时版本诊断 |
| csharp-foundations-program-structure | 顶级入口、语句、代码块、顺序执行 | 变量生命周期仅提醒 | 传统Main完整结构、using/type声明顺序对照 |
| csharp-foundations-basic-syntax | 标识符大小写、字符/字符串、两类注释、分号 | 编译诊断仅实践建议 | 关键字与转义标识符、字面量与表达式/语句区别 |
| csharp-foundations-data-types | int/double/bool/string、var静态推断 | 范围与整数除法仅提醒 | decimal/float/char、数值范围、值/引用分类总览（后续类与结构体已展开） |
| csharp-foundations-conversion | 隐式int→double、显式转换概念、TryParse | 精度损失与截断只说明 | checked转换溢出、文化相关数值文本与Convert舍入区别 |
| csharp-foundations-variables | 声明/赋值、确定赋值、临时变量与元组交换 | 状态命名建议 | 局部变量与字段默认初始化的区别、多变量初始化顺序 |
| csharp-foundations-scope | 块作用域、内层可读外层变量 | 变量遮蔽只有提醒 | 字段this限定、局部名称冲突的编译反例 |
| csharp-foundations-constants | const与命名规则、decimal常量 | const与运行时只读仅简介 | const与readonly初始化对照、跨程序集常量内联风险 |
| csharp-foundations-operators | 算术优先级、比较、逻辑与/或短路 | 除零与整数除法仅提醒 | 位运算、移位、赋值与递增、checked溢出和短路副作用示例 |
| csharp-foundations-decisions | if/else if/else、条件为bool、嵌套条件表达式 | 边界与互斥建议 | switch语句/表达式、嵌套分支与模式匹配入门 |
| csharp-foundations-loops | for/while、累计、终止条件 | 有限循环错误提醒 | do/while、foreach、break/continue、嵌套循环与零次执行对照 |
| csharp-oop-encapsulation | private字段、public方法、TrySpend状态保护 | 访问修饰符仅private/public | internal/protected与程序集、返回可变对象造成的封装泄漏 |
| csharp-oop-methods | 参数返回、MaxOfThree、重载参数匹配 | 按值传参在classes章补充 | ref/out/in、可选/命名参数、params与递归终止条件 |
| csharp-oop-nullable | Nullable<T>与string?区别、HasValue/Value、??/??=、?.、默认值、null算术/比较、!仅抑制诊断 | 可空引用分析给出上下文但未做诊断练习 | 复杂流分析、外部API注解与泛型可空约束 |
| csharp-oop-arrays | 一维数组、默认元素、Length/合法索引、反向遍历 | 数组固定长度只文字解释 | 多维/交错数组、Array方法、数组引用与浅复制 |
| csharp-oop-strings | string不可变、Length/索引、序数/忽略大小写比较 | 区域规则与拼接成本有解释 | Split/Substring/Replace、插值与转义、UTF-16代码单元与Unicode字符区别 |
| csharp-oop-structs | 值复制、嵌套引用浅复制、class身份对比、装箱副本、default与构造边界 | readonly struct为设计建议 | 可变struct在集合/属性中修改的陷阱、ref readonly与ref struct |
| csharp-oop-enums | 显式底层值、默认编号、整数/名称转换、TryParse数字陷阱 | 安全解析建议未系统比较IsDefined | Flags组合与按位判断、合法零值及底层类型范围 |
| csharp-oop-classes | 对象/实例、构造/this委托、字段/方法、static区别、共享引用、按值传参/重绑定、readonly引用边界 | 构造校验原则有讲解但旧Book示例未实现校验 | 对象相等与身份比较、对象初始化顺序、资源生命周期 |
| csharp-oop-inheritance | 单继承/多接口、基类构造与base、private/protected/internal边界、sealed、virtual覆盖、构造期间虚调用风险 | 受保护成员只描述常用访问 | protected internal/private protected组合、设计可替换性的复杂反例 |
| csharp-oop-polymorphism | 运行期虚分派、静态重载区别、new隐藏完整对照、abstract基类/成员与具体实现、基类数组 | 重载未提供第二套重载分派例题 | 重载与虚分派同时发生的两阶段解析、协变返回 |
| csharp-oop-operator-overloading | 二元+声明、分量运算、至少一参数为所在类型、==/!=成对 | 相等合同只有成对规则 | Equals/GetHashCode一致性、转换运算符与支持/不支持的操作符清单 |
| csharp-oop-interfaces | 能力合同、多实现、隐式public实现、显式实现与接口视图、抽象类选型、接口无实例字段 | 现代默认/静态接口成员仅边界说明 | 默认实现冲突解析、静态抽象成员与泛型数学 |
| csharp-oop-namespaces | 全限定名、using、文件范围namespace、全局命名空间、程序集区别 | 名称解析练习与实际类型查找区别未展开 | using别名、using static、global using与名称冲突对照 |
| csharp-io-metadata-preprocessor-directives | #define文件内作用域、#if嵌套、#region、编译期/运行期区别、修正define应在using之前 | 嵌套裁剪以模拟练习为主 | #elif/#undef、#warning/#error、#line/#pragma与可空指令 |
| csharp-io-metadata-regular-expressions | 字符类、捕获、量词、Matches不重叠、Unicode数字、贪婪/懒惰、Regex.Escape | 格式与语义校验边界 | 锚点/整串校验、替换、匹配超时与回溯成本 |
| csharp-io-metadata-exception-handling | try/catch/finally、具体异常顺序、checked、TryParse优先、避免泄露堆栈 | 资源清理只文字提醒 | using/Dispose实作、自定义异常、throw保留堆栈、异常过滤 |
| csharp-io-metadata-file-io | 读写/追加、全量/惰性、换行、相对路径及可信本地运行边界 | using/Dispose只有建议 | Stream读写闭环、编码、目录与文件异常分类 |
| csharp-io-metadata-attributes | 自定义Attribute、AttributeUsage、属性参数、运行期读取、元数据与行为区别 | 多次应用与参数类型仅文字说明 | 标准特性的编译器消费、构造参数对比、Inherited与AllowMultiple实作 |
| csharp-io-metadata-reflection | typeof/GetType、BindingFlags、DeclaredOnly、属性访问器过滤、修正反射非唯一特性分析途径 | 仅检查本程序集元数据 | 特性数据免实例化读取、Invoke/创建实例的失败边界及裁剪兼容性 |
| csharp-language-features-properties | 自动/完整/计算属性、get/private set/init边界、value后备字段与递归陷阱、浅只读、源代码/二进制兼容区别 | 旧Account示例未完整校验输入但已有说明 | required/初始化合同、虚属性与接口属性的组合 |
| csharp-language-features-indexer | this[int]只读、二维读写/set value、字符串键及重载、越界合同、浅复制隔离 | 字符串索引器只有语法说明 | 多参数重载冲突、ref返回与接口索引器实现 |
| csharp-language-features-delegates | 委托声明绑定/调用、多播与管道输出对照、Func/Action、同步异常、null/不可变调用链 | 兼容返回类型仅提及 | 协变/逆变具体规则、实例目标生命周期与Task回调异常 |
| csharp-language-features-events | 发布/订阅、event封装、EventHandler参数、阈值、退订实例、同步异常、委托快照竞态边界 | 基类protected触发仅描述 | 自定义add/remove、接口事件与完整生命周期设计 |
| csharp-language-features-collections | List/Dictionary操作、保序词频、HashSet/Queue/Stack操作对照、Count/Capacity、比较规则、哈希键可变风险、枚举失效 | SortedDictionary与旧ArrayList/Hashtable仅选型说明 | 排序映射操作实作、只读包装与不可变集合区别、线程安全集合 |
| csharp-language-features-generics | 泛型类/方法、类型推断/约束、Default相等比较、运行期类型、装箱限定、List不变性、标准Stack复用 | 方差与常用约束只入门 | in/out方差声明、泛型约束组合与nullable/notnull、泛型静态字段 |
| csharp-language-features-anonymous-methods | delegate/lambda、FindAll立即新列表、ConvertAll、闭包变量捕获、for/foreach差异、static lambda | 表达式树只说明转换边界 | 捕获对象生命周期、异步lambda与表达式树执行限制 |
| csharp-capstone-unsafe-code | unsafe/指针/取址/解引用、fixed数组、地址生命周期、平台白名单边界 | 替代Span仅建议 | stackalloc/sizeof、固定缓冲区、指针运算溢出与互操作布局 |
| csharp-capstone-multithreading | Thread Start/Join、共享写入风险、独占结果槽、调度无关汇总 | lock/Interlocked只点名 | 锁与原子操作实例、取消/异常传播、任务与线程的区别 |
| csharp-capstone-language-quiz | 类型/错误/集合组合、两个线程独占局部结果并确定性合并 | 综合挑战只涵盖选定主线 | 不能替代42章全部子题的逐项验收；现代异步与更大应用设计不在此挑战 |
