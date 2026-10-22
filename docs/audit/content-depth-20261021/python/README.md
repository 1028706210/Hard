# Python 教学深度首轮修订

日期：2026-10-21。范围为 `content/python/**` 和本目录。审查本地全部 84 篇课文，实际扩充 14 篇核心课文；课程数量、稳定 ID、前置关系、难度、积分与原始来源信息保持不变。84 份练习和 `course.yaml` 的 SHA-256 均与本轮开始时相同，没有改动答案、测试或输入输出契约。

这是首轮深度修订，未判定 84 课在语义上完整。完整的本地复核与后续缺口见 [coverage.md](coverage.md) 和 [coverage.json](coverage.json)。来源主题清单是复核维度，不是对 84 个外部章节逐段比对的结果。

## 实际改动

| 文件 | 新增教学内容 |
| --- | --- |
| `python-modules-io-oop/classes.md` | 实例/类属性、绑定方法、初始化边界、继承/重写、多态、`super()`、多继承/MRO、名称改写、特殊方法与 `NotImplemented` |
| `python-functions-iteration/functions.md` | 位置/关键字参数、默认值、`/` 与 `*`、实参展开、可变默认值、对象传递、返回元组与递归边界 |
| `python-functions-iteration/scope.md` | LEGB、闭包、未绑定局部变量、`global/nonlocal`、块/类/推导式作用域边界 |
| `python-functions-iteration/decorators.md` | 装饰时机、参数与返回值转发、`wraps`、带配置工厂、叠加次序、副作用与异步限制 |
| `python-functions-iteration/iterators.md` | `iter/next`、迭代协议、自定义迭代器、耗尽、生成器恢复顺序、表达式与内存边界 |
| `python-core-types/data-types.md` | 内建类型表、`None`、真假、`bool` 子类、类型判断、引用、相等/身份、可变性 |
| `python-core-types/conversion.md` | 数值截断与文本解析、基数、异常、非有限值、容器转换、真假与文本/字节编码 |
| `python-flow-collections/lists.md` | 切片更新、增删方法、排序、返回值、浅复制、嵌套共享与遍历修改风险 |
| `python-flow-collections/tuples.md` | 逗号语义、解包、重绑定、嵌套可变与可哈希条件 |
| `python-flow-collections/dictionaries.md` | 键约束、更新删除、顺序、动态视图、遍历、计数、缺失值与浅复制 |
| `python-flow-collections/sets.md` | 交并差、子集、修改方法、哈希、`frozenset`、相等去重与顺序边界 |
| `python-flow-collections/data-structures.md` | 容器选择表、栈/队列、`deque`、组合记录、`enumerate/zip` 与重复键 |
| `python-modules-io-oop/exceptions.md` | 异常传播、处理器顺序、`else/finally`、自定义异常、原因链和清理/断言边界 |
| `python-modules-io-oop/files.md` | 文件模式、编码、文本/字节、临时文件、行读取、游标、异常、缓冲和持久化限制 |

以上路径均相对 `content/python/`。保留原有示例与练习说明，新增示例使用原创中文解释并列明预期输出；对每课明确区分扩展教学内容与较窄的现有自动练习范围。面向对象追加已有有效概念标签；数据结构课追加 `data-structures` 标签。

## 验证证据及限度

- [before.json](before.json)：本轮开始时 169 个 Python 文件的摘要，以及 84 课原始 front matter，记录本轮起点；未修改文件可直接按摘要核对。
- [verification.json](verification.json)：14 课的 34 个新增示例逐个在独立 Python 3.13.13 进程和临时目录执行，退出码、标准输出及标准错误均符合预期；85 个非课文文件摘要一致，受保护元数据未变。通过 `.venv/Scripts/python.exe -X utf8 docs/audit/content-depth-20261021/python/verify_examples.py` 可重复核对。
- [validation.json](validation.json)：执行 `tools/content/validate.py --language python --require-complete`，退出码 0，1 门课程、84 课、84 份练习，错误数组为空。这是内容结构检查，不是教学语义全覆盖认证。
- [mapping-suggestions.json](mapping-suggestions.json)：6 个共享映射建议，附各自已独立运行通过的代码和预期输出。没有修改共享 `concepts.yaml`。建议更新继承、多态、封装、方法、运算符重载，以及原先指向 MongoDB 的数据结构映射。
- [example-extraction-failure.json](example-extraction-failure.json)：保留首次临时提取脚本跨越 Markdown 围栏导致的失败记录。它把正文误当成代码，属于提取器错误；最终 verifier 先识别围栏再配对，34 例全部通过。此文件不代表课程示例存在语法错误。

本轮未执行 `report.py`、Runner、全量参考解、浏览器或端到端验收；总控统一安排这些执行。文件示例仅在新建临时目录运行，没有操作用户文件。已执行示例的解释器为 3.13.13；技术参考选用 Python 3.14 官方文档，新增示例未依赖 3.14 专属语法。

## 技术来源与剩余重点

新增解释核对了 [Python 类教程](https://docs.python.org/3.14/tutorial/classes.html)、[函数与参数](https://docs.python.org/3.14/tutorial/controlflow.html)、[数据结构](https://docs.python.org/3.14/tutorial/datastructures.html)、[异常](https://docs.python.org/3.14/tutorial/errors.html)、[文件读写](https://docs.python.org/3.14/tutorial/inputoutput.html)、[内建函数](https://docs.python.org/3.14/library/functions.html)、[内建类型](https://docs.python.org/3.14/library/stdtypes.html)、[数据模型](https://docs.python.org/3.14/reference/datamodel.html)、[函数定义语义](https://docs.python.org/3.14/reference/compound_stmts.html#function-definitions)、[wraps](https://docs.python.org/3.14/library/functools.html#functools.wraps)、[deque](https://docs.python.org/3.14/library/collections.html#collections.deque)、[内建异常](https://docs.python.org/3.14/library/exceptions.html) 和 [流接口](https://docs.python.org/3.14/library/io.html)。原菜鸟来源 URL 与快照日期继续保留，未把它们改称本轮官方技术核对时间。

后续优先补足循环的 `break/continue/else`、逻辑/位运算、数值精度、模块/包、真正的上下文协议及容器类型注解。第三方、数据库、网络、部署和 GUI 章节虽然已有受控练习，正文对真实 API 与生命周期仍明显不足；需要在保留安全练习边界的同时补教学，而不是据 fixture 通过宣称真实集成完成。面向对象仍缺 `property`、描述器、反向运算等进阶展开；本轮没有因此建议将属性或索引器映射标为可用。
