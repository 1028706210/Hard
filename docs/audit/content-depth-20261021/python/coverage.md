# Python 首轮教学深度覆盖矩阵

审查本地全部 84 篇课文。来源主题清单是依课程主题整理的复核维度，不声称逐段核对 84 个外部章节；技术核对集中在本轮修改的 14 课，各课附 Python 官方资料。菜鸟链接保留为目录来源，不复制正文。

“已扩充”仅表示补足列明子主题，全部课时仍列出剩余项。未使用语义全覆盖或覆盖率百分比。第三方/联网/GUI/数据库章节的 fixture 练习保留，其不足仍作为教学缺口记录。

| 课程 / 本轮状态 | 来源主题复核维度 | 当前已讲 | 剩余与边界 |
| --- | --- | --- | --- |
| [Python 爬虫解析边界](../../../../content/python/python-automation-ui-web/crawler.md) 未修改 | 获取、解析、提取、访问规则 | 本地 h1 实体和内联解析 | 获取流程、解析器选择、分页、速率、错误 |
| [Python Markdown 安全转换](../../../../content/python/python-automation-ui-web/markdown.md) 未修改 | 语法、解析、HTML 净化 | 仅简化标题识别 | 列表/链接/代码、解析库、净化 |
| [Python pyecharts 数据准备](../../../../content/python/python-automation-ui-web/pyecharts.md) 未修改 | 图表对象、配置、渲染、数据 | 仅 labels/values 类型和长度 | Bar/Line API、坐标/系列/选项、本地渲染 |
| [Python PyQt 界面状态](../../../../content/python/python-automation-ui-web/pyqt.md) 未修改 | 窗口控件、信号槽、事件循环 | 仅保存条件和状态逻辑 | 真实 QApplication/窗口/信号槽、线程边界 |
| [Python Scrapy 请求计划](../../../../content/python/python-automation-ui-web/scrapy.md) 未修改 | Spider/Request/Response、回调、管道 | 仅计划白名单和去重 | 项目结构、选择器、yield、管道、设置 |
| [Python selenium 选择器设计](../../../../content/python/python-automation-ui-web/selenium.md) 未修改 | 驱动、定位、等待、交互、关闭 | fake 定位点击、finally 清理 | 真实 API、显式等待、陈旧元素、浏览器验证 |
| [AI 绘画任务的离线规格](../../../../content/python/python-capstone/ai-draw.md) 未修改 | 请求、规格、状态、结果 | 仅提示词尺寸规格 | 提供方接口、状态、保存、失败路径 |
| [Python 实例：从需求到可验证程序](../../../../content/python/python-capstone/examples.md) 未修改 | 输入输出、分解、算法、边界 | 成绩分类、排序副本 | 成组进阶实例和复杂度 |
| [Python AI 客户端的本地契约](../../../../content/python/python-capstone/openai.md) 未修改 | 客户端、请求响应、错误、配置 | 仅离线结构提取 | 版本化实际 API、流、错误、超时教学 |
| [量化策略的离线回测边界](../../../../content/python/python-capstone/quant.md) 未修改 | 序列、策略、回测、风险 | 仅相邻比较 | 收益、时间顺序、成本、偏差 |
| [Python 路线自测与诊断](../../../../content/python/python-capstone/quiz.md) 未修改 | 诊断、反馈、综合 | 规范化、汇总、协程挑战 | 分层测验与解释性反馈 |
| [Python asyncio](../../../../content/python/python-concurrency-network/asyncio.md) 未修改 | 协程任务、调度、取消、并发 | 本地 await/gather、取消和等待 | TaskGroup、超时、阻塞调用、异常传播 |
| [Python 多线程](../../../../content/python/python-concurrency-network/multithreading.md) 未修改 | 创建、生命周期、共享状态 | 只汇总已完成结果 | GIL、I/O/CPU 分工、生命周期、协调 |
| [Python requests](../../../../content/python/python-concurrency-network/requests.md) 未修改 | HTTP 方法、状态、超时、响应、会话 | 仅状态 fixture | 实际 API、timeout、raise_for_status、Session |
| [Python SMTP](../../../../content/python/python-concurrency-network/smtp.md) 未修改 | 消息、连接、TLS、认证 | 仅消息字段 fixture | EmailMessage、传输、认证、异常 |
| [Python 网络编程](../../../../content/python/python-concurrency-network/sockets.md) 未修改 | 客户端服务端、字节流、分帧、超时 | 仅本地消息解析 | 生命周期、部分收发、编码、分帧/超时教学 |
| [Python subprocess](../../../../content/python/python-concurrency-network/subprocess.md) 未修改 | 参数列表、结果、超时、管道 | 只校验命令清单 | run/check/capture_output/timeout、shell/错误路径 |
| [Python threading](../../../../content/python/python-concurrency-network/threading.md) 未修改 | Thread/Lock/join、协调、失败 | 有限真实线程和锁、禁止 sleep 猜测 | Event/Condition、死锁、异常汇总、取消 |
| [Python urllib](../../../../content/python/python-concurrency-network/urllib.md) 未修改 | URL 解析编码、请求、错误 | urlsplit/urlencode、白名单 | urlopen、超时、HTTPError/URLError、关闭 |
| [Python 基础语法](../../../../content/python/python-core-types/basic-syntax.md) 未修改 | 缩进、绑定、语句、字面量 | 执行顺序与缩进 | 多行语句、标识符、语法诊断 |
| [Python 注释](../../../../content/python/python-core-types/comments.md) 未修改 | 注释、docstring、可读性 | 注释表达原因与标识符边界 | 文档字符串和普通字符串区别 |
| [Python 数据类型转换](../../../../content/python/python-core-types/conversion.md) 已扩充 | 数值文本转换、容器、真假、编码 | 新增截断/基数/异常、非有限数、容器、字节转换 | 自定义转换协议与复杂精度案例 |
| [Python 基本数据类型](../../../../content/python/python-core-types/data-types.md) 已扩充 | 标量容器、自省、真假、可变性 | 新增类型表、None、bool 子类、引用、相等/身份 | 复数等其他类型、自定义类型协议 |
| [Python 数字](../../../../content/python/python-core-types/numbers.md) 未修改 | 数值类型、运算、精度 | 除法取余、负数符号、零除数 | 浮点误差、复数、Decimal/Fraction |
| [Python 运算符](../../../../content/python/python-core-types/operators.md) 未修改 | 算术、比较、逻辑、成员、身份、位运算 | 减法、严格大于、赋值区别 | 短路返回值、链式比较、优先级、位运算 |
| [Python 字符串](../../../../content/python/python-core-types/strings.md) 未修改 | 索引切片、格式化、方法、编码 | Unicode、切片边界、split/join、f-string | 转义/格式说明、码点与字形区别 |
| [CGI 的请求边界](../../../../content/python/python-database-deployment/cgi.md) 未修改 | 请求响应、历史支持、替代 | 仅表单函数，头部示例仍用字面转义 | 历史模块移除状态、报文换行、现代接口选择 |
| [MongoDB 文档与查询边界](../../../../content/python/python-database-deployment/mongodb.md) 未修改 | 文档 CRUD、过滤、更新、索引 | 仅白名单和内存过滤 | 客户端 API、操作符、索引、权限 |
| [mysql-connector 与参数化查询](../../../../content/python/python-database-deployment/mysql-connector.md) 未修改 | 连接游标、参数、CRUD、事务 | 仅模板与参数 | 实际 API、关闭、事务、类型 |
| [PyMySQL 的事务意图](../../../../content/python/python-database-deployment/pymysql.md) 未修改 | 连接游标、参数、事务、异常 | 仅提交回滚意图 | 实际事务调用、受控数据库验证 |
| [uWSGI 部署配置审查](../../../../content/python/python-database-deployment/uwsgi.md) 未修改 | WSGI、进程、配置、部署 | 仅顶层键检查 | 入口契约、配置项、进程模型、运行边界 |
| [Python 推导式](../../../../content/python/python-flow-collections/comprehensions.md) 未修改 | 列表/集合/字典推导、过滤、嵌套 | 列表变换过滤 | 集合/字典推导、嵌套顺序、变量范围 |
| [Python 条件控制](../../../../content/python/python-flow-collections/conditions.md) 未修改 | if/elif/else、真假、条件表达式 | if/else 和阈值 | elif、多条件短路、条件表达式 |
| [Python 数据结构](../../../../content/python/python-flow-collections/data-structures.md) 已扩充 | 容器选择、栈队列、组合、遍历 | 新增选择表、deque、enumerate/zip、重复键边界 | 复杂索引/分组；树图等不在本轮 |
| [Python 字典](../../../../content/python/python-flow-collections/dictionaries.md) 已扩充 | 键、CRUD、顺序、视图、默认值 | 新增更新删除、视图/items、计数、相等键、浅复制 | 合并、defaultdict、自定义键 |
| [Python 编程第一步](../../../../content/python/python-flow-collections/first-program.md) 未修改 | 输入处理输出、变换 | upper 和返回新值 | 需求到可复用程序的完整案例 |
| [Python for 循环](../../../../content/python/python-flow-collections/for-loop.md) 未修改 | 可迭代、range、循环控制 | 右端点、零次循环 | 负步长、enumerate/zip、本课 break/else 实例 |
| [Python 列表](../../../../content/python/python-flow-collections/lists.md) 已扩充 | 索引切片、CRUD、排序、复制 | 新增方法对比、浅复制/共享、栈队列选择 | 扩展切片限制、复杂排序、深复制策略 |
| [Python 循环语句](../../../../content/python/python-flow-collections/loops.md) 未修改 | for/while、break/continue、else | 有限遍历、顺序和重复 | break/continue、循环 else、嵌套 |
| [Python 集合](../../../../content/python/python-flow-collections/sets.md) 已扩充 | 构造、去重、运算、更新、frozenset | 新增交并差、子集、哈希、删除区别、顺序 | 自定义哈希对象、复杂集合建模 |
| [Python 元组](../../../../content/python/python-flow-collections/tuples.md) 已扩充 | 构造、解包、操作、不可变、可哈希 | 新增逗号/解包、嵌套可变、字典键 | namedtuple/dataclass 的选择 |
| [Python while 循环](../../../../content/python/python-flow-collections/while-loop.md) 未修改 | 状态推进、退出、循环控制 | 计数状态与端点 | 提前退出、continue 更新陷阱、else |
| [Hello World](../../../../content/python/python-foundations/hello-world.md) 未修改 | print、文本、首个脚本 | 输出与变量 | 泛化提示仍待改为本课具体说明，无需人为失败分支 |
| [安装后的第一项检查](../../../../content/python/python-foundations/installation.md) 未修改 | 安装、路径、版本验证 | 版本记录格式与环境验证区别 | 平台安装步骤、解释器定位 |
| [在解释器中验证想法](../../../../content/python/python-foundations/interpreter.md) 未修改 | REPL、脚本、执行选项 | 会话状态与表达式 | 退出、命令行选项与脚本参数 |
| [Python 的学习方式](../../../../content/python/python-foundations/introduction.md) 未修改 | 语言用途、执行、学习反馈 | 编辑运行观察与输入输出边界 | 适用范围、实现与版本差异 |
| [选择与整理学习资源](../../../../content/python/python-foundations/learning-resources.md) 未修改 | 文档、版本、资源筛选 | 名称用途版本的记录 | 实际文档问题导航示例 |
| [用 pip 管理依赖](../../../../content/python/python-foundations/package-management.md) 未修改 | pip、约束、安装目标 | 依赖声明与简化格式 | python -m pip、需求文件、卸载、冲突 |
| [用 PyCharm 组织项目](../../../../content/python/python-foundations/pycharm.md) 未修改 | 解释器、运行、调试 | 入口与解释器职责 | 配置步骤、断点和变量观察 |
| [为项目隔离虚拟环境](../../../../content/python/python-foundations/virtual-environment.md) 未修改 | venv、激活、依赖隔离 | 隔离价值与清单去重 | 创建/激活/退出及环境确认步骤 |
| [用 VS Code 编辑与运行](../../../../content/python/python-foundations/vscode.md) 未修改 | 扩展、解释器、运行调试 | 解释器与入口的顺序 | 调试步骤与环境排错 |
| [Python 装饰器](../../../../content/python/python-functions-iteration/decorators.md) 已扩充 | 时机、包装、工厂、叠加、元数据 | 新增参数/返回转发、wraps、配置闭包、顺序 | 异步包装、缓存/重试的实际约束 |
| [Python 函数](../../../../content/python/python-functions-iteration/functions.md) 已扩充 | 参数、默认值、可变参数、返回 | 新增位置/关键字专用、展开、默认共享、对象传递 | 递归仅边界说明，缺执行轨迹实例 |
| [Python 迭代器与生成器](../../../../content/python/python-functions-iteration/iterators.md) 已扩充 | iter/next、协议、yield、表达式 | 新增自定义迭代器、耗尽、延迟顺序、内存边界 | yield from、send/throw/close、异步迭代 |
| [Python lambda](../../../../content/python/python-functions-iteration/lambda.md) 未修改 | 表达式函数、回调、捕获 | 简单转换、排序 key | 晚绑定实例、map/filter 与生成器选择 |
| [Python __name__](../../../../content/python/python-functions-iteration/name-main.md) 未修改 | 执行、导入、入口 | 模块名、守卫、两种运行提示 | 多文件完整案例、python -m |
| [Python 命名空间与作用域](../../../../content/python/python-functions-iteration/scope.md) 已扩充 | 命名空间、LEGB、闭包、global/nonlocal | 新增捕获、未绑定局部、nonlocal、作用域边界 | global 修改和晚绑定的实测实例 |
| [Python 类型注解](../../../../content/python/python-functions-iteration/type-hints.md) 未修改 | 参数返回、容器、联合、工具 | 参数返回注解、不自动校验 | list[T]、T 或 None、泛型、工具诊断 |
| [Python with](../../../../content/python/python-functions-iteration/with.md) 未修改 | 上下文协议、进入退出、异常、资源 | nullcontext、语法、不创建作用域 | __enter__/__exit__、抑制异常、contextmanager |
| [Python 面向对象](../../../../content/python/python-modules-io-oop/classes.md) 已扩充 | 属性方法、继承、多继承、重写、封装、特殊方法 | 新增实例/类状态、super/MRO、多态、名称改写、__add__ | classmethod/staticmethod 仅解释；property/描述器/反向运算未展开 |
| [Python 错误和异常](../../../../content/python/python-modules-io-oop/exceptions.md) 已扩充 | 传播、处理顺序、else/finally、raise | 新增控制流、自定义异常、原因链、断言/清理边界 | ExceptionGroup/except*、跨层错误接口 |
| [Python 文件](../../../../content/python/python-modules-io-oop/files.md) 已扩充 | 模式、文本字节、游标、行、清理 | 新增模式表、临时文件、编码、seek、异常、缓冲 | 原子替换/耐久性仅说明限制，未实现策略 |
| [Python 输入和输出](../../../../content/python/python-modules-io-oop/input-output.md) 未修改 | input/print、格式、标准流 | 整数解析和 f-string | sep/end、EOF、stderr、格式说明 |
| [Python 模块](../../../../content/python/python-modules-io-oop/modules.md) 未修改 | 导入、搜索、包、命名空间 | import/from、冲突、入口原则 | 包/相对导入、搜索顺序、缓存、循环导入 |
| [Python OS](../../../../content/python/python-modules-io-oop/os.md) 未修改 | 路径、目录、环境、系统 | PurePosixPath 的文本边界 | os/pathlib 常用目录操作、环境读取 |
| [Python 内置函数](../../../../content/python/python-stdlib-data/builtins.md) 未修改 | 内建函数、参数、空值 | len/sum、元素数量 | min/max 默认值、all/any、自省等 |
| [Python csv](../../../../content/python/python-stdlib-data/csv.md) 未修改 | reader/writer、表头、引号换行 | 表头读取与列校验 | writer、newline/编码、dialect、往返 |
| [Python 日期和时间](../../../../content/python/python-stdlib-data/date-time.md) 未修改 | 日期时间、格式、解析 | date、日历、ISO | 时间戳、时区、模块分工 |
| [Python datetime](../../../../content/python/python-stdlib-data/datetime.md) 未修改 | date/datetime/timedelta、时区 | 日期加减、闰年、溢出 | aware/naive、转换、时间戳、DST |
| [Python hashlib](../../../../content/python/python-stdlib-data/hashlib.md) 未修改 | 摘要、字节编码、流式更新 | SHA-256 完整摘要、UTF-8、非加密 | update 分块、不同算法、安全比较与口令派生区分 |
| [Python JSON](../../../../content/python/python-stdlib-data/json.md) 未修改 | 序列化、类型映射、字段 | dumps/loads、校验、bool/int | 流接口、非有限数、自定义编码 |
| [Python logging](../../../../content/python/python-stdlib-data/logging.md) 未修改 | 等级、logger/handler/formatter | 过滤、stdout、占位参数、秘密边界 | 模块 logger、异常、处理器、格式 |
| [Python math](../../../../content/python/python-stdlib-data/math.md) 未修改 | 函数、定义域、浮点 | ceil/sqrt、固定格式 | isclose、三角函数、常量、非有限数 |
| [Python operator](../../../../content/python/python-stdlib-data/operator.md) 未修改 | 函数运算、getter | add/gt、类型决定行为 | itemgetter/attrgetter、排序回调 |
| [Python 标准库概览](../../../../content/python/python-stdlib-data/overview.md) 未修改 | 标准库分类与检索 | 优先标准库、ceil 方向 | 按任务导航、版本可用性 |
| [Python Pickle](../../../../content/python/python-stdlib-data/pickle.md) 未修改 | 往返、协议、信任 | 仅受信内存往返，拒绝不可信加载 | 协议选择、类型限制、兼容性 |
| [Python queue](../../../../content/python/python-stdlib-data/queue.md) 未修改 | FIFO、阻塞、超时、完成 | Queue/get_nowait、竞争提醒 | maxsize/timeout、task_done/join 协调 |
| [Python random](../../../../content/python/python-stdlib-data/random.md) 未修改 | 随机源、种子、选择、抽样 | Random、choice、复现边界 | randrange/sample/shuffle、分布、版本 |
| [Python re 模块](../../../../content/python/python-stdlib-data/re.md) 未修改 | 匹配搜索、分组、替换、标志 | compile/fullmatch、输入原文 | 分组、sub、finditer、标志、性能 |
| [Python 正则表达式基础](../../../../content/python/python-stdlib-data/regex-basics.md) 未修改 | 模式、转义、量词、分组 | 原始字符串、ASCII、fullmatch | 分组、替换、贪婪/非贪婪、复杂度 |
| [Python statistics](../../../../content/python/python-stdlib-data/statistics.md) 未修改 | 均值、中位数、样本、方差 | mean/median、重复样本 | 方差/标准差、总体/样本、缺失数据 |
| [Python StringIO](../../../../content/python/python-stdlib-data/stringio.md) 未修改 | 文本流、游标、取值 | write/seek/read、getvalue | 关闭、流接口注入消费者 |
| [Python sys](../../../../content/python/python-stdlib-data/sys.md) 未修改 | 解释器、参数、标准流、退出 | version_info、argv 形状 | argv 实例、标准流、退出码 |
| [Python XML](../../../../content/python/python-stdlib-data/xml.md) 未修改 | 元素属性、查询、序列化、限制 | ElementTree、受限结构 | 层级查询、写出、完整安全评估 |
