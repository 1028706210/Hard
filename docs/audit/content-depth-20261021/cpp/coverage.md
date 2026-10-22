# C++ 全路线教学深度矩阵

日期：2026-10-21。按 `content/cpp/course.yaml` 顺序逐篇阅读当前本地全部 **99 课**，记录正文实际出现的内容与后续缺口。每行状态均为 **partial**；“本轮扩充”由只读解析 `expand.py` 的 `LESSONS` 得到，共 **11 课**。本审计子任务只写本矩阵及 JSON，没有扩充或改写课程。

“已讲”表示正文存在说明或示例，不表示习题已验证全部知识，也不表示该章语义完整。未用篇幅、代码块数、主目录对齐或静态校验作为完整性证据。来源 URL 保留在 JSON，矩阵是逐章本地正文核对，未声称本轮逐段核验全部外部来源。

“剩余”同时记录缺失教学深度与需要进一步准确区分的事实/边界；另有任务正在做少量事实修订，因此个别措辞可能在阅读后更新。JSON 保存本次生成时的文件摘要，便于后续复核。这些主题即使已有一句提醒，也不等于有完整例子、失败路径和对应评估。

文件重点仍缺模式/状态/关闭失败/二进制与游标；并发重点仍缺生命周期异常、取消、共享状态契约和内存模型；算法重点仍缺迭代器类别/比较器/区间前置条件与删除算法；数值重点仍缺类型范围、溢出、相对误差和跨实现保证；OpenCV 仍是 API 识别加本地矩阵模拟，不能视为真实库集成。

本矩阵任务未编译、运行 Runner、执行重套件或验证第三方服务。其余任务的运行证据应分别引用，不能由本表推导。

| 顺序 / 课程 | 本轮正文扩充 | 状态 | 正文实际已讲 | 剩余深度与边界 |
| --- | --- | --- | --- | --- |
| 1. [C++ 教程总览](../../../../content/cpp/cpp-foundations/tutorial.md) | 否 | partial | 静态类型/编译执行、多范式、模块学习顺序、标准输入输出练习约定 | 缺一条含编译命令与诊断结果的完整学习闭环；尚未建立按标准版本查证语言规则的示例 |
| 2. [C++ 简介](../../../../content/cpp/cpp-foundations/introduction.md) | 否 | partial | 语言背景与用途、main/include/cout、return 0、头文件和分号错误 | 生命周期/值语义等语言特性只有概览；需区分教学入口简化描述与初始化过程 |
| 3. [C++ 环境设置](../../../../content/cpp/cpp-foundations/environment.md) | 否 | partial | 编译/链接职责、GCC/Clang/MSVC、g++版本与C++20选项 | 实际编译和运行命令、警告/错误定位、多源文件链接、平台工具链差异未展开 |
| 4. [C++ 基本语法](../../../../content/cpp/cpp-foundations/basic-syntax.md) | 否 | partial | 声明、字面量、字符与字符串、语句分号、main返回值 | 标识符规则的版本/字符范围、表达式与声明的区别、头文件齐全的独立程序与编译诊断 |
| 5. [C++ 注释](../../../../content/cpp/cpp-foundations/comments.md) | 否 | partial | 行/块注释、不能嵌套、说明原因、过时注释、条件编译屏蔽 | 注释与字符串边界的具体例子；词法空白效应与文档注释工具未展开 |
| 6. [C++ 数据类型](../../../../content/cpp/cpp-foundations/data-types.md) | 否 | partial | 基本类型、sizeof(char)、整除/取余、宽度和浮点误差提醒 | 实现最小范围、numeric_limits、转换/提升、负数与零除/最小值除-1边界缺具体例子 |
| 7. [C++ 变量类型](../../../../content/cpp/cpp-foundations/variables.md) | 否 | partial | 带类型声明、初始化、auto推导、未初始化读取风险 | 声明和定义、列表初始化与窄化、对象初始化分类；不同存储期的初始化区别 |
| 8. [C++ 变量作用域](../../../../content/cpp/cpp-foundations/scope.md) | 否 | partial | 块/全局作用域、嵌套遮蔽、局部名称与减少全局状态 | 作用域与存储期/生存期区别，静态局部/命名空间/声明点与多文件可见性未展开 |
| 9. [C++ 常量与字面量](../../../../content/cpp/cpp-foundations/constants.md) | 否 | partial | const/constexpr、字面量、宏与类型检查、LL后缀 | 字面量类型选取不能仅按int概括；运行时const、常量表达式约束和字符转义缺细例 |
| 10. [C++ 类型修饰符](../../../../content/cpp/cpp-foundations/modifiers.md) | 否 | partial | signed/unsigned/short/long、负数转无符号、size_t混合比较 | 各种合法修饰组合、平台宽度、整数转换秩与例外、可移植边界检查未完整讲解 |
| 11. [C++ 存储类](../../../../content/cpp/cpp-foundations/storage-classes.md) | 否 | partial | static跨调用、auto、extern、引用推导提醒、共享状态同步提醒 | 静态局部初始化时机、存储期与链接性、thread_local、多文件声明定义和并发初始化/更新区别 |
| 12. [C++ 运算符](../../../../content/cpp/cpp-foundations/operators.md) | 否 | partial | 运算分类、优先级、括号、除零风险、逻辑短路 | 有符号/无符号溢出的独立边界示例、位移/位运算、序列与副作用、常规算术转换 |
| 13. [C++ 循环](../../../../content/cpp/cpp-foundations/loops.md) | 否 | partial | for/while、do-while定义、累计、包含端点、整数宽度 | do-while独立例子、break/continue、范围for与嵌套循环；更新溢出和终止条件证明 |
| 14. [C++ 判断](../../../../content/cpp/cpp-foundations/decisions.md) | 否 | partial | if/else-if/else、条件表达式概述、switch/case/default/break、符号分类 | 条件表达式类型、显式fallthrough、switch允许类型/初始化、分支组合边界例子 |
| 15. [C++ 函数](../../../../content/cpp/cpp-core-memory/functions.md) | 否 | partial | 声明定义、返回值、按值/引用/指针、void、悬垂返回提醒 | 默认参数、重载决议、递归停止条件、签名/链接与const参数规则未展开 |
| 16. [C++ 数字](../../../../content/cpp/cpp-core-memory/numbers.md) | 否 | partial | 整数/浮点、abs/pow、显式浮点除法、误差与范围提醒 | INT_MIN的abs、乘法前提升与结果溢出、绝对/相对误差、NaN/Inf和整数精确范围 |
| 17. [C++ 数组](../../../../content/cpp/cpp-core-memory/arrays.md) | 否 | partial | 固定长度、连续存储、下标、范围遍历、越界、参数退化 | 部分初始化、多维数组、引用保留长度、span与array选择；sizeof在退化参数上的反例 |
| 18. [C++ 字符串](../../../../content/cpp/cpp-core-memory/strings.md) | 否 | partial | string与C字符串、拼接/长度、getline、反转、c_str、下标风险 | 字节/字符/Unicode区别、at/空串、c_str失效、混读换行处理及内嵌NUL |
| 19. [C++ 指针](../../../../content/cpp/cpp-core-memory/pointers.md) | 是 | partial | 地址/解引用/交换、const指针、nullptr、借用/拥有、尾后/悬垂/失效 | 完整数组遍历和多级指针例子、函数指针、自定义接口有效性契约；不可据非空判安全 |
| 20. [C++ 引用](../../../../content/cpp/cpp-core-memory/references.md) | 是 | partial | 别名不改绑、T&/const T&、复制/引用推导、临时延寿限制、右值引用/移动概述 | 临时对象和返回引用的对照例子、引用折叠/转发、视图和容器失效的组合案例 |
| 21. [C++ 日期 & 时间](../../../../content/cpp/cpp-core-memory/date-time.md) | 否 | partial | chrono时长、秒到时分秒、duration_cast/count、时钟用途提醒 | 不同表示类型的隐式转换条件、负时长截断、溢出、日历/时区与系统时间未展开 |
| 22. [C++ 基本的输入输出](../../../../content/cpp/cpp-core-memory/input-output.md) | 否 | partial | cin/cout、空白提取、setw、失败态检查 | getline混读修复、eof/fail/bad区别、clear/ignore恢复、输出失败和状态保持 |
| 23. [C++ 结构体](../../../../content/cpp/cpp-core-memory/struct.md) | 否 | partial | 相关字段聚合、成员访问、聚合初始化、复制、const引用传参 | 默认成员初始化、struct/class默认继承方式、嵌套结构与聚合限制；坐标差溢出边界 |
| 24. [C++ vector 容器](../../../../content/cpp/cpp-core-memory/vector.md) | 是 | partial | 连续动态序列、size/at、reserve/resize/capacity、摊还追加、重分配失效 | 较复杂元素的复制/移动与异常保证、最大长度/分配失败；现有练习不覆盖全部失效规则 |
| 25. [C++ 数据结构](../../../../content/cpp/cpp-core-memory/data-structures.md) | 否 | partial | 栈/队列/链表概览、vector栈、空栈检查、按访问方式选容器 | 队列/链表独立实例、位置查找成本和失效、图树等结构；操作指令错误处理未系统讲解 |
| 26. [C++ 类 & 对象](../../../../content/cpp/cpp-oop/classes.md) | 是 | partial | 访问控制、构造初始化顺序、explicit、const边界、复制值语义、Rule of Zero、受控状态 | 复制/移动特殊成员、委托/默认构造、static成员、友元和完整资源类案例未展开 |
| 27. [C++ 继承](../../../../content/cpp/cpp-oop/inheritance.md) | 是 | partial | public/protected、构造链、默认继承方式、隐藏与virtual/override对照、析构顺序 | 多继承/菱形只提醒，虚继承、访问转换、using解除隐藏与可替代性契约缺例子 |
| 28. [C++ 重载运算符和重载函数](../../../../content/cpp/cpp-oop/overloading.md) | 否 | partial | 函数按参数重载、成员运算符、非成员/对称性、短路语义提醒 | 完整函数重载集合和歧义例子、隐式转换、前/后置运算符、等价比较/输出运算符设计 |
| 29. [C++ 多态](../../../../content/cpp/cpp-oop/polymorphism.md) | 是 | partial | virtual/override、基类指针引用、虚析构、切片、unique_ptr拥有、构造析构分派、final | 多态容器完整例子、克隆/复制契约、访问控制/默认参数与虚调用、动态类型检查未展开 |
| 30. [C++ 数据抽象](../../../../content/cpp/cpp-oop/abstraction.md) | 否 | partial | 公开能力/隐藏实现、纯虚Sequencer、替换实现、不可实例化 | 接口语义与错误契约、可复制完整调用例子；状态不变量和数值翻倍溢出边界 |
| 31. [C++ 数据封装](../../../../content/cpp/cpp-oop/encapsulation.md) | 否 | partial | 私有余额、公有操作、失败保持状态、const查询、避免机械setter | 构造/存款/取款都应维护不变量；负金额、加法溢出和失败信号的完整设计 |
| 32. [C++ 接口（抽象类）](../../../../content/cpp/cpp-oop/interfaces.md) | 是 | partial | 抽象基类的接口角色、虚析构、最终具体重写、统一引用调用、替身Reader例子 | 多接口组合、资源所有权和异常约定、可替换性测试；现有小练习未覆盖全部设计约束 |
| 33. [C++ 文件和流](../../../../content/cpp/cpp-advanced/files.md) | 否 | partial | ifstream/ofstream/fstream、RAII关闭、临时工作目录范围、打开检查和写读闭环 | 模式表、打开成功与后续I/O成功区别、EOF/错误、二进制、游标/刷新/关闭错误、编码与原子替换 |
| 34. [C++ 异常处理](../../../../content/cpp/cpp-advanced/exceptions.md) | 是 | partial | throw/catch传播、具体类型顺序、按引用捕获、RAII展开、stoi全量解析、重抛、基本/强保证 | noexcept/terminate、自定义异常、保证等级实证、构造失败和跨线程异常传递；现有题只覆盖解析分支 |
| 35. [C++ 动态内存](../../../../content/cpp/cpp-advanced/dynamic-memory.md) | 是 | partial | new/delete[]配对、初始化/分配失败、拥有与借用、unique_ptr移动、RAII、shared_ptr循环风险 | shared/weak的完整例子、自定义删除器、数组大小溢出、复制移动与底层存储期/对象生存期 |
| 36. [C++ 命名空间](../../../../content/cpp/cpp-advanced/namespaces.md) | 否 | partial | 具名/嵌套作用域、限定符、using声明与指令、头文件污染 | 匿名/inline命名空间、别名、多文件定义、名称查找和ADL未展开 |
| 37. [C++ 模板](../../../../content/cpp/cpp-advanced/templates.md) | 是 | partial | 函数/类模板、推导与显式实参、类型要求、Box、冲突推导、定义可见性、concepts概述 | 约束的可编译例子、非类型参数、特化/重载、转发引用和实例化诊断；类模板未另设评估 |
| 38. [C++ 预处理器](../../../../content/cpp/cpp-advanced/preprocessor.md) | 否 | partial | include/define/ifdef、文本替换、类型/作用域缺失、constexpr替代 | 头文件守卫、宏参数多次求值、字符串化/拼接、条件表达式与构建参数的完整例子 |
| 39. [C++ 信号处理](../../../../content/cpp/cpp-advanced/signals.md) | 否 | partial | signal/raise、sig_atomic_t置位、主流程响应、不在处理器做I/O | 实现和平台差异、处理器允许操作的准确范围、注册失败、异步到达与同步raise区别；不能推导完整安全性 |
| 40. [C++ 多线程](../../../../content/cpp/cpp-advanced/threads.md) | 否 | partial | thread启动/join、锁保护共享更新、lock_guard、竞争/死锁提醒、分区后合并 | joinable生命周期、异常安全等待、参数传递、工作线程异常/取消、jthread/stop_token、性能与结果宽度 |
| 41. [C++ Web 编程](../../../../content/cpp/cpp-advanced/web.md) | 否 | partial | CGI环境/输入输出概述、头与空行、查询串拆分、分阶段校验 | CGI和HTTP报文责任区别、URL解码/重复键/正文长度、状态/错误响应、HTML转义；未验证真实服务器 |
| 42. [C++ STL 总览](../../../../content/cpp/cpp-stl-containers/overview.md) | 否 | partial | 容器/迭代器/算法协作、半开区间、accumulate初值类型、容器值语义 | 迭代器类别约束、复杂度/失效、分配/异常保证、范围算法与数值溢出不能仅靠0LL解决 |
| 43. [C++ 导入标准库](../../../../content/cpp/cpp-stl-containers/import.md) | 否 | partial | 按名include、std限定、C/C++风格头、显式包含提醒 | 标准头与传递包含的保证、C头命名空间细节、多源文件组织；实际主题为头文件并非模块import |
| 44. [C++ 标准库](../../../../content/cpp/cpp-stl-containers/standard-library.md) | 否 | partial | 标准库分类、abs边界、exit跳过局部析构、显式头 | 完整按任务检索表、numeric_limits使用、差值先溢出的边界与安全计算例子 |
| 45. [C++ <iostream>](../../../../content/cpp/cpp-stl-containers/iostream.md) | 否 | partial | 四标准流、提取/整行、换行残留、读取状态检查 | eof/fail/bad及恢复、flush/unitbuf、同步与重定向、Unicode和输出错误；需完整混读修复示例 |
| 46. [C++ <fstream>](../../../../content/cpp/cpp-stl-containers/fstream.md) | 否 | partial | 写读流、小作用域关闭、默认覆盖、打开检查、getline计数、app提示 | eof与I/O失败区分、写入/flush/close检查、二进制read/write、tell/seek、双向流状态切换、编码 |
| 47. [C++ <sstream>](../../../../content/cpp/cpp-stl-containers/sstream.md) | 否 | partial | istringstream解析、ostringstream拼接、状态/游标重置 | 非法尾随和范围失败区分、clear与str/seek配套、精度/locale、空白协议与全量解析案例 |
| 48. [C++ <iomanip>](../../../../content/cpp/cpp-stl-containers/iomanip.md) | 否 | partial | setw单次、fixed/setprecision保持、宽度不截断 | setfill/left/right、defaultfloat有效位数、格式状态恢复、舍入/负数/非有限值边界 |
| 49. [C++ <array>](../../../../content/cpp/cpp-stl-containers/array.md) | 否 | partial | 固定模板长度、size/at/[]、遍历、复制比较 | 零长度、初始化方式、data及生存期、数组引用/span、容器自身位置与堆/栈不能简单绑定 |
| 50. [C++ <vector>](../../../../content/cpp/cpp-stl-containers/vector.md) | 是 | partial | 连续存储、首尾非空检查、扩容失效、erase返回新迭代器、insert失效、capacity清理 | 较复杂元素的移动/异常保证、vector<bool>、批量erase、内存/长度边界；仅首尾题不评估新增删除案例 |
| 51. [C++ <list>](../../../../content/cpp/cpp-stl-containers/list.md) | 否 | partial | 双链表、成员稳定sort、splice名称、非随机访问、非被删元素迭代器稳定 | insert/erase返回值、splice的所有权/分配器前置条件、查找与分配成本；需明确被删迭代器失效 |
| 52. [C++ <forward_list>](../../../../content/cpp/cpp-stl-containers/forward-list.md) | 否 | partial | 单链、头插、front、无size/back和反向迭代 | before_begin/insert_after/erase_after、splice_after、删除循环、空表边界和复杂度权衡 |
| 53. [C++ <deque>](../../../../content/cpp/cpp-stl-containers/deque.md) | 否 | partial | 两端插入、随机访问、非整块连续、front/back与容器选择 | 头尾/中间增删对迭代器和引用的不同失效规则、空容器与at、实际复杂度/内存权衡 |
| 54. [C++ <stack>](../../../../content/cpp/cpp-stl-containers/stack.md) | 否 | partial | LIFO、top与无返回pop、empty检查、底层容器、括号匹配 | 嵌套错误定位、emplace、底层类型约束与无遍历接口；空串/非法字符的教学测试例子 |
| 55. [C++ <queue>](../../../../content/cpp/cpp-stl-containers/queue.md) | 否 | partial | FIFO、push/front/pop、back区别、超量出队检查 | 底层容器/emplace、无遍历接口、计数输入边界；线程安全队列与普通queue的区别 |
| 56. [C++ <priority_queue>](../../../../content/cpp/cpp-stl-containers/priority-queue.md) | 否 | partial | 默认最大堆、最小堆比较器、top/pop、空堆风险 | 比较器严格弱序、自定义记录、建堆/操作复杂度、相等优先级与可重复输出顺序、全序弹出过程 |
| 57. [C++ <set>](../../../../content/cpp/cpp-stl-containers/set.md) | 否 | partial | 有序唯一、insert/count/size、对数操作 | 比较器等价而非简单==、insert返回值、find/erase/lower_bound、键不可改、multiset与失效规则 |
| 58. [C++ <unordered_set>](../../../../content/cpp/cpp-stl-containers/unordered-set.md) | 否 | partial | 无序哈希、平均/最坏复杂度、查找、输出排序提醒 | hash和相等谓词一致性、load_factor/reserve/rehash与失效、自定义键、性能不能仅按平均复杂度判断 |
| 59. [C++ <map>](../../../../content/cpp/cpp-stl-containers/map.md) | 否 | partial | 有序键值、计数、[]默认插入、find/count/at、按键遍历 | try_emplace/insert_or_assign、比较器等价、erase/lower_bound、键不可改和引用/迭代器失效 |
| 60. [C++ <unordered_map>](../../../../content/cpp/cpp-stl-containers/unordered-map.md) | 否 | partial | 哈希计数、[]副作用、平均/最坏复杂度、辅助vector保首次顺序 | hash/equality契约、rehash和引用/迭代器失效区别、reserve/load_factor、恶意冲突和重复键更新 |
| 61. [C++ <bitset>](../../../../content/cpp/cpp-stl-containers/bitset.md) | 否 | partial | 定长位、整数/字符串构造、count/flip、位序、交集 | 构造截取与非法字符的准确区别、test/set/位移、to_ulong溢出、代理引用；边界须区分库规则与练习限制 |
| 62. [C++ <algorithm>](../../../../content/cpp/cpp-algorithms-concurrency/algorithm.md) | 否 | partial | sort/find/count/min/max概览、半开区间、降序、空结果检查、中位位置 | 迭代器/严格弱序前置条件、稳定排序、二分需有序、remove/unique逻辑结束、复制输出容量、偶数中位数定义 |
| 63. [C++ <iterator>](../../../../content/cpp/cpp-algorithms-concurrency/iterator.md) | 否 | partial | begin/end、find、随机访问相减、next/prev/advance、尾后不可解引用 | 输入/前向/双向/随机访问类别、distance复杂度、back_inserter和流迭代器、容器修改失效与跨容器非法区间 |
| 64. [C++ <functional>](../../../../content/cpp/cpp-algorithms-concurrency/functional.md) | 否 | partial | function装lambda、count_if、按值/引用捕获、悬垂/分配提醒、bind名称 | 空function、可复制目标限制、mutable与捕获*this、reference_wrapper/bind/invoke、异步捕获对象生命周期 |
| 65. [C++ <numeric>](../../../../content/cpp/cpp-algorithms-concurrency/numeric.md) | 否 | partial | partial_sum/back_inserter、iota、accumulate宽度、inner_product概览 | partial_sum与accumulate的累加类型不能混同、宽类型前缀和、输出容量、inner_product长度、reduce顺序与溢出 |
| 66. [C++ <complex>](../../../../content/cpp/cpp-algorithms-concurrency/complex.md) | 否 | partial | real/imag、四则、abs/norm、相等和误差 | 复除零/非有限值、conj/arg/polar、分支切割/复数学函数、运算/输出精度边界 |
| 67. [C++ <valarray>](../../../../content/cpp/cpp-algorithms-concurrency/valarray.md) | 否 | partial | 逐元素运算/原地更新、sum、size、slice名称、自由begin/end提示 | 等长前置条件、空聚合、表达式模板与临时生存期、slice赋值/重叠、数值溢出；不能直接断言中间全物化 |
| 68. [C++ <cmath>](../../../../content/cpp/cpp-algorithms-concurrency/cmath.md) | 否 | partial | pow/sqrt/floor/ceil/fabs/llround、浮点转整数提醒 | 定义域/范围报告的实现条件、NaN/Inf/isfinite、负数舍入、llround范围、整数幂也要防溢出 |
| 69. [C++ <string>](../../../../content/cpp/cpp-algorithms-concurrency/string.md) | 否 | partial | getline/提取、字符统计、find/npos、substr、at/[]、reserve | 字节与Unicode、npos算术、pos==size边界、字符指针/视图失效、插入删除/替换和内嵌NUL |
| 70. [C++ <regex>](../../../../content/cpp/cpp-algorithms-concurrency/regex.md) | 否 | partial | regex_match/search、量词、ASCII范围、regex_error、编译复用 | 捕获/迭代查找/replace、原始字符串转义、语法选项和锚点边界、输入长度/性能；完整匹配不等于任意^...$语义 |
| 71. [C++ <ctime>](../../../../content/cpp/cpp-algorithms-concurrency/ctime.md) | 否 | partial | time_t/gmtime/tm、年/月偏移、静态缓冲和线程提醒 | epoch/表示的实现边界、gmtime失败检查、localtime/mktime本地时区、DST、缓冲覆盖和平台_s/_r差异 |
| 72. [C++ <chrono>](../../../../content/cpp/cpp-algorithms-concurrency/chrono.md) | 否 | partial | 类型化duration、duration_cast/count、steady/system时钟、单位端点 | 负数向零截断与floor/ceil区别、表示范围/非有限转换、time_point/日历时区、计时重复性 |
| 73. [C++ <thread>](../../../../content/cpp/cpp-algorithms-concurrency/thread.md) | 否 | partial | 构造/join/joinable、复制参数/std::ref、独立结果、异常不自动传回、detach名称 | 可连接析构/移动语义、工作函数未捕获异常终止、异常安全join、detach生存期、jthread取消和共享状态契约 |
| 74. [C++ <mutex>](../../../../content/cpp/cpp-algorithms-concurrency/mutex.md) | 否 | partial | lock/unlock、lock_guard RAII、竞争、scoped_lock和固定锁序、短临界区 | 读读与冲突访问区别、unique_lock所有权状态、try/timed锁、锁粒度和异常路径、多锁完整防死锁示例 |
| 75. [C++ <condition_variable>](../../../../content/cpp/cpp-algorithms-concurrency/condition-variable.md) | 否 | partial | 谓词wait、unique_lock释放/重获锁、共享状态更新后notify、虚假唤醒 | 通知不存储事件、丢失唤醒和同一互斥量契约、wait_for/until超时/终止、队列消费者与异常退出 |
| 76. [C++ <future>](../../../../content/cpp/cpp-algorithms-concurrency/future.md) | 否 | partial | async显式策略、future/get/valid、延迟执行、promise单值、异常传递概述 | 重复set的future_error与无状态get的前置条件需区分、wait_for/shared_future、broken_promise、析构等待和线程异常显式存储 |
| 77. [C++ <atomic>](../../../../content/cpp/cpp-algorithms-concurrency/atomic.md) | 否 | partial | load/store/fetch_add、CAS、默认顺序一致、多语句不自动原子 | CAS失败更新expected/弱CAS重试、对象类型和lock-free非保证、发布/获取/relaxed的适用边界、复合状态和计数溢出 |
| 78. [C++ 有用的资源](../../../../content/cpp/cpp-capstone/useful-resources.md) | 否 | partial | 资源按用途归类、名称/类别/用途、版本提醒、受限类别统计 | 实际链接和标准版本查证路径、参考站与标准/实现的层次、过期资料核验案例 |
| 79. [C++ 实例：从需求到可验证程序](../../../../content/cpp/cpp-capstone/examples.md) | 否 | partial | 需求到合同、vector汇总、min/accumulate、初值宽度、空输入检查提醒 | 空区间返回end和解引用应区分、求和溢出/最值哨兵、更多算法实例与复杂度；三个汇总不覆盖实例大全 |
| 80. [C++ 测验与路线结业](../../../../content/cpp/cpp-capstone/quiz.md) | 否 | partial | 选项/数量验证、知识与代码题、双线程分区、join后主线程汇总、边界列表 | 解释性诊断与分层复习、完整可复制结业数据流、错误/异常与线程生命周期；未评估所有标准库主题 |
| 81. [C++ <type_traits>](../../../../content/cpp/cpp-capstone/type-traits.md) | 否 | partial | is_integral/floating/same/pointer/reference、_v、if constexpr、static_assert | 丢弃分支仍有解析/非依赖诊断规则、remove_cvref/变换、类型别名平台关系、概念约束和测试矩阵 |
| 82. [C++ <typeinfo>](../../../../content/cpp/cpp-capstone/typeinfo.md) | 否 | partial | typeid比较、动态多态概述、type_info不可复制、name实现相关、顶层cv/ref忽略 | 指针对象与解引用glvalue的实际对照、空多态指针bad_typeid、求值与编译期能力的准确限制 |
| 83. [C++ <exception>](../../../../content/cpp/cpp-capstone/exception.md) | 否 | partial | std::exception基类、const引用捕获、what、顺序、throw重抛 | 用户异常不必继承此基类、exception_ptr/current_exception/rethrow_exception、terminate/noexcept与跨线程传递 |
| 84. [C++ <stdexcept>](../../../../content/cpp/cpp-capstone/stdexcept.md) | 否 | partial | 标准异常族、at/out_of_range、[]对照、消息和捕获顺序 | logic/runtime家族分类、算术不会自动抛overflow_error、负索引到size_t转换、失败语义与异常安全保证 |
| 85. [C++ <cstdio>](../../../../content/cpp/cpp-capstone/cstdio.md) | 否 | partial | printf数制/宽度/补零、scanf返回项数、格式与类型匹配 | scanf范围溢出与缓冲区宽度、fgets/EOF、格式串注入、inttypes可移植格式、混用iostream与错误检查 |
| 86. [C++ <cstdint>](../../../../content/cpp/cpp-capstone/cstdint.md) | 否 | partial | int64_t/uint8_t定宽、边界宏、直接流输入、符号混用提醒 | 精确宽度类型可选性、least/fast/intmax/intptr、uint8_t字符输出、相加前范围检查、可移植格式 |
| 87. [C++ <memory>](../../../../content/cpp/cpp-capstone/memory.md) | 否 | partial | unique_ptr/make_unique、移动非复制、get/release、数组、借用不可delete | reset与自定义删除器、shared/weak循环与引用计数线程语义、移动后状态与资源释放的完整案例 |
| 88. [C++ <new>](../../../../content/cpp/cpp-capstone/new.md) | 否 | partial | new[]/delete[]、默认bad_alloc、nothrow空值、零长度不可解引用 | 数组长度和字节乘法边界、初始化、构造失败释放、对齐/placement new、所有者RAII和异常安全 |
| 89. [C++ <utility>](../../../../content/cpp/cpp-capstone/utility.md) | 否 | partial | pair字典序、make_pair、成员访问、move概述 | move只转换值类别并不必然移动、被移动对象可执行的操作、forward/perfect forwarding、swap/exchange |
| 90. [C++ <random>](../../../../content/cpp/cpp-capstone/random.md) | 否 | partial | mt19937与distribution分工、固定种子、闭区间、状态消耗、避免循环重建 | 引擎与分布跨实现复现范围、random_device不保证密码安全、给MT随机种子也非CSPRNG、分布/安全随机选型 |
| 91. [C++ <locale>](../../../../content/cpp/cpp-capstone/locale.md) | 否 | partial | classic locale、字符分类、name实现相关、分类统计 | locale模板重载与cctype参数域区别、facet/imbue、C与C++ locale交互、Unicode非逐字节分类 |
| 92. [C++ <codecvt>](../../../../content/cpp/cpp-capstone/codecvt.md) | 否 | partial | 弃用背景、ASCII窄宽直映射、字节数非字符数、字母值练习 | 标准版本移除状态、UTF-8/UTF-16代理对/wchar宽度、无效序列与往返、生产编码库选择；未真正调用codecvt |
| 93. [C++ <cassert>](../../../../content/cpp/cpp-capstone/cassert.md) | 否 | partial | assert内部不变量、NDEBUG取消、禁止副作用、失败abort、外部输入另验 | 调试/发布双构建行为验证、static_assert区别、宏逗号/表达式、诊断不可当异常恢复 |
| 94. [C++ <cwchar>](../../../../content/cpp/cpp-capstone/cwchar.md) | 否 | partial | mbstowcs宽字符转换、wcscmp三态、缓冲和失败提醒 | locale依赖、截断时终止符保证、返回size_t(-1)检查、wchar并非通用码点、头文件和转换容量 |
| 95. [C++ <climits>](../../../../content/cpp/cpp-capstone/climits.md) | 否 | partial | INT_MIN/MAX、LLONG_MAX、CHAR_BIT、实现范围与平台假设 | numeric_limits替代、char符号性、范围先验检查；不可把所有平台硬编码32位或溢出称必然回绕 |
| 96. [C++ <cfloat>](../../../../content/cpp/cpp-capstone/cfloat.md) | 否 | partial | epsilon/MAX、浮点近似比较示例、epsilon不是最小正数 | 绝对/相对混合容差与量级、NaN/Inf、有符号零、DBL_MIN/TRUE_MIN、精度/舍入和业务误差模型 |
| 97. [C++ <cstdlib>](../../../../content/cpp/cpp-capstone/cstdlib.md) | 否 | partial | strtol基数/endptr、非法尾巴、ERANGE、atoi歧义 | errno先清零、long转目标整数范围、前导空白/符号协议、from_chars替代、不同平台long宽度 |
| 98. [C++ <numbers>](../../../../content/cpp/cpp-capstone/numbers.md) | 否 | partial | C++20数学常量、pi/pi_v浮点类型、constexpr、圆面积格式化 | 标准版本/工具链特性检查、常量精度与面积乘法溢出/非有限值、单位和误差传播 |
| 99. [C++ OpenCV](../../../../content/cpp/cpp-capstone/opencv.md) | 否 | partial | Mat API识别注释、灰度矩阵fixture、行列顺序、阈值计数、BGR提醒 | 真实依赖/编译、Mat共享浅复制/clone/ROI、类型/通道/步长、threshold比较语义、图像读写错误和资源生命周期 |
