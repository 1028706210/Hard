# C++ 定向事实修正记录（2026-10-21）

独立只读复核后，总控授权落实本记录列出的最小正文修正。实际涉及 15 篇 Markdown，以及 `cpp/expand.py` 中动态内存、异常两处新增段的同步文本。课时 frontmatter（包括 objectives）、课程配置、题目 JSON、参考解和测试合同保持本轮修正前状态。

## 修正与核对来源

| 正文 | 最小修正 | 官方或原始技术来源 |
| --- | --- | --- |
| cpp-advanced/dynamic-memory.md | 借用指针有效性取决于对象是否存活；再次移动所有权不使对象地址失效，release 不删除对象。同步 expand.py 对应段落。 | [unique_ptr release/reset 条款](https://eel.is/c++draft/unique.ptr.single.modifiers) |
| cpp-algorithms-concurrency/future.md | promise 重复设置已就绪结果抛 future_error，错误条件 promise_already_satisfied；删除“未定义行为”误述。 | [promise 条款](https://eel.is/c++draft/futures.promise) |
| cpp-capstone/examples.md | min/max_element 可接受合法空区间并返回 last；解引用尾后迭代器才越界。 | [最值算法条款](https://eel.is/c++draft/alg.min.max) |
| cpp-foundations/operators.md | 分清无符号模运算与有符号溢出 UB。 | [算术表达式边界](https://eel.is/c++draft/expr.pre)、[整数类型](https://eel.is/c++draft/basic.fundamental) |
| cpp-stl-containers/import.md | math.h 是标准支持的 C 兼容头；强调 cmath 的 std 声明保证，保留优先用 cmath 的建议。 | [C 兼容头条款](https://eel.is/c++draft/support.c.headers.general) |
| cpp-foundations/modifiers.md | 不允许任意拼接 short/long/char；signed/unsigned 比较根据等级与范围决定共同类型，不总是转 unsigned。 | [类型说明符组合](https://eel.is/c++draft/dcl.type)、[通常算术转换](https://eel.is/c++draft/expr.arith.conv) |
| cpp-algorithms-concurrency/atomic.md | 正文补充 atomic 不对所有类型/平台保证无锁；is_lock_free/is_always_lock_free 查询。按授权保留原 objective，正文明确其“无锁”说法不能作为实现保证。 | [原子操作无锁属性](https://eel.is/c++draft/atomics.lockfree) |
| cpp-algorithms-concurrency/mutex.md | 数据竞争加入冲突内存位置、非原子与 happens-before 条件；删去 unique_lock 必然更慢的暗示，收窄死锁描述。 | [数据竞争](https://eel.is/c++draft/intro.races) |
| cpp-advanced/threads.md | joinable 前提更明确；数据竞争不再等同任何“无锁读写同一对象”。 | [数据竞争](https://eel.is/c++draft/intro.races) |
| cpp-algorithms-concurrency/condition-variable.md | 用同一互斥量保护谓词；通知可在持锁或解锁后执行，同一锁内先通知再更新不自动错误。保留既有先更新再通知范式。 | [condition_variable wait/notify](https://eel.is/c++draft/thread.condition.condvar) |
| cpp-advanced/exceptions.md | 明确新增 parse_all 整串合同与旧题 stoi 前缀解析区别；旧题输入42x仍按42求两倍84。同步 expand.py 对应段落。 | 本课现有 exercise prompt/reference_solution；[string 数值转换](https://eel.is/c++draft/string.conversions) |
| cpp-stl-containers/bitset.md | 长字符串本身不因长于N而抛 invalid_argument；说明默认使用前N字符及非法字符/pos异常，题目长度边界仍需主动校验。 | [bitset 构造](https://eel.is/c++draft/bitset.cons) |
| cpp-capstone/random.md | random_device 播种不会把 mt19937 变为 CSPRNG；去掉 secure 变量名，说明 random_device 质量依赖实现、分布映射不保证跨标准库逐值一致。 | [Mersenne Twister](https://eel.is/c++draft/rand.eng.mers)、[random_device](https://eel.is/c++draft/rand.device)、[Microsoft 标准库 random 文档](https://learn.microsoft.com/en-us/cpp/standard-library/random?view=msvc-170) |
| cpp-capstone/cfloat.md | 不把固定epsilon当通用相等判据；大跨度量级通常需相对容差、接近零需绝对容差，并明确旧题固定阈值不变。 | [numeric_limits epsilon](https://eel.is/c++draft/numeric.limits.members)、[Boost 浮点比较说明](https://www.boost.org/doc/libs/latest/libs/multiprecision/doc/html/boost_multiprecision/tut/limits/functions.html) |
| cpp-algorithms-concurrency/chrono.md | 整数单位转换向零截断，-1500ms转seconds为-1；需要向下取整使用chrono::floor。 | [duration_cast/floor](https://eel.is/c++draft/time.duration.cast) |

来源在本次复核中通过联网读取核对。标准草案会继续演进；项目 CppRunner 在 `apps/api/src/hard_api/runners/cpp.py` 的 `_compile_arguments` 中显式使用 `-std=c++20`，本记录以该 C++20 执行基线为准。Boost 文档用于浮点比较策略说明，不新增该库依赖。

## 验证与边界

运行 `.venv/Scripts/python.exe tools/content/validate.py --language cpp --require-complete`，结果为 valid=true，1门课程、99课时、99份练习、错误0。首批11篇日志为同目录 `factual-corrections-validation.log`；加入额外4篇后的最终日志为 `factual-corrections-final-validation.log`，分开保留两个阶段的校验记录。

`factual-corrections-before.json` 保存修正前的 C++ 文件哈希与 frontmatter 文本哈希；`factual-corrections-integrity.json` 记录首批11篇的边界检查，`factual-corrections-final-integrity.json` 核对最终只有授权的15篇正文发生变化，99份frontmatter保持一致，课程与99份练习共100个文件哈希不变，expand.py中11篇追加段全部仍能在当前正文中找到。

按任务限制未编译，未运行 Runner、参考解、拒绝测试或浏览器套件；静态校验与哈希一致性不能替代运行验收。除random示例变量改名/注释澄清外，本次只修正文解释，不改变示例算法或既有题目语义。

## 总控续核补记

上述“99份frontmatter保持一致”与“保留原objective”描述的是事实修正子任务当时的授权和检查结果，原始 integrity 证据继续保留。最终汇总核查另获授权，仅将 atomic.md 的学习目标“无锁计数”改为“原子计数”，避免把原子接口误写成所有实现均无锁；因此最终状态有这一处明确记录的 objective 变化，不能把先前的 frontmatter 一致性结论外推到最终文件。最终摘要与全语言结构校验见审计根目录的 final-manifest.json 及 README.md；该续核仍未编译或重跑例子。
