# C# 正文深度第一轮（2026-10-21）

本轮核对了现有 42 篇课时正文与来源目录中的 42 个主要入口，修改 15 篇正文：其中 13 篇补充概念、对照示例与边界，2 篇修正事实表述。全部课时仍有明确后续子题，因此逐章矩阵将整章状态记录为 partial；每章已经覆盖的子项、部分覆盖的子项、明确剩余项分别列出。目录对应数与练习数不能推导出内容深度或全面完成。

变更只涉及 `content/csharp/**/*.md` 和本审计目录。原先未提交内容被作为本次基线读取并继续保留。`course.yaml` 与 42 份练习 JSON 对比本次修改前 SHA-256 完全一致；课时前置、ID、目标、XP、source_url/source_snapshot_date 和必要标题均未改动，已编辑 Markdown 的换行统一为 LF。没有更改共享概念映射、后端、前端、依赖、Git 状态或用户数据。

## 具体改进

| 正文 | 新增或纠正 |
| --- | --- |
| csharp-oop/classes.md | 对象身份、static 与实例、默认构造条件、this 构造委托、共享引用和普通按值传参、readonly 引用边界 |
| csharp-oop/structs.md | 字段复制与嵌套引用共享、readonly struct 选型、存储位置误区、default 构造边界、装箱副本 |
| csharp-oop/inheritance.md | 单继承与多接口、构造函数链、访问边界、sealed/base、构造期间调用虚方法的风险 |
| csharp-oop/polymorphism.md | override/new 的具体输出对照、abstract 类/方法、抽象与默认实现选型；修正原示例顶级语句顺序 |
| csharp-oop/interfaces.md | 隐式与显式实现、接口视图、接口/抽象类选择，纠正“所有实现都必须 public”的过度概括，明确现代接口边界 |
| csharp-oop/nullable.md | 缺失与 0/空串、提升算术和比较、?. 与 ??、可空编译上下文及 ! 的局限 |
| csharp-language-features/properties.md | get/private set/init、计算属性、set 递归错误、浅只读与字段/属性兼容区别 |
| csharp-language-features/indexer.md | 二维读写与 value、字符串键、异常合同与浅复制所有权 |
| csharp-language-features/delegates.md | 多播与管道输出差别、Action/Func、同步调用与异常传播；删除“委托本身自动异步”的误导 |
| csharp-language-features/events.md | 退订同一委托、订阅者生命周期、同步异常、基类触发与快照边界；纠正判空竞态表述 |
| csharp-language-features/generics.md | 类型约束、Default 相等、运行期保留类型、装箱限定、List 不变性与标准栈复用 |
| csharp-language-features/collections.md | List/Dictionary/HashSet/Queue/Stack 选择、排序集合与旧容器定位、容量/数量、键比较、可变哈希键及枚举失效 |
| csharp-language-features/anonymous-methods.md | 捕获变量、for/foreach 差别、static lambda、表达式树边界；修正 FindAll 原地过滤的误导 |
| csharp-io-metadata/preprocessor-directives.md | 修正 #define 必须位于 using 之前 |
| csharp-io-metadata/reflection.md | 修正反射并非特性分析唯一途径，区分 typeof(具体类型) 与 typeof(T) |

每个密集章节明确区分当前练习的有限目标与正文的更宽概念。没有修改参考解、隐藏测试或题目合同，也没有添加“通过一个练习就代表整章掌握”的声明。

## 核验结果与限制

- `.venv/Scripts/python.exe tools/content/validate.py --language csharp --require-complete`：通过，1 门课程、42 课时、42 份练习、错误 0。结果保存在 `validate.log`。
- 17 个新增小例由本机已安装 .NET SDK 10.0.100 的 Roslyn 编译，再用本机 .NET 10 执行：17/17 编译退出 0、运行退出 0、实际输出与预期逐行一致。`example-results.json` 保留每例结果，`examples/` 保留原始源码、编译响应文件及二进制。委托与事件示例附加了本课已有的类型声明作为上下文。所有编译均有 CS2023 提示：noconfig 被放在响应文件中而被忽略；没有编译错误，编译引用均显式来自本机离线引用包。
- `build-audit.py`：确认 42 行逐章语义矩阵、6 条共享映射建议，以及 43 份课程/练习文件哈希一致。
- 初次用 toolchain-lock 中的基础 Python 运行校验遇到缺少 yaml；随即改用项目已有 .venv，未安装或更改环境。
- 小例执行只证明这些例子的编译与输出；本轮没有执行全套 Runner、所有参考解/拒绝测试、浏览器验收或重型 report.py。上述验收由总控统一安排。
- 仍欠缺的基础章节深度（如 switch/do-while、数值转换/溢出、数组多维/交错形式、方法参数修饰符、字符串常用 API）、反射/IO/线程等后续内容已在矩阵逐章列出。

## 资料与产物

目录对照仅使用 [Runoob C# 教程自身的主目录](https://www.runoob.com/csharp/csharp-tutorial.html)，其内容未作为当前 C# 技术事实的权威。正文均为本项目原创中文说明和小型自建例子。

技术事实在 2026-10-21 通过浏览器读取以下官方文档核对，修改课时末尾也保留相应链接。原 source_url 仍标识目录来源，未替换历史溯源字段。

- [Microsoft Learn 类型系统](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/)、[参数与按值传递](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/method-parameters)、[结构体](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/struct)
- [继承](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/object-oriented/inheritance)、[多态](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/object-oriented/polymorphism)、[abstract](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/abstract)、[接口](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/interfaces)
- [可空值类型](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/nullable-value-types)、[可空引用](https://learn.microsoft.com/en-us/dotnet/csharp/nullable-references)、[属性](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/properties)、[索引器](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/indexers/)
- [委托](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/delegates/)、[事件](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/events/)、[泛型](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/generics)、[集合选型](https://learn.microsoft.com/en-us/dotnet/standard/collections/selecting-a-collection-class)、[lambda](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/lambda-expressions)
- [预处理器](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/preprocessor-directives)、[反射](https://learn.microsoft.com/en-us/dotnet/fundamentals/reflection/overview)

`coverage-matrix.md/json` 是完整路线子题核对；`mapping-suggestions.json` 是交给总控的建议，尚未修改共享映射；`baseline-sha256.json` 是本轮起点；`changed-files.json` 与 `integrity.json` 记录文件边界。`enrich.py` 为一次性、有重复执行保护的正文写入记录，不应再次运行覆盖本轮基线；`build-audit.py` 只生成本目录审计文件。
