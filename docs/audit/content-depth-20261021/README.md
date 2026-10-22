# Hard 内容深度首轮汇总核查（2026-10-21）

当前四语言共 282 课时、282 份练习。最终全语言结构校验通过，错误 0；本轮内容工作涉及 76 篇不同课文，并保留 101 个新增课文示例的执行结果。**282 课目前均保留逐章待补项，未据此认定任一整章或全路线在语义上完整。** 本文是内容审计汇总，前端、后端全套测试和浏览器验收应以总控的独立证据为准。

最终格式续核：清理 concepts.yaml 中 11 行空白行的尾随空格，解析后的 YAML 数据逐值相同；再次执行全语言结构校验，仍为 4/282/282、错误 0。续核输出保存在 final-format-validation.stdout.json 与 final-format-validation.stderr.txt，最终清单同步记录当前哈希，原始示例执行日志保持不变。

## 改动范围与契约

| 语言 | 总课时 | 本轮不同课文变更 | 课程配置与练习哈希未变文件数 | 当前正文字符数 |
| --- | ---: | ---: | ---: | ---: |
| Python | 84 | 14 | 85 | 67,673 |
| Java | 57 | 23 | 58 | 75,235 |
| C# | 42 | 15 | 43 | 45,070 |
| C++ | 99 | 24 | 100 | 69,111 |
| 合计 | 282 | 76 | 286 | 257,089 |

字符数采用 Unicode 码点计数：排除 YAML frontmatter 和换行符，包含 Markdown 标记、空格、标点及代码。逐课计数与当前 SHA-256 见 [final-manifest.json](final-manifest.json)。该数字只用于追踪版本和篇幅，不是教学质量或覆盖率指标。

Python 的 14 课为重点深化；Java 的 23 课为 20 课深化加 3 课事实修正；C# 的 15 课为 13 课深化加 2 课事实修正；C++ 的 24 课是 11 课扩充与 15 课事实修正的并集，动态内存、异常两课重叠，不能相加成 26 课。C++ 最终另把 atomic 的学习目标由“无锁计数”改为“原子计数”，仍在上述 24 课中。

本次从各语言本轮起点摘要重新比对，四份 course.yaml 与 282 份练习 JSON 共 286 文件的 SHA-256 一致，既有题目、参考解及测试合同保持该基线。Python、Java、C# 的基线记录分别为 [before.json](python/before.json)、[baseline.json](java/baseline.json)、[baseline-sha256.json](csharp/baseline-sha256.json)。C++ 的 [factual-corrections-before.json](cpp/sources/factual-corrections-before.json) 在最初 11 课扩充后采集，因此本汇总用扩充记录与其后的事实修正摘要联合计数，未把它误称为全部内容工作开始前的快照。这些起点均包含各代理开始前已有的未提交工作。

元数据有明确例外：Python 两课补充 concepts 标签，Java 四课的标签由总控与共享映射同步；C++ 最初扩充已把 vector 的倍增目标改为按需扩容，最终续核又修正 atomic 的一个 objective。其余保留要求分别见各语言证据，不能把历史子任务“frontmatter 一致”结论外推到所有最终文件。

## 本次实际验证

执行 `.venv/Scripts/python.exe tools/content/validate.py --require-complete`，省略 `--language` 即检查全部四语言。退出码为 0，结果为 valid=true、4 courses、282 lessons、282 exercises、errors=[]。该命令检查目录/来源映射、内容结构、关联与静态合同；`--require-complete` 不是逐章知识完整性的认证。

原始输出与命令证据分别见 [final-validation-all.stdout.txt](final-validation-all.stdout.txt)、[final-validation-all.stderr.txt](final-validation-all.stderr.txt)、[final-validation-all.json](final-validation-all.json)。本次最终核查没有重跑旧例子、编译全量课程或覆盖先前日志。

| 保留的示例执行证据 | 数量与记录 | 能证明的范围 |
| --- | --- | --- |
| Python 新增课文示例 | [verification.json](python/verification.json)，34/34 | 独立 Python 3.13.13 进程的退出码、stdout/stderr；当前 14 课摘要仍匹配该记录 |
| Java 新增课文示例 | [example-run-001/results.json](java/example-run-001/results.json)，38/38；[example-run-002/results.json](java/example-run-002/results.json)，1/1 | JDK 17 编译与程序输出；本次只读核对 39 份代码 SHA、保存程序与当前正文一致 |
| C# 新增小例 | [example-results.json](csharp/example-results.json)，17/17 | 已安装 .NET 10/Roslyn 编译与运行输出；保留源码和响应文件，本次核对其可从当前课文重建 |
| C++ 新增例子 | [example-results.json](cpp/example-results.json)，11/11 | 这 11 个独立程序的 CppRunner 执行结果；保存源码目前仍在对应课文中 |
| Python 共享映射片段 | [mapping-suggestions.json](python/mapping-suggestions.json)，6 个 example_check=pass | 另计的短片段记录；本次核对当前映射代码一致，不纳入 101 个课文例子 |

C# 的 17 次编译均记录 CS2023 警告：响应文件中的 noconfig 被忽略；没有编译错误，不能把有警告写成无警告。C#、C++ 旧运行结果没有完整记录当时源码哈希，本次生成的摘要固定当前源文件状态，并用保存程序与正文的只读比对连接两者，未倒填为当时已有的证据。Java 清单最初的 prepared_not_run 是提取阶段状态，实际执行以两次 results.json 为准；后来四处 concepts 标签改变了课文全文摘要，39 份示例代码 SHA 仍匹配。

Javadoc 课中的 1 个 Java 程序已编译运行；**未执行 javadoc 文档生成，也未审阅生成的 HTML 页面**。101 个示例通过不覆盖全部练习、拒绝测试、外部 API、数据库、GUI 或端到端流程。Python 的原始 [example-extraction-failure.json](python/example-extraction-failure.json) 保留首次提取器跨围栏错误，最终 34 例证据独立保存；未抹去失败记录。

## 共享概念整合

当前 [content/concepts.yaml](../../../content/concepts.yaml) 包含 45 个概念、180 个语言槽，111 available、69 missing。依据 [mapping-integration.json](mapping-integration.json) 整合 17 个经审查的映射槽（Python 6、Java 6、C# 5），并同步 Java 四处课时标签。C# references 建议未采用，因为普通对象引用并不等于当前对照中的 C++ 别名引用。

与 [concepts-before.yaml](concepts-before.yaml) 直接比较，实际共有 23 个 compare 槽变化：除上述 17 槽，还有既有说明的 6 处措辞修正，涉及 variables/C#、types/C#、control-flow/Python、control-flow/C#、functions/C++、references/C++。available 表示已存在对应教学和对照内容，不代表整个概念已教完，也不代表所有语言片段都作为独立程序运行过。各语言旧 README 中“共享映射尚未改动”描述其交付当时边界，整合后状态以本节和最终清单为准。

## 逐章覆盖与当前补记

完整矩阵保留在 [Python coverage.md/json](python/coverage.md)、[Java coverage-matrix.md/json](java/coverage-matrix.md)、[C# coverage-matrix.md/json](csharp/coverage-matrix.md)、[C++ coverage.md/json](cpp/coverage.md)。这些是逐篇本地正文审阅与子题缺口记录，没有把来源主目录对应数推导成外部原文逐段覆盖。四语言 282 行均仍为 partial 或等义的首轮/本地部分覆盖状态。

C++ 原矩阵保存其生成时的快照；operators、bitset、atomic 三课随后发生事实或目标修正，因此其 observed_sha256 与最终文件不同。原矩阵不覆盖写入，当前事实与仍待补内容如下，最终清单也保留这三条旧/新摘要和补记：

| 课文 | 最终正文已经覆盖 | 仍待完善 |
| --- | --- | --- |
| [operators.md](../../../content/cpp/cpp-foundations/operators.md) | 已区分实际运算类型为无符号时的模运算、有符号溢出的未定义行为，并提醒较窄整数可能先提升；保留除零与短路说明。 | 仍需提升前后类型的独立对照、最小有符号值除以 -1、移位等边界和失败路径示例。 |
| [bitset.md](../../../content/cpp/cpp-stl-containers/bitset.md) | 已说明默认最多用前 N 字符，长于 N 不自动报错；用 101011 构造 bitset<4> 得 1010，区分非法字符与起始位置异常及题目自定长度限制。 | 仍需 test/set、to_ulong 范围异常、代理引用和更多输入边界的可运行对照；本轮未新增相关运行验收。 |
| [atomic.md](../../../content/cpp/cpp-algorithms-concurrency/atomic.md) | 已说明 std::atomic 不保证所有类型和实现无锁，可查询 is_lock_free/is_always_lock_free；最终学习目标改为原子计数。 | 仍需 CAS 失败更新 expected、弱 CAS 重试、发布/获取与 relaxed 内存序的适用条件、计数溢出和复合状态示例。 |

项目 [CppRunner](../../../apps/api/src/hard_api/runners/cpp.py) 的 `_compile_arguments` 明确使用 `-std=c++20`；事实修正记录中把项目称为 C++17 的表述已纠正为 C++20。事实修正子任务当时按授权保留 objective、未编译的历史边界仍在 [factual-corrections.md](cpp/sources/factual-corrections.md) 保留，最终 atomic 目标改动另加续核说明，不修改旧 integrity 结论或伪造其时间顺序。

后续内容工作仍须按矩阵推进：

- Python：循环 else、参数与数值边界、模块/包、上下文协议、类型注解，以及第三方/数据库/网络/部署/GUI 的真实 API 与生命周期。
- Java：Javadoc 生成与页面审阅、方法按值传递、数组/字符串/IO、反射、线程同步与中断、离线网络、JDBC 资源/事务/参数绑定、版本边界。
- C#：基础控制流、数值转换与溢出、多维/交错数组、方法参数修饰符、字符串 API，以及反射/IO/线程的失败路径与完整例子。
- C++：所有权与生命周期的异常路径、文件状态、迭代器/比较器/区间前提、并发取消与内存模型、数值范围/误差和跨实现保证；OpenCV 仍为 API 识别与本地矩阵模拟。

## 清单与使用能力

[final-manifest.json](final-manifest.json) 保存全部 content 文件与本审计目录产物的最新 SHA-256、282 篇课文的字符数、各语言基线比对、旧执行证据的读取核对结果和本次结构校验命令。清单不把自身纳入摘要，避免自引用；摘要只证明这些字节的版本，不证明教学或运行正确性。

本轮最终核查实际使用本地文件读取/最小写入、项目内容校验器、SHA-256、JSON/YAML 与只读源码比对，并按“先验证后结论”流程输出报告；没有启服务、安装依赖、执行发布或更改 Git 暂存/提交。官方资料的技术核对继承各语言已保存的来源记录，本次汇总未重新联网核验所有外部章节。
