# Hard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `D:\projects\1\Hard` 交付一个本地优先、桌面与手机功能一致的编程学习网站，完整覆盖菜鸟教程 Python、Java、C#、C++ 主教程目录，并提供可执行练习、评分、复习、搜索、笔记、成长分析和可靠备份。

**Architecture:** Vue 3 + TypeScript 单页前端与 FastAPI 模块化单体后端通过 `/api/v1` 通信；只读课程内容存放在 Git 管理的 Markdown/YAML/JSON 中，可变学习数据存入 SQLite + FTS5；代码运行由统一任务管理器调用四个本地适配器。所有项目数据与可配置工具均位于 D 盘。

**Tech Stack:** Node.js 24.17、pnpm 11.19、Vue 3.5.41、Vue Router 5.2.0、Pinia 4.0.3、Vite 8.2.2、TypeScript 7.0.2、Monaco Editor 0.56.0、Vitest 4.1.11、Vue Test Utils 2.4.11、Playwright 1.62.1；Python 3.13、FastAPI 0.141.1、Pydantic v2、SQLAlchemy 2.0、Alembic、pytest；SQLite/FTS5；Java 17、.NET 10 SDK、MSYS2 UCRT64 GCC。

**Spec:** `docs/superpowers/specs/2026-08-23-hard-programming-learning-platform-design.md`

**Visual target:** `docs/design/hard-homepage-visual-target.png`

---

## 0. Terra 执行与审计硬门禁

以下规则适用于每个任务，优先级高于任务正文：

1. 一次只执行一个编号任务。不得预做、顺手做或提交后续任务。
2. 开始前阅读本文件、设计规格和当前 `git status`；发现与任务无关的用户修改时保留并报告。
3. 行为变更必须先写失败测试或失败验证器，确认失败原因正确，再写最小实现。
4. 只改任务列出的路径。确需越界时停止并向项目经理申请，不得自行扩大范围。
5. 不得用 Codex、Workbuddy 内部 Python 作为产品运行时；项目虚拟环境必须由 `D:\DevTools\python\python.exe` 创建。
6. 下载工具、修改 Windows 防火墙或写入 `D:\DevTools` 前，使用产品批准流程取得用户授权。
7. 每项仅生成一个原子 Git 提交。提交消息必须使用任务给出的文字。
8. 完成后按本节模板报告并立即停止，等待项目经理审计；未获得“通过，执行下一项”不得继续。

每项交付报告必须包含：

```text
任务：Task N — 名称
提交：<完整 commit hash>
变更：<逐文件列出>
验证：<命令 + 退出码 + 关键结果>
证据：<截图绝对路径 / 覆盖率 / 内容覆盖报告；不适用则写“不适用”>
限制：<已知限制；没有则写“无”>
状态：已停止，等待审计
```

审计拒绝时，只修复当前任务并使用 `git commit --amend` 保持单提交；再次报告并停止。

## 1. 固定目录与接口地图

实现必须收敛到以下边界，不创建第二套平行架构：

```text
Hard/
  apps/
    api/
      pyproject.toml
      alembic.ini
      src/hard_api/
        api/                 # HTTP 路由、请求/响应模型
        core/                # 配置、错误、日志、时间、幂等
        db/                  # SQLAlchemy、迁移、事务
        content/             # 课程解析、校验、目录
        learning/            # 进度、评分、解锁、复习、成长
        search/              # FTS5
        runners/             # 队列、限制、四语言适配器
        backup/              # 备份、导入、导出
      tests/
    web/
      src/
        api/                 # 生成的 OpenAPI 类型与薄客户端
        app/                 # 路由、外壳、全局状态
        design/              # tokens、动效、响应式基础
        features/            # map/course/assessment/review/search/growth/settings
      tests/
  content/
    sources.yaml
    concepts.yaml
    <language>/course.yaml
    <language>/<module>/<lesson>.md
    <language>/<module>/<lesson>.exercises.json
  packages/contracts/openapi.json
  scripts/
  tools/content/
  tests/e2e/
  docs/
```

核心 API 仅使用 `/api/v1`，统一错误体为：

```json
{"error":{"code":"stable_code","message":"中文可读消息","details":{},"request_id":"uuid"}}
```

核心实体 ID 规则：课程 `python|java|csharp|cpp`；模块 `<language>-<slug>`；课时 `<module>-<slug>`；题目 `<lesson>-kNN|cNN|challenge`。ID 一经进入数据库不得改名。

## 2. 全局完成标准

- 后端：`pytest` 全部通过，`hard_api` 总行覆盖率不低于 85%，评分、复习、备份和 runner 核心模块不低于 95%。
- 前端：Vitest 全部通过，总行覆盖率不低于 80%；Playwright 桌面 `1440x1024` 与手机 `390x844` 核心流程通过。
- 内容：来源清单覆盖率 100%，ID/前置关系/概念引用有效，参考答案与隐藏测试全部运行成功，无占位文本。
- 安全：命令必须以参数数组启动，不拼接 shell 字符串；超时、输出上限和进程树清理有真实子进程测试。
- 数据：迁移前备份、日/周保留、校验和、失败导入回滚均有集成测试。
- UI：无页面级横向溢出，键盘与触摸可完成主流程；支持聚焦提示、语义标签、对比度与减少动态效果。
- 每个 UI 任务将截图写入 `docs/audit/task-<NN>/` 并随任务提交。

---

## Phase A — 工具链与工程骨架

### Task 1: D 盘工具链引导与健康检查

**Files:** `.gitignore`、`scripts/bootstrap-python.ps1`、`scripts/bootstrap-dotnet.ps1`、`scripts/bootstrap-msys2.ps1`、`scripts/verify-toolchain.ps1`、`docs/setup/windows-d-drive.md`、`tests/scripts/verify-toolchain.Tests.ps1`

**Produces:** 可重复运行且不覆盖已有安装的 D 盘安装脚本；JSON 健康报告协议 `{name,path,version,healthy,detail}`。

- [ ] 先写脚本测试，证明 C 盘目标、Codex/Workbuddy Python 路径和缺失版本会被拒绝。
- [ ] 实现 Python `D:\DevTools\python`、.NET `D:\DevTools\dotnet`、MSYS2 `D:\DevTools\msys64` 的固定目标和下载校验和参数；Java 只检测现有 JDK 17。
- [ ] 所有 npm/pnpm、pip、NuGet、MSYS2 缓存默认指向 `D:\DevTools\cache`；脚本不得改系统级默认路径。
- [ ] 运行 `Invoke-Pester tests/scripts/verify-toolchain.Tests.ps1`；如未安装 Pester，使用文档中的 Windows PowerShell 5.1 安装步骤并先申请授权。
- [ ] 提交 `build: add D-drive toolchain bootstrap`，报告脚本测试结果后停止。

### Task 2: 安装并锁定四语言工具链

**Files:** `docs/setup/toolchain-lock.json`、`docs/setup/toolchain-verification.md`

**Consumes:** Task 1 脚本。**Produces:** Python、Java、.NET、g++ 的可执行路径与版本证据。

- [ ] 取得授权后运行三个安装脚本；现有健康安装不得重复下载。
- [ ] 用 `scripts/verify-toolchain.ps1 -Output docs/setup/toolchain-lock.json` 验证 Python 3.13.x、Java 17.x、.NET SDK 10.x、g++ 可编译 C++20。
- [ ] 分别执行四个 Hello World，并证明输出文件与临时文件都在 D 盘。
- [ ] 在验证文档记录安装大小、路径、版本、重装命令和清理缓存方式，不删除用户现有文件。
- [ ] 提交 `build: verify local language toolchains`，报告版本证据后停止。

### Task 3: 工作区、锁文件与统一检查命令

**Files:** `package.json`、`pnpm-workspace.yaml`、`pnpm-lock.yaml`、`.editorconfig`、`.env.example`、`apps/api/pyproject.toml`、`apps/api/requirements.lock`、`apps/web/package.json`、`scripts/bootstrap-project.ps1`、`scripts/check.ps1`

- [ ] 先写 `scripts/check.ps1 -Mode Smoke` 的失败断言：缺少 `.venv`、Node 版本错误或锁文件漂移必须非零退出。
- [ ] 用 D 盘 Python 创建 `.venv`；后端约束 FastAPI 0.141.1、SQLAlchemy 2.0.x、Alembic 1.x、pytest、pytest-cov、httpx、PyYAML、markdown-it-py、psutil；生成精确 `requirements.lock`。
- [ ] 创建 pnpm workspace，并精确锁定顶部 Tech Stack 中的前端核心版本；缓存使用 `.tool-cache` 或 `D:\DevTools\cache`。
- [ ] 根命令提供 `pnpm check:api`、`check:web`、`check:e2e`、`check:content` 与 `check`，初始 smoke 可运行。
- [ ] 运行 `scripts/bootstrap-project.ps1` 和 `scripts/check.ps1 -Mode Smoke`。
- [ ] 提交 `build: scaffold Hard workspace` 后停止。

### Task 4: FastAPI 基础、配置与错误协议

**Files:** `apps/api/src/hard_api/main.py`、`core/config.py`、`core/errors.py`、`core/logging.py`、`api/health.py`、`apps/api/tests/test_health.py`、`test_errors.py`

- [ ] 先写测试：`/api/v1/health/live`、`ready`、未知路由错误体、请求 ID；使用 FastAPI `TestClient` lifespan 上下文。
- [ ] 实现应用工厂，配置路径全部从项目根解析并拒绝 C 盘数据目录；生产响应不返回堆栈。
- [ ] `ready` 分别报告数据库、内容和四 runner 状态，单 runner 缺失不导致 API 崩溃。
- [ ] 运行 `.venv\Scripts\python.exe -m pytest apps/api/tests/test_health.py apps/api/tests/test_errors.py -q`。
- [ ] 提交 `feat(api): establish application contracts` 后停止。

### Task 5: Vue 外壳、路由与 OpenAPI 类型同步

**Files:** `apps/web/index.html`、`vite.config.ts`、`src/main.ts`、`src/App.vue`、`src/app/router.ts`、`src/app/AppShell.vue`、`src/api/client.ts`、`scripts/export-openapi.ps1`、`packages/contracts/openapi.json`、`apps/web/tests/app-shell.spec.ts`

- [ ] 先写组件测试：八个主目的地可访问、未知路由回主页、API 错误体被保留。
- [ ] 从 FastAPI 应用离线导出 OpenAPI 并生成 TypeScript 类型；不得手写一套重复响应类型。
- [ ] 建立 `/`、`/course/:language`、`/lesson/:lessonId`、`/review`、`/search`、`/compare`、`/growth`、`/settings` 路由。
- [ ] 增加检查，OpenAPI 重新生成后有 diff 时 `pnpm check` 失败。
- [ ] 运行前端单测、TypeScript 检查和 OpenAPI 漂移检查。
- [ ] 提交 `feat(web): add typed application shell` 后停止。

---

## Phase B — 内容、数据与学习引擎

### Task 6: 课程文件规范与验证器

**Files:** `tools/content/schema.py`、`validate.py`、`report.py`、`apps/api/src/hard_api/content/models.py`、`parser.py`、`content/schema/*.json`、`tools/content/tests/test_validate.py`、`content/concepts.yaml`

- [ ] 先为非法 ID、重复题号、循环前置、未知概念、泄露隐藏答案、缺少来源、空正文和路径逃逸写失败测试。
- [ ] 固定 `course.yaml`、Markdown front matter、exercise JSON 与 `concepts.yaml` 的 schema；参考答案和隐藏测试只能由后端读取。
- [ ] 验证器输出机器可读 JSON 和中文摘要，任何隔离内容都非零退出。
- [ ] 建立跨语言概念初始词表：变量、类型、控制流、函数、集合、类、继承、多态、异常、泛型、IO、并发、内存。
- [ ] 运行 `pytest tools/content/tests -q`。
- [ ] 提交 `feat(content): define validated course format` 后停止。

### Task 7: 菜鸟教程来源快照与完整性基线

**Files:** `tools/content/snapshot_sources.py`、`check_originality.py`、`tools/content/tests/test_sources.py`、`content/sources.yaml`、`docs/content/source-policy.md`、`docs/content/source-coverage.json`

**Source indexes:** Python `https://www.runoob.com/python3/python3-tutorial.html`；Java `https://www.runoob.com/java/java-tutorial.html`；C# `https://www.runoob.com/csharp/csharp-tutorial.html`；C++ `https://www.runoob.com/cplusplus/cpp-tutorial.html`。

- [ ] 先用静态 HTML fixture 测试：只采集课程导航中的标题和 URL、去重、保持顺序、拒绝跨域和未分类条目。
- [ ] 经授权读取四个目录页，仅保存标题、URL、目录分组、`snapshot_date: 2026-08-23`、模块 ID 和内容类型；不保存正文、图片、评论或广告。
- [ ] 将每个来源条目精确归入本计划列出的一个内容模块；零归属或多归属均失败。
- [ ] 原创性检查临时读取源页，忽略代码后标记连续 16 个以上相同中文字符；临时正文不得提交。
- [ ] 生成基线报告，断言四门课目录条目总数均大于零且 `assigned == expected`。
- [ ] 提交 `docs(content): freeze tutorial source manifest` 后停止。

### Task 8: SQLite 模型、FTS5 与可恢复迁移

**Files:** `apps/api/src/hard_api/db/base.py`、`session.py`、`models.py`、`migrations.py`、`apps/api/alembic.ini`、`apps/api/alembic/versions/0001_initial.py`、`apps/api/tests/db/test_migrations.py`、`test_transactions.py`

- [ ] 先写临时数据库测试：WAL/外键开启、全部表创建、FTS5 可查询、写事务失败回滚、迁移失败保留旧库。
- [ ] 建表：settings、daily_goals、lesson_progress、attempts、submissions、mastery_snapshots、review_items、notes、favorites、achievements、backup_records、content_versions、idempotency_keys。
- [ ] 迁移前调用备份接口；无备份成功不得迁移。测试中注入失败证明恢复。
- [ ] 禁止 SQLite 连接跨线程泄露；每次请求或后台任务拥有明确事务边界。
- [ ] 运行数据库测试并生成临时迁移往返证据。
- [ ] 提交 `feat(db): add recoverable learning database` 后停止。

### Task 9: 课程目录、课时读取与内容版本

**Files:** `apps/api/src/hard_api/content/repository.py`、`service.py`、`apps/api/src/hard_api/api/content.py`、`apps/api/tests/content/test_catalog.py`、`test_lesson.py`、`content/python/course.yaml`、`content/python/python-foundations/**`（只允许最小测试 fixture）

- [ ] 先写 API 测试：课程目录、模块顺序、前置状态、课时 Markdown 渲染、来源链接、非法课时、内容版本变更。
- [ ] 实现启动时全量验证、按稳定 ID 索引和隔离错误报告；不得在请求期间抓取网络。
- [ ] 对客户端只返回公开题面、starter code 和 visible tests；隐藏测试与答案不得出现在 OpenAPI 响应。
- [ ] 使用最小 Python Hello World fixture 证明完整读取链路，明确标记 `fixture_only`，Task 22 必须替换。
- [ ] 提交 `feat(content): serve versioned lesson catalog` 后停止。

### Task 10: 进度、目标、笔记、收藏与全文搜索

**Files:** `apps/api/src/hard_api/learning/progress.py`、`goals.py`、`notes.py`、`apps/api/src/hard_api/search/service.py`、`apps/api/src/hard_api/api/progress.py`、`search.py`、`apps/api/tests/learning/test_progress.py`、`test_goals.py`、`apps/api/tests/search/test_search.py`

- [ ] 先测试阅读位置单调更新、时长与任务目标、笔记/收藏增删改、FTS 课程与笔记命中、中文空查询与特殊符号。
- [ ] 所有写接口接收幂等键；同键重试不得重复计时或创建重复记录。
- [ ] 搜索结果返回来源类型、语言、课时、片段和跳转定位，搜索不到不是错误。
- [ ] 进度接口一次返回主页需要的今日目标、连续天数和继续学习位置。
- [ ] 提交 `feat(learning): track progress notes and search` 后停止。

### Task 11: 评分、掌握度、解锁与分级测试

**Files:** `apps/api/src/hard_api/learning/scoring.py`、`mastery.py`、`unlocking.py`、`apps/api/src/hard_api/api/assessment.py`、`apps/api/tests/learning/test_scoring.py`、`test_mastery.py`、`test_unlocking.py`

- [ ] 先以参数化测试固定权重 30/40/20/10、未作答为零、课时 70 通过、模块/课程 85 掌握、分级 85 解锁。
- [ ] 固定提示惩罚：轻提示当前题得分乘 0.85，强提示乘 0.60，揭示答案为 0；重试可改善掌握度但不重复给经验。
- [ ] 评分、尝试、解锁、经验候选事件在一个事务内更新；并发重复提交仍只生成一份结果。
- [ ] 分级跳过标记为 `validated`，不授普通完成经验。
- [ ] 提交 `feat(learning): calculate mastery and unlocks` 后停止。

### Task 12: 间隔复习、经验成就、弱点与代码成长

**Files:** `apps/api/src/hard_api/learning/review.py`、`experience.py`、`achievements.py`、`weakness.py`、`history.py`、`apps/api/src/hard_api/api/growth.py`、`review.py`、`apps/api/tests/learning/test_review.py`、`test_experience.py`、`test_weakness.py`、`test_history.py`

- [ ] 先固定 1/3/7/14/30/60 日间隔：>=80 前进、60–79 保持、<60 后退；用注入时钟测试跨日，不依赖系统当天。
- [ ] 首次完成事件的经验具有唯一键；重复、并发和导入重放均不能刷经验。
- [ ] 弱点排序只使用近期错误、提示、编译分类、隐藏测试与复习逾期，并返回已有学习资源。
- [ ] 保存每次源码、规范化结果、得分、时间和相邻 unified diff；禁止执行或渲染提交代码为 HTML。
- [ ] 实现等级、连续学习、路线完成和可测试的初始徽章规则。
- [ ] 提交 `feat(learning): add review and growth analytics` 后停止。

---

## Phase C — 代码执行与完整 Python 纵向闭环

### Task 13: 统一 runner 管理器与安全边界

**Files:** `apps/api/src/hard_api/runners/contracts.py`、`manager.py`、`limits.py`、`processes.py`、`workspace.py`、`apps/api/src/hard_api/api/runners.py`、`apps/api/tests/runners/test_manager.py`、`test_processes.py`、`test_workspace.py`

- [ ] 先测试成功、排队、取消、超时、输出溢出、源码过大、并发上限、路径逃逸、缺工具、子进程树清理。
- [ ] 固定输入 `Submission(language, files, stdin, visible_tests, hidden_tests, idempotency_key)` 和输出 `RunResult(status, compile, tests, stdout, stderr, diagnostics, duration_ms)`。
- [ ] 只允许适配器提供的可执行路径和参数数组；用户内容不得进入 shell、工作目录名或环境 PATH。
- [ ] 默认限制：源码总计 128 KiB、编译 15 秒、运行 5 秒、输出 64 KiB、并发 2；超限结果使用稳定错误码。
- [ ] 用真实孙进程证明 Windows Job Object 或等价进程树清理有效；测试后 `runner-work` 为空。
- [ ] 提交 `feat(runner): add bounded execution manager` 后停止。

### Task 14: Python 3.13 runner 适配器

**Files:** `apps/api/src/hard_api/runners/python.py`、`diagnostics/python.py`、`apps/api/tests/runners/test_python.py`、`fixtures/python/**`

- [ ] 先写真实解释执行测试：成功、语法错行列、断言失败、stdin、超时、输出上限、import 禁止模块、缺工具。
- [ ] 仅调用 `D:\DevTools\python\python.exe -I`；设置独立临时目录并移除用户 site、代理和不必要环境变量。
- [ ] 固定允许标准库策略；阻止 `subprocess`、`socket`、`ctypes` 等高风险导入，但在产品文档明确这不是恶意代码沙箱。
- [ ] 将 traceback 归一为中文类别，同时保留原始 Python 消息；隐藏测试代码不得返回客户端。
- [ ] 提交 `feat(runner): execute Python exercises` 后停止。

### Task 15: 深色设计系统、响应式外壳与可访问导航

**Files:** `apps/web/src/design/tokens.css`、`base.css`、`motion.css`、`src/app/AppShell.vue`、`PrimaryNav.vue`、`MobileNav.vue`、`apps/web/tests/design-system.spec.ts`、`tests/e2e/navigation.spec.ts`、`docs/audit/task-15/**`

- [ ] 先写桌面/手机导航与减少动态效果测试；断言页面无横向溢出。
- [ ] 从视觉目标提取深海军蓝、紫色主动作、青/琥珀/红状态色、字号、间距、圆角、阴影和动效 token；禁止散落魔法色值。
- [ ] 八个目的地使用语义导航、可见焦点、44px 触摸目标和当前页标记。
- [ ] 截取 `1440x1024` 与 `390x844` 外壳截图。
- [ ] 提交 `feat(web): establish responsive Hard design system` 后停止。

### Task 16: 桌面轨道知识星图与手机纵向路线

**Files:** `apps/web/src/features/map/KnowledgeMapPage.vue`、`OrbitalMap.vue`、`MobileRouteMap.vue`、`MapWorld.vue`、`map-layout.ts`、`map.store.ts`、`apps/web/tests/map/*.spec.ts`、`tests/e2e/map.spec.ts`、`docs/audit/task-16/**`

- [ ] 先测试四语言均可进入、中心继续学习动作、未开始/学习中/掌握状态，以及断点切换为纵向路线。
- [ ] 桌面以当前课时为中心、四语言世界为轨道节点；进度、今日目标、等级与复习数位于边缘信息区。
- [ ] 手机不缩小桌面画布，改为纵向节点路线；不得依赖 hover 才能操作。
- [ ] 动效仅使用 transform/opacity，并遵守 `prefers-reduced-motion`。
- [ ] 对视觉目标做 1440x1024 截图对照，并提交手机截图。
- [ ] 提交 `feat(web): build adaptive knowledge map` 后停止。

### Task 17: 课程阅读工作区

**Files:** `apps/web/src/features/course/CoursePage.vue`、`LessonPage.vue`、`LessonNav.vue`、`LessonContent.vue`、`LessonTools.vue`、`course.store.ts`、`apps/web/tests/course/*.spec.ts`、`tests/e2e/lesson.spec.ts`、`docs/audit/task-17/**`

- [ ] 先测试模块导航、前置锁定、来源跳转、阅读位置、收藏和笔记保存/失败重试。
- [ ] Markdown 使用白名单渲染并对代码高亮；禁止原始 HTML、脚本 URL 和未经允许的外链资源。
- [ ] 桌面保留章节侧栏；手机使用可关闭目录，正文与操作不横向溢出。
- [ ] 自动保存使用幂等键，离线失败保留本地草稿并明确显示状态。
- [ ] 提交 `feat(web): add lesson reading workspace` 后停止。

### Task 18: 知识题、Monaco 代码题与结果反馈

**Files:** `apps/web/src/features/assessment/AssessmentPage.vue`、`KnowledgeQuestion.vue`、`CodeExercise.vue`、`CodeWorkspace.vue`、`RunResult.vue`、`assessment.store.ts`、`editor-drafts.ts`、`apps/web/tests/assessment/*.spec.ts`、`tests/e2e/assessment.spec.ts`、`docs/audit/task-18/**`

- [ ] 先测试答题、提示惩罚、重试、运行/取消、编译错误、隐藏测试结果、重复提交和草稿恢复。
- [ ] Monaco 按语言配置；桌面编辑器/输出分栏，手机竖屏切换面板、横屏可双栏，保留普通 textarea 降级。
- [ ] 运行状态可取消；只显示允许的可见失败与规范化诊断，不显示参考答案或隐藏测试。
- [ ] 分数更新后同步主页与路线状态；同一幂等键网络重试不重复计分。
- [ ] 提交 `feat(web): deliver scored coding workspace` 后停止。

### Task 19: 复习、搜索、成长、对照与设置页面

**Files:** `apps/web/src/features/review/**`、`search/**`、`growth/**`、`compare/**`、`settings/**`、`apps/web/tests/{review,search,growth,compare,settings}/**`、`tests/e2e/secondary-flows.spec.ts`、`docs/audit/task-19/**`

- [ ] 先测试复习队列与普通错题分离、搜索定位、代码 diff 转义、弱点链接、每日目标和缺工具提示。
- [ ] 成长页展示等级、经验、连续天数、徽章、掌握度、热力图和提交历史；不虚构无数据图表。
- [ ] 对照页按 concept ID 展示四语言槽位，缺失内容明确标记而不猜测。
- [ ] 设置页显示 D 盘工具状态、数据路径、手机访问风险、目标、备份/导入/导出入口。
- [ ] 提交 `feat(web): expose review search and growth tools` 后停止。

### Task 20: 自动备份、手动导出与失败回滚

**Files:** `apps/api/src/hard_api/backup/service.py`、`retention.py`、`archive.py`、`apps/api/src/hard_api/api/backup.py`、`apps/api/tests/backup/test_backup.py`、`test_import.py`、`test_retention.py`、`apps/web/src/features/settings/DataManagement.vue`、`tests/e2e/backup.spec.ts`

- [ ] 先测试 WAL checkpoint、当日首次成功写入后备份、7 日 + 4 周保留、迁移前快照、校验和错误、版本不兼容和导入失败回滚。
- [ ] 导出包只含数据库、设置清单、内容版本和 SHA-256 清单；拒绝绝对路径、重复归档项和 zip-slip。
- [ ] 导入前自动快照；验证全部成功后原子替换，任一步失败恢复旧库。
- [ ] UI 明确同盘备份不防 D 盘损坏，并建议手动复制导出包到其他磁盘。
- [ ] 提交 `feat(backup): add verified local recovery` 后停止。

### Task 21: 私有 LAN 模式与断线草稿

**Files:** `apps/api/src/hard_api/core/network.py`、`apps/api/src/hard_api/api/lan.py`、`apps/api/tests/test_lan.py`、`apps/web/src/features/settings/LanAccess.vue`、`apps/web/src/app/offline-drafts.ts`、`apps/web/tests/offline-drafts.spec.ts`、`tests/e2e/lan.spec.ts`、`docs/setup/phone-access.md`

- [ ] 先测试默认只绑定 loopback、只允许私有接口、拒绝公网/隧道配置、每次 LAN 启动需要确认、断线草稿幂等恢复。
- [ ] 显示局域网 URL 与二维码；不创建端口转发、公共隧道或全网防火墙规则。
- [ ] 防火墙命令只生成预览；实际添加私有网络规则必须单独取得用户批准并记录撤销命令。
- [ ] 手机断线时保存阅读位置、答案、笔记和代码草稿，重连仅提交未确认项。
- [ ] 提交 `feat(lan): support warned private-network access` 后停止。

---

## Phase D — 课程内容批次统一合同

课程内容 Tasks 22–31、34–40、42–46、48–54 均受以下合同约束。该合同是任务验收条件，不得删减：

- 只修改该任务列出的 `content/<language>/<module>/**`、对应 `content/<language>/course.yaml`、`content/concepts.yaml`（仅新增确需 concept）和对应快照测试。
- `content/sources.yaml` 中归属该模块的每个来源条目必须恰好对应一个 Hard 课时或明确的 examples/quiz/resource 结构项，模块覆盖为 100%。
- 每个普通课时至少有 2 个目标、原创中文解释、2 个原创示例、3 道原创知识题和 1 道可执行代码题；确实不可执行的环境/资源页可用情景题替代代码题，但须在元数据写出原因。
- 每模块必须有一项综合挑战；课程最后模块还必须有路线结业挑战和分级测试覆盖。
- 不复制来源长段落、图片、评论或原测验题；保留来源链接。原创性检查出现连续长匹配必须重写或作为短引用明确标注。
- starter code 可见；参考解与隐藏测试仅存 exercise JSON 的 server 区，必须通过真实对应 runner。
- 完成命令固定为：

```powershell
.venv\Scripts\python.exe tools\content\validate.py --language <language> --module <module> --require-complete
.venv\Scripts\python.exe tools\content\check_originality.py --language <language> --module <module>
.venv\Scripts\python.exe -m pytest tools\content\tests apps\api\tests\content -q
.venv\Scripts\python.exe tools\content\report.py --language <language> --module <module> --json docs\audit\task-<NN>\coverage.json
```

- 报告 expected/implemented/validated/reference_solutions_passed 四项相等，提交一份人工抽查记录和覆盖 JSON，然后使用任务给出的提交消息并停止。

### Task 22: Python 入门与环境

**Module/path:** `python-foundations` / `content/python/python-foundations/**`

**Sources:** 教程、简介、环境搭建、PyCharm、VS Code、解释器、虚拟环境、pip、有用的资源。

- [ ] 删除 Task 9 的 `fixture_only` 内容并按内容合同完成本模块。
- [ ] 运行内容合同四条命令和 Python runner 冒烟测试。
- [ ] 提交 `content(python): add foundations module` 后停止。

### Task 23: Python 语法与核心类型

**Module/path:** `python-core-types` / `content/python/python-core-types/**`

**Sources:** 基础语法、注释、基本数据类型、数据类型转换、运算符、Number、字符串。

- [ ] 按内容合同完成全部来源和模块挑战。
- [ ] 提交 `content(python): add core types module` 后停止。

### Task 24: Python 集合与控制流

**Module/path:** `python-flow-collections` / `content/python/python-flow-collections/**`

**Sources:** 列表、元组、字典、集合、条件控制、循环语句、编程第一步、推导式、数据结构、for 循环、while 循环。

- [ ] 按内容合同完成全部来源和模块挑战。
- [ ] 提交 `content(python): add flow and collections module` 后停止。

### Task 25: Python 函数、迭代与作用域

**Module/path:** `python-functions-iteration` / `content/python/python-functions-iteration/**`

**Sources:** 迭代器与生成器、with、函数、lambda、装饰器、`__name__`、命名空间/作用域、类型注解。

- [ ] 按内容合同完成全部来源和模块挑战。
- [ ] 提交 `content(python): add functions and iteration module` 后停止。

### Task 26: Python 模块、IO、异常与面向对象

**Module/path:** `python-modules-io-oop` / `content/python/python-modules-io-oop/**`

**Sources:** 模块、输入和输出、File、OS、错误和异常、面向对象。

- [ ] 按内容合同完成全部来源和模块挑战；文件题仅访问 runner 临时目录。
- [ ] 提交 `content(python): add modules io and oop module` 后停止。

### Task 27: Python 标准库与数据格式

**Module/path:** `python-stdlib-data` / `content/python/python-stdlib-data/**`

**Sources:** 标准库概览、内置函数、JSON、XML、日期和时间、datetime、math、random、statistics、operator、re/正则表达式、sys、Pickle、StringIO、queue、logging、csv、hashlib。

- [ ] 按内容合同完成全部来源和模块挑战。
- [ ] 提交 `content(python): add standard library module` 后停止。

### Task 28: Python 并发与网络

**Module/path:** `python-concurrency-network` / `content/python/python-concurrency-network/**`

**Sources:** 网络编程、SMTP、urllib、requests、subprocess、多线程、threading、asyncio。

- [ ] 按内容合同完成；涉及网络/进程的题使用 mock 或纯函数判题，不为 runner 放开危险能力。
- [ ] 提交 `content(python): add concurrency and network module` 后停止。

### Task 29: Python 数据库与部署专题

**Module/path:** `python-database-deployment` / `content/python/python-database-deployment/**`

**Sources:** CGI、MySQL(mysql-connector)、MySQL(PyMySQL)、MongoDB、uWSGI。

- [ ] 按内容合同完成；不要求安装数据库服务，代码题使用 fixture/mock 或 SQL/配置静态检查。
- [ ] 提交 `content(python): add database and deployment module` 后停止。

### Task 30: Python 自动化、UI 与 Web 工具

**Module/path:** `python-automation-ui-web` / `content/python/python-automation-ui-web/**`

**Sources:** pyecharts、selenium、爬虫、Scrapy、Markdown、PyQt。

- [ ] 按内容合同完成；不下载浏览器驱动或打开 GUI，题目验证核心 API 与思路。
- [ ] 提交 `content(python): add automation and ui module` 后停止。

### Task 31: Python 新兴专题、实例、测验与结业

**Module/path:** `python-capstone` / `content/python/python-capstone/**`

**Sources:** OpenAI、AI 绘画、量化、Python3 实例、Python 测验，以及来源清单中尚未归入前述模块的 Python 目录项。

- [ ] 按内容合同完成；OpenAI/AI/量化内容不产生在线依赖和真实交易行为。
- [ ] 添加覆盖前十模块的分级测试与结业挑战，真实 Python runner 全部通过。
- [ ] 断言 Python `unassigned == 0` 且路线覆盖 100%。
- [ ] 提交 `content(python): complete Python route` 后停止。

### Task 32: Python 纵向闭环里程碑审计

**Files:** `tests/e2e/python-journey.spec.ts`、`docs/audit/python-milestone/**`、`docs/setup/python-user-guide.md`

- [ ] 用空白数据库完成：主页进入 Python、读课、知识题、代码题、得分、错题复习、搜索、笔记、成长、备份恢复。
- [ ] 同一旅程在桌面和手机 viewport 运行；手机真实局域网冒烟若需防火墙更改须先获批准。
- [ ] 运行全量后端、前端、内容、E2E；记录覆盖率、总课时/题目/挑战数、runner 健康与截图。
- [ ] 失败必须回到对应当前能力修复，不得降低断言或覆盖阈值。
- [ ] 提交 `test: certify Python learning milestone` 后停止。

---

## Phase E — Java 路线

### Task 33: Java 17 runner 适配器

**Files:** `apps/api/src/hard_api/runners/java.py`、`diagnostics/java.py`、`apps/api/tests/runners/test_java.py`、`fixtures/java/**`

- [ ] 先测试编译/运行成功、public class 文件名、编译诊断、测试失败、stdin、超时、输出限制、进程清理与缺工具。
- [ ] 固定调用健康检查锁定的 `javac`/`java` 17 路径，类路径仅包含临时目录和受控测试 harness。
- [ ] 禁止用户提供 JVM 参数、classpath 或文件路径；隐藏测试不返回。
- [ ] 提交 `feat(runner): execute Java exercises` 后停止。

### Task 34: Java 入门与语言基础

**Module/path:** `java-foundations` / `content/java/java-foundations/**`

**Sources:** 教程、简介、开发环境、基础语法、注释、对象和类、基本数据类型、变量类型、变量命名规则、修饰符、运算符、循环、条件、switch。

- [ ] 按内容合同完成并用 Java runner 验证。
- [ ] 提交 `content(java): add foundations module` 后停止。

### Task 35: Java 核心 API 与方法

**Module/path:** `java-core-api` / `content/java/java-core-api/**`

**Sources:** Number & Math、Character、String、StringBuffer、数组、日期时间、正则、方法、构造方法、Scanner。

- [ ] 按内容合同完成。
- [ ] 提交 `content(java): add core api module` 后停止。

### Task 36: Java IO、异常与面向对象

**Module/path:** `java-oop-io` / `content/java/java-oop-io/**`

**Sources:** Stream/File/IO、异常处理、继承、Override/Overload、多态、抽象类、封装、接口、枚举、package。

- [ ] 按内容合同完成；文件题限制在临时目录。
- [ ] 提交 `content(java): add oop and io module` 后停止。

### Task 37: Java 集合、泛型与反射

**Module/path:** `java-collections-generics` / `content/java/java-collections-generics/**`

**Sources:** 反射、数据结构、集合框架、ArrayList、LinkedList、HashSet、HashMap、Iterator、Object、NIO Files、泛型。

- [ ] 按内容合同完成。
- [ ] 提交 `content(java): add collections and generics module` 后停止。

### Task 38: Java 序列化、网络与并发

**Module/path:** `java-network-concurrency` / `content/java/java-network-concurrency/**`

**Sources:** 序列化、网络编程、发送邮件、多线程、文档注释、Applet。

- [ ] 按内容合同完成；网络与邮件题使用 mock；Applet 作为历史知识标记，不要求浏览器运行。
- [ ] 提交 `content(java): add network and concurrency module` 后停止。

### Task 39: Java 现代特性与生态

**Module/path:** `java-modern-ecosystem` / `content/java/java-modern-ecosystem/**`

**Sources:** Java 8 新特性、Java 9 新特性、MySQL 连接、常用类库。

- [ ] 按内容合同完成；数据库题不要求本地 MySQL 服务。
- [ ] 提交 `content(java): add modern ecosystem module` 后停止。

### Task 40: Java 实例、测验与结业

**Module/path:** `java-capstone` / `content/java/java-capstone/**`

**Sources:** Java 实例、Java 测验，以及来源清单中尚未归入前述模块的 Java 目录项。

- [ ] 按内容合同完成，添加全路线分级测试与结业挑战。
- [ ] 断言 Java `unassigned == 0`、覆盖 100%，运行 Java 路线 E2E。
- [ ] 提交 `content(java): complete Java route` 后停止。

---

## Phase F — C# 路线

**正式起始基线：** `6246473bf565be308c1505921ec1219beb30803c`

**阶段状态：** Hard 当前范围为单用户、本地、个人编程学习平台，仅执行用户本人编写和信任的学习代码。`Task 41-RMT-PRE = CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE`；E2B/Remote Runner/生产级 Sandbox 路线停止且不再阻塞 Phase F。`Task 41 = READY FOR DISPATCH`，Task 42–46 继续等待 Task 41、独立审计和前端门禁；Phase G 为 `FROZEN`。

**唯一允许的执行顺序：**

```text
历史生产级 Sandbox 研究（保留证据，不再是当前前置门禁）
→ Task 41-RMT-PRE（CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE）
→ Task 41 — C# Runner / Trusted Local Learning Environment（READY FOR DISPATCH）
→ Task 41 独立审计
→ 前端 C# 编辑器兼容门禁
→ 前端独立验收
→ Task 42
→ Task 43
→ Task 44
→ Task 45
→ Task 46
→ C# 内容统一验收
→ Phase F 完整 E2E
→ Phase F 最终统一审计
```

任一当前门禁出现 P0/P1、前序验证失败、公共合同缺口、未授权文件修改需求、安装/下载/提权需求或冻结架构变更需求时，立即停止后续步骤。不得并行或越序。Task 41 必须明确标注 `TRUSTED_LOCAL_LEARNING_ONLY`，不得宣传或暗示具备 hostile/untrusted code sandbox 能力。

### Task 41-PRE: .NET 10 Runner 安全可行性门禁

**性质：** 独立 PRE-GATE，只验证安全可行性，不实现 C# Runner，不修改产品源码。

**起始基线：** `6246473bf565be308c1505921ec1219beb30803c`

**允许产物：** 只读审计记录、一次性安全验证脚本/测试夹具和可复核证据；正式任务包必须单独限定允许路径。不得创建或修改 `apps/api/src/**`、`apps/web/src/**`、`content/**` 等产品实现。

- [ ] 在当前 Windows 权限、当前 Hard Runner 基础设施、不安装额外沙箱、不提升管理员权限的条件下，证明存在可靠的 OS / process / sandbox 层文件访问隔离。
- [ ] 证明 C# 用户进程允许 workspace 内相对文件读写。
- [ ] 证明用户进程拒绝访问 `C:\Windows\win.ini`、任意绝对路径和 `..` 规范化逃逸。
- [ ] 证明 `Path.Combine` / `Path.GetFullPath`、字符串拼接、Base64/编码构造路径、`System.IO` 全限定 API、Reflection、Delegate、Dynamic 等方式均不能绕过隔离。
- [ ] 禁止以源码关键词扫描、API 名称黑名单或编码特征扫描冒充文件隔离。
- [ ] 保存环境、机制、测试矩阵、原始输出、失败关闭行为和可复核结论。

**结论枚举只能是：** `PASS` 或 `BLOCKED`。

- `PASS`：所有允许/拒绝场景均由可靠的 OS / process / sandbox 层机制强制满足，且证据可复核；随后才可下发 Task 41。
- `BLOCKED`：现有基础设施无法提供 hostile/untrusted code 隔离。该结论继续有效，但 2026-08-30 的 trusted-local 产品范围裁决使其不再阻塞当前 Task 41；未来多人在线/不可信执行仍受此结论约束。

**2026-08-29 正式结果：`BLOCKED`。**

外部 Agent 在 Windows 普通用户权限、固定 .NET SDK `10.0.100`、Hard 等价进程启动条件下完成验证：workspace 相对读写为 `ALLOW`；15 个应拒绝场景为 `0/15 DENY`。`C:\Windows\win.ini`、`..` 逃逸、`Path.GetFullPath`、字符串/`char[]`/Base64 构造路径、`System.IO` 全限定 API、`FileStream`/`FileInfo`/`Directory`、Reflection/Delegate/InvokeMember 均可访问或绕过。

现有 host-side workspace path validation、cwd/env 控制、timeout、output limit 和 process-tree cleanup 无法形成 .NET 子进程的文件系统权限边界。本轮未修改正式项目文件或 `.git`，未安装软件，未创建 `CSharpRunner`，未产生 commit。

当前状态：**Task 41-PRE / Task 41-SBX / Tier 3-PRE 历史结果保留；Task 41-RMT-PRE = CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE；E2B/Remote Runner 当前停止；Task 41 = READY FOR DISPATCH；Task 42–46 等待 Task 41 与前端门禁；Phase G = FROZEN。**

### Phase F 安全决策项: Untrusted Runner filesystem isolation architecture

**主责：** 架构与管理 Session；策划总控参与必要的合同裁决。

**状态：** Tier 1 / Tier 2 已完成验证但均无可用候选；`Task 41-SBX = BLOCKED`，转入 Tier 3 架构决策。

**已验证的 Tier 1 / Tier 2 候选架构（当前主机不可作为通过方案）：**

```text
Hard API / Runner Manager
→ local sandbox broker
→ AppContainer / LPAC / Windows Sandbox API
→ 最小 ACL / capability
→ dotnet build/run inside temporary workspace
```

真正的安全边界必须来自 Windows OS access check。`cwd`、`TEMP/TMP`、`PATH`、host-side path validation、Job Object、源码扫描、API 黑名单、字符串/Base64 特征扫描只能作为辅助控制，不能作为文件系统隔离依据。

**实现路径优先级：**

1. Tier 1：只读探测当前主机是否支持 Windows 官方 Create Process In Sandbox / `Experimental_CreateProcessInSandbox` 能力；支持时优先构造最小 AppContainer sandbox prototype。
2. Tier 2：Classic AppContainer / LPAC + local sandbox broker + 最小 ACL 授权。
3. Tier 3：本机 Hyper-V-isolated Windows Container 因 `Tier 3-PRE = HOST_UNSUPPORTED_EDITION` 停止；Remote Runner 随后也因 trusted-local 当前范围取消。两者均只保留为未来多人在线版本强化参考。

- [ ] 比较并验证独立/远程隔离 Runner（Container / VM / sandbox service）。
- [ ] 比较并验证 Windows AppContainer。
- [ ] 比较并验证其他能够真正强制 workspace-only 文件访问的 OS 级方案。
- [ ] 每个候选方案必须说明当前 Windows 与 .NET 10.0.100 可行性、强制边界、所需权限/安装/下载/网络变化、生命周期、清理、运维成本、失败关闭方式和同等级 PRE-GATE 复测方法。
- [ ] Job Object 单独、cwd/TEMP/PATH、源码扫描/API 黑名单均不得作为文件系统隔离方案。
- [ ] “低权限独立用户 + workspace ACL”只有在实验证明所有 workspace 外路径均不可访问后才可候选；普通低权限用户仍可读取 `C:\Windows` 等公共可读文件，不能凭推断通过。
- [x] 形成推荐方案、拒绝方案及证据缺口；涉及安装、下载、管理员权限、系统配置或公共合同变化时停止并请求用户授权。

上述生产级隔离研究结论继续作为历史证据保留。根据 2026-08-30 产品范围裁决，当前 Phase F 不以 hostile/untrusted code execution 为验收目标，独立 Sandbox / Remote Runner 不再是 Task 41 前置条件；如未来开放多人在线代码执行，必须重新启用独立安全项目。

### Task 41-SBX: Windows Sandbox / AppContainer Prototype Gate

**性质：** 独立安全原型门禁；不是 CSharpRunner 实现任务，不修改业务源码，不创建 Task 41 工作树。

**状态：** `BLOCKED`

**目标：** 证明一个真实的 OS 级 workspace-only 隔离原型是否可行。必须先验证最小原生/探针进程，再验证 .NET runtime，最后验证固定 .NET SDK build。

**允许范围：** 安全原型、探针、测试夹具、审计证据和必要架构记录。不得修改 `apps/api/src/**`、`apps/web/src/**`、`content/**` 或公共 API；不得实现 `CSharpRunner`。

**权限模型：**

- workspace：`READ / WRITE`。
- 本次运行专属 `TEMP`：`READ / WRITE`。
- `D:\DevTools\dotnet\`：`READ / EXECUTE ONLY`。
- 必要 runtime / sdk / packs：`READ / EXECUTE ONLY`。
- NuGet/cache：优先 `READ ONLY`；如确需写缓存，必须使用本次运行独享的临时 cache，不允许多个 Submission 共享可写 cache。
- 宿主其他路径：`DENY`。

**必须拒绝：** `C:\Windows\win.ini`、任意绝对路径、`..` 逃逸、`Path.GetFullPath` 规范化逃逸、字符串拼接路径、`char[]` 构造路径、Base64/编码构造路径、`Environment` + `Path` API、`System.IO` 全限定 API、`FileStream`、`FileInfo`、`Directory`、`DirectoryInfo`、Reflection、Delegate、Dynamic / InvokeMember。

**禁止 PASS 依据：** 扫描 `File.ReadAllText`、`System.IO`、`C:\`、`..`、Reflection，或任何正则/AST 黑名单。必须由 Windows OS access check 实际拒绝。

**分阶段门禁：**

- Gate A — Host capability：只读检查 `processmodel.dll`、`Experimental_CreateProcessInSandbox` / 对应 sandbox API 和当前 Windows build 支持情况；不得安装组件。不支持时仅标记该路径 `UNSUPPORTED_FOR_THIS_PATH`，继续 Tier 2。
- Gate B — Minimal sandbox probe：先运行最小探针，验证 workspace 相对 read/write 为 `ALLOW`，`C:\Windows\win.ini` 与 `..` escape 为 `DENY`。
- Gate C — Full bypass matrix：重新执行 Task 41-PRE 同等级安全矩阵，必须达到 `15/15 DENY` + workspace `ALLOW` 全部通过。
- Gate D — .NET runtime：验证 `dotnet app.dll` 可正常运行，同时 workspace 外读取仍为 `DENY`。
- Gate E — .NET SDK：固定 `D:\DevTools\dotnet\dotnet.exe` 与 `.NET SDK 10.0.100`，验证受控离线 `dotnet build --no-restore`，同时 filesystem isolation 不退化。

**网络隔离：** 默认不得授予网络 capability。至少验证 HTTP、TCP、DNS、localhost、`127.0.0.1:8000`、`127.0.0.1:4173`、LAN 均为 `DENY`。除非未来受控题目另有正式合同，普通 C# Runner 无网络权限。

**Handle / IPC 门禁：** sandbox broker 默认禁止继承宿主全部 handle，不得使用无约束 `inheritHandles = true`。只允许显式白名单 `stdin`、`stdout`、`stderr` 和必要 IPC handle；不得把文件、socket、token 或其他敏感宿主 handle 泄漏给 sandbox 子进程。

**Job Object 定位：** Job Object 可以继续用于 process tree、kill-on-close、timeout、CPU / memory 和 cleanup；但 `Job Object != filesystem isolation`，不能单独作为 `Task 41-SBX PASS` 依据。

**AppContainer 判定：** “采用 AppContainer”本身不是 PASS。只有真实实验同时满足 workspace `ALLOW`、全部 workspace 外路径 `DENY`、绕过矩阵 `DENY`、网络 `DENY`、handle 不泄漏，才能视为隔离原型通过。必要时应比较 AppContainer 与 LPAC 的实际权限差异。

**结论枚举只能是：** `PASS`、`BLOCKED`、`UNSUPPORTED_FOR_THIS_PATH`。

- `PASS`：证明所选 sandbox 实现满足完整安全合同。
- `BLOCKED`：当前可行方案无法满足安全合同，或必须降低门禁。
- `UNSUPPORTED_FOR_THIS_PATH`：仅表示某一具体实现路径当前主机不可用，应继续下一优先级方案。

### 2026-08-29 Gate A / Gate B-DIAG 最终登记

- Gate A：`COMPLETE`。
- Tier 1 Create Process In Sandbox / `Experimental_CreateProcessInSandbox`：`UNSUPPORTED_FOR_THIS_PATH`；当前主机缺少 `processmodel.dll`，对应 sandbox API 无法加载。
- Tier 2 Classic AppContainer：`FAIL`。workspace relative read/write 为 `ALLOW`，`..` 与 `Path.GetFullPath` 逃逸为 `DENY`，但 `C:\Windows\win.ini` 仍为 `ALLOW`，因此安全合同失败。
- Tier 2 LPAC Gate B 初始为 `LAUNCH BLOCKED`；Gate B-DIAG（LPAC Launch Viability Diagnostic）已完成。
- LPAC launch path：`UNSUPPORTED_ON_CURRENT_HOST`。Microsoft 签名的 `where.exe` / `cmd.exe` 通过 LPAC 创建路径均在 `CreateProcessW` 返回 `ERROR_NOT_SUPPORTED (50)`；相同映像在 Classic AppContainer 下可启动。
- 未签名 .NET TinyProbe + LPAC 返回 `ERROR_INVALID_IMAGE_HASH (577)`。
- 已核对官方 LPAC attribute 模型：`SECURITY_CAPABILITIES`、`ALL_APPLICATION_PACKAGES_POLICY`、`OPT_OUT=1`、`AttributeCount=2`、`EXTENDED_STARTUPINFO_PRESENT`，以及结构大小和生命周期。capability、appName、Unicode env 等变体不能消除错误 50。
- 未通过安装证书、关闭 Code Integrity、修改 Defender、修改系统策略、修改系统目录 ACL、安装 Feature 或把提权作为最终依赖来绕过。
- Gate C 未启动；当前 Tier 2 没有有效候选。

**正式裁决：** Classic AppContainer = `security contract FAIL`。LPAC security contract = `UNPROVEN`，因为 LPAC 子进程未能启动；LPAC launch path = `UNSUPPORTED_ON_CURRENT_HOST`。不得泛化为“LPAC 技术本身不安全”或“LPAC 在所有平台不可用”。

**Task 41-SBX 最终状态：`BLOCKED`。**

**当前范围裁决：** 上述解冻条件仅适用于未来 hostile/untrusted 或多人在线执行版本。当前可信本地学习范围已由用户正式放行，Task 41 直接登记为 `READY FOR DISPATCH`。

### Tier 3 隔离架构决策项

**共同主责：** 策划总控 + 架构与管理 Session。

**用户授权：** 2026-08-29 已授权进入 Tier 3。授权范围是完成候选比较、选择一个推荐方案，并为该方案形成最小、可回滚、可审计的原型任务包。授权不等于 Task 41 解冻，也不允许在未选定方案时同时实施多个 Tier 3 基础设施路径。

**候选至少包括：**

1. 隔离 Runner Service / Remote Sandbox；
2. Windows Container；
3. 本地 VM / Hyper-V；
4. Windows Sandbox 类方案。

Tier 3-PRE 已正式返回 `HOST_UNSUPPORTED_EDITION`。Hyper-V-isolated Windows Container 作为当前本机主路线停止推进；不得继续安装 runtime、启用 Containers/Hyper-V 或处理本机 Windows container image。

Remote Runner / 独立远程沙箱已转为未来多人在线版本的安全强化事项，不再是当前 Phase F 主路线。

```text
Hard API
→ authenticated Runner Client
→ Remote Runner Service
→ per-submission isolated sandbox
→ pinned .NET SDK 10.0.100 runtime/image
→ ephemeral workspace
→ sanitized result
```

Tier 3 原型必须执行 host filesystem allowlist isolation：只允许 per-run workspace、per-run TEMP 与明确授权的 trusted SDK/toolchain，未显式 mount 的 host filesystem 必须不可见；guest image 自身 `C:\Windows` 不属于 host leak。用户代码必须无法到达 host localhost、Hard `8000`、frontend `4173`、LAN 与 Internet；guest 自身 loopback 可以存在。最终 runner image 必须包含精确 .NET SDK `10.0.100` 并锁定 digest，不得使用 rolling `10.0` tag。Docker Desktop 仅是 prototype runtime 候选，用户代码不得获得 Docker daemon、host named pipe 或 runtime control capability。

相关历史合同继续保留于 `docs/superpowers/specs/2026-08-29-remote-runner-service-architecture.md` 和 `docs/superpowers/plans/2026-08-29-task41-rmt-pre-remote-runner-viability.md`，状态均由当前范围裁决覆盖。

### Tier 3-PRE: Windows Container Host Compatibility Gate

**性质：** 独立只读主机门禁；不安装 runtime、不启用 Feature、不处理 image、不修改产品源码。

**状态：** `HOST_UNSUPPORTED_EDITION`；已完成。Hyper-V-isolated Windows Container 本机主路线停止推进。

**主责：** 部署与运维 Session；架构与管理 Session 复核合同映射；策划总控登记唯一门禁结论。

**必须核对：** Windows Edition、build、Containers Feature availability、Hyper-V Feature availability、SLAT、BIOS virtualization、RAM、Docker Windows-container eligibility。

**唯一结论：** `HOST_SUPPORTED`、`HOST_UNSUPPORTED_EDITION`、`HOST_UNSUPPORTED_HARDWARE`、`HOST_REQUIRES_OS_CHANGE`。

当前结论不是 `HOST_SUPPORTED`，因此不得安装本机 container runtime、启用 Feature 或处理 image。

### Task 41-RMT-PRE: Remote Runner Viability Gate

**性质：** 独立远程沙箱可行性与安全门禁；不是 `CSharpRunner` 实现。

**状态：** `CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE`。

**处置：** 停止 E2B Provider、Remote Runner prototype、Firecracker、20 项 hostile-code matrix、cross-submission、host-secret、control-plane/runtime-socket 和 hostile path bypass 工作。不得创建 E2B Account/API Key/Sandbox/Template。

**未来恢复条件：** Hard 开放多人在线执行、陌生用户提交或不可信第三方代码时，必须重新建立独立 Sandbox / Remote Runner 安全项目并重新授权。

**历史说明：** 原 20 项矩阵、停止条件和执行计划仅供未来多人在线/不可信代码版本恢复安全项目时参考；当前不得执行。

### Task 41: C# Runner — Trusted Local Learning Environment

**Files:** `apps/api/src/hard_api/runners/csharp.py`、`apps/api/src/hard_api/diagnostics/csharp.py`、`apps/api/src/hard_api/main.py`、`apps/api/tests/runners/test_csharp.py`、`apps/api/tests/runners/fixtures/csharp/**`，以及任务确需的既有 RunnerManager/contract 测试。

- [x] 前置条件：用户已正式将当前范围限定为单用户、本地、用户本人可信学习代码；Task 41 = `READY FOR DISPATCH`。
- [ ] 1. 实现 C# compile/run。
- [ ] 2. 支持 top-level statements。
- [ ] 3. 支持标准 `Program` / `Main`。
- [ ] 4. 使用 `dotnet build --no-restore`。
- [ ] 5. 使用完全由服务端控制的固定离线 project/template。
- [ ] 6. 禁止任意 NuGet packages / `PackageReference`。
- [ ] 7. 禁止用户提供 NuGet Source。
- [ ] 8. 禁止用户 `.csproj` 注入、`Import`、`Exec`、`UsingTask` 和自定义项目路径。
- [ ] 9. 禁止用户 MSBuild / compiler argument 注入。
- [ ] 10. 每次运行使用独立临时 workspace。
- [ ] 11. 支持 stdin。
- [ ] 12. 支持 UTF-8 源码、输入和输出。
- [ ] 13. 正确 capture stdout / stderr。
- [ ] 14. 正确分类 compile error 并返回安全诊断。
- [ ] 15. 正确分类 runtime error。
- [ ] 16. 执行 hidden tests。
- [ ] 17. Hidden test / reference content 不得通过公共 API、诊断、stdout/stderr 或日志泄漏。
- [ ] 18. timeout 必须终止执行并返回稳定分类。
- [ ] 19. output limit 必须终止执行并返回稳定分类。
- [ ] 20. process-tree cleanup 必须覆盖超时、输出超限、取消和异常路径。
- [ ] 21. workspace cleanup 必须覆盖成功和所有失败路径。
- [ ] 22. 固定 `D:\DevTools\dotnet\dotnet.exe` 与 SDK `10.0.100`；缺失或错误版本显式失败，不得自动安装、下载或切换 SDK。
- [ ] 23. 保持 RunnerManager queue/cancel 兼容性，取消等待中/执行中任务不得遗留进程或 workspace。
- [ ] 24. 运行既有 PythonRunner、JavaRunner 和后端回归，禁止破坏现有语言路径。
- [ ] 固定 `DOTNET_CLI_TELEMETRY_OPTOUT=1`、`DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1`、`DOTNET_NOLOGO=1`，并将 `NUGET_PACKAGES` 指向 D 盘受控目录；普通执行不得联网 restore。
- [ ] 预留服务端内部 `allow_unsafe` capability：普通 Exercise 固定 `false`，只有服务端私有 Exercise Metadata / 内部 allowlist 可以设为 `true`。
- [ ] 用户 Submission、前端、源码内容、用户 `.csproj`、MSBuild 参数和编译器参数均不得提供、控制或自动开启 `allow_unsafe`；默认必须关闭。
- [ ] 在文档、接口说明或用户提示中明确：`TRUSTED_LOCAL_LEARNING_ONLY`，不是恶意代码安全沙箱；不得宣称可安全运行陌生用户、恶意或不可信第三方代码。
- [ ] 提交 `feat(runner): execute CSharp exercises` 后停止。

### Task 41 独立审计

**主责：** 测试与审计 Session；不得由 Task 41 实施者自审替代。

- [ ] 从正式 Task 41 提交核对固定本地 SDK 10.0.100、离线模板、compile/run、top-level/Main、禁止项目/参数注入、错误分类、stdin/UTF-8、隐藏内容保密、timeout/output/process/workspace cleanup、RunnerManager queue/cancel、`allow_unsafe` 和 Python/Java 回归。
- [ ] 核对产品和文档明确声明 `TRUSTED_LOCAL_LEARNING_ONLY`，没有任何 hostile/untrusted sandbox 安全宣传。
- [ ] 结论为 `PASS` 或 `BLOCKED`；`BLOCKED` 时冻结后续前端与内容任务。

### 前端 C# 编辑器兼容门禁

**主责：** 前端 Session；仅在 Task 41 独立审计 `PASS` 后开始。

- [ ] 编辑器语言映射必须显式为 `python → python`、`java → java`、`csharp → csharp`。
- [ ] 未知语言不得自动伪装为 Python；使用 `plaintext` 或现有产品合同明确规定的 unsupported fallback。
- [ ] 前端不得展示、提交或控制 `allow_unsafe`，不得提供 `.csproj`、NuGet、MSBuild 或编译器参数入口。
- [ ] 为三种已支持语言和未知语言 fallback 添加可复核测试。

### 前端独立验收

**主责：** 测试与审计 Session；不得由前端实施者自验替代。

- [ ] 独立验证显式语言映射、未知语言 fallback、编辑器交互、提交合同与 `allow_unsafe` 不可控。
- [ ] 结论 `PASS` 后才允许 Task 42；否则冻结 C# 内容链。

### Task 42: C# 入门、类型与控制流

**Module/path:** `csharp-foundations` / `content/csharp/csharp-foundations/**`

**Sources:** 教程、简介、开发环境、程序结构、基本语法、数据类型、类型转换、变量、变量作用域、常量、运算符、判断、循环。

- [ ] 按内容合同完成并用已通过独立审计的 C# runner 验证。
- [ ] 普通 `+`、`-`、`*`、`/`、`%` 运算符基础知识只在本模块出现；不得包含用户自定义 `operator overload` 课时。
- [ ] 提交 `content(csharp): add foundations module` 后停止。

### Task 43: C# 数据结构与面向对象

**Module/path:** `csharp-oop` / `content/csharp/csharp-oop/**`

**Sources:** 封装、方法、可空类型、数组、字符串、结构体、枚举、类、继承、多态、运算符重载、接口、命名空间。

- [ ] 按内容合同完成；用户自定义 `operator overload` 唯一归属本任务和 `csharp-oop`。
- [ ] 与 Task 42 不重复生成 lesson，来源覆盖必须恰好一次且 `unassigned == 0`；内容执行 Agent 无权改变该归属。
- [ ] 提交 `content(csharp): add oop module` 后停止。

### Task 44: C# IO、异常与元数据

**Module/path:** `csharp-io-metadata` / `content/csharp/csharp-io-metadata/**`

**Sources:** 预处理器指令、正则表达式、异常处理、文件输入输出、特性、反射。

- [ ] 按内容合同完成；文件题只访问临时目录。
- [ ] 提交 `content(csharp): add io and metadata module` 后停止。

### Task 45: C# 属性、委托与集合

**Module/path:** `csharp-language-features` / `content/csharp/csharp-language-features/**`

**Sources:** 属性、索引器、委托、事件、集合、泛型、匿名方法。

- [ ] 按内容合同完成。
- [ ] 提交 `content(csharp): add language features module` 后停止。

### Task 46: C# 不安全代码、并发、测验与结业

**Module/path:** `csharp-capstone` / `content/csharp/csharp-capstone/**`

**Sources:** 不安全代码、多线程、语言测验，以及来源清单中尚未归入前述模块的 C# 目录项。

- [ ] 按内容合同完成；普通题 `allow_unsafe = false`，仅服务端私有 Exercise Metadata / 内部 allowlist 可为隔离专用题设置 `true`。
- [ ] 用户 Submission、前端、源码、`.csproj`、MSBuild 参数和编译器参数均不得开启 `/unsafe`。
- [ ] 添加全路线分级测试与结业挑战，断言 C# 来源覆盖 100% 且 `unassigned == 0`；本任务不代替后续统一验收或完整 E2E。
- [ ] 提交 `content(csharp): complete CSharp route` 后停止。

### C# 内容统一验收

**主责：** 内容与课程 Session 提交完整内容报告，测试与审计 Session 独立验收。

- [ ] 验证 Task 42–46 每个模块、lesson、exercise、reference solution、来源映射和模块间依赖。
- [ ] 验证普通运算符只在 `csharp-foundations`，用户自定义运算符重载只在 `csharp-oop`，无重复 lesson、无多归属、`unassigned == 0`。
- [ ] 验证普通 Exercise 均未取得 `allow_unsafe=true`，专用不安全代码题仅通过服务端私有 allowlist 获权。

### Phase F 完整 E2E

**唯一启动者：** 测试与审计 Session。

- [ ] 在冻结的 Phase F 候选基线上执行真实 .NET 10 Runner、前端编辑器、Task 42–46 内容、评分、进度、恢复与安全边界的完整 E2E。
- [ ] 保留命令、环境、结果、失败、截图/日志定位和工作树状态证据；不得由内容或实施会话自行宣告替代。

### Phase F 最终统一审计

**主责：** 策划总控汇总专业报告并维护门禁，最终阶段放行由用户决定。

- [ ] 核对 trusted-local 范围声明、Task 41 独立审计、前端独立验收、Task 42–46 独立提交、C# 内容统一验收和完整 E2E；历史 Task 41-PRE/RMT-PRE 不作为当前 PASS 前置。
- [ ] 只有 P0/P1 为 0、全部合同和回归通过、证据完整、候选工作树干净时，才能形成 Phase F `FINAL PASS` 候选结论。
- [x] Phase G 在用户明确放行前继续冻结；P001 已于 2026-09-02 明确放行，后续按 Phase G 串行门禁执行。

---

## Phase G — C++ 路线

**正式起始基线：** `2106d8432da3a892bcfda7a12b95a35638796afd`

**阶段状态：** P001 已于 2026-09-02 登记 `PHASE_F: ACCEPTED`、`START_PHASE_G: YES`。`Task 47 = READY FOR DISPATCH`；Task 48–54 必须等待各自直接前置任务的接受提交后逐项解锁；Phase H 继续冻结。

**唯一允许的执行顺序：**

```text
Task 47 → Task 47 独立审计与 P001 接受
→ Task 48 → P001 接受
→ Task 49 → P001 接受
→ Task 50 → P001 接受
→ Task 51 → P001 接受
→ Task 52 → P001 接受
→ Task 53 → P001 接受
→ Task 54 → C++ 路线统一验收与 E2E
→ Phase G 最终统一审计 → P001 决定是否启动 Phase H
```

### Task 47: MSYS2 UCRT64 C++20 runner 适配器

**Files:** `apps/api/src/hard_api/runners/cpp.py`、`apps/api/src/hard_api/diagnostics/cpp.py`、`apps/api/src/hard_api/main.py`（仅注册 `CppRunner`）、`apps/api/tests/runners/test_cpp.py`、`apps/api/tests/runners/fixtures/cpp/**`，以及任务确需的既有 RunnerManager/contract 集成测试。`main.py` 是完成产品 API 语言注册所需的最小范围修正，不授权其他接口或架构重构。

- [ ] 先测试编译/运行、多个源文件、编译诊断、测试失败、stdin、超时、输出限制、进程清理和缺 g++。
- [ ] 固定调用 `D:\DevTools\msys64\ucrt64\bin\g++.exe`，参数固定为 C++20、警告开启、输出到临时目录；用户不得传编译/链接参数。
- [ ] 运行时 PATH 只含所需 UCRT64 DLL 目录，隐藏 harness 不返回。
- [ ] 提交 `feat(runner): execute Cpp exercises` 后停止。

### Task 48: C++ 入门与语言基础

**Module/path:** `cpp-foundations` / `content/cpp/cpp-foundations/**`

**Sources:** 教程、简介、环境设置、基本语法、注释、数据类型、变量类型、变量作用域、常量、修饰符、存储类、运算符、循环、判断。

- [ ] 按内容合同完成并用 C++ runner 验证。
- [ ] 提交 `content(cpp): add foundations module` 后停止。

### Task 49: C++ 函数、容器与内存基础

**Module/path:** `cpp-core-memory` / `content/cpp/cpp-core-memory/**`

**Sources:** 函数、数字、数组、字符串、指针、引用、日期时间、基本输入输出、结构体、vector、数据结构。

- [ ] 按内容合同完成；地址相关隐藏测试不依赖具体绝对地址。
- [ ] 提交 `content(cpp): add core memory module` 后停止。

### Task 50: C++ 面向对象

**Module/path:** `cpp-oop` / `content/cpp/cpp-oop/**`

**Sources:** 类与对象、继承、运算符/函数重载、多态、数据抽象、数据封装、接口/抽象类。

- [ ] 按内容合同完成。
- [ ] 提交 `content(cpp): add oop module` 后停止。

### Task 51: C++ 高级语言特性

**Module/path:** `cpp-advanced` / `content/cpp/cpp-advanced/**`

**Sources:** 文件和流、异常处理、动态内存、命名空间、模板、预处理器、信号处理、多线程、Web 编程。

- [ ] 按内容合同完成；信号、线程、Web 题使用受限 harness，不开放任意网络。
- [ ] 提交 `content(cpp): add advanced module` 后停止。

### Task 52: C++ STL 与容器头文件

**Module/path:** `cpp-stl-containers` / `content/cpp/cpp-stl-containers/**`

**Sources:** STL 教程、导入标准库、标准库、`iostream`、`fstream`、`sstream`、`iomanip`、`array`、`vector`、`list`、`forward_list`、`deque`、`stack`、`queue`、`priority_queue`、`set`、`unordered_set`、`map`、`unordered_map`、`bitset`。

- [ ] 按内容合同完成。
- [ ] 提交 `content(cpp): add stl containers module` 后停止。

### Task 53: C++ 算法、数值与并发库

**Module/path:** `cpp-algorithms-concurrency` / `content/cpp/cpp-algorithms-concurrency/**`

**Sources:** `algorithm`、`iterator`、`functional`、`numeric`、`complex`、`valarray`、`cmath`、`string`、`regex`、`ctime`、`chrono`、`thread`、`mutex`、`condition_variable`、`future`、`atomic`。

- [ ] 按内容合同完成；并发题必须有确定性超时和无数据竞争判定。
- [ ] 提交 `content(cpp): add algorithms and concurrency module` 后停止。

### Task 54: C++ 工具、内存、实例、测验与结业

**Module/path:** `cpp-capstone` / `content/cpp/cpp-capstone/**`

**Sources:** `type_traits`、`typeinfo`、`exception`、`stdexcept`、`cstdio`、`cstdint`、`memory`、`new`、`utility`、`random`、`locale`、`codecvt`、`cassert`、`cwchar`、`climits`、`cfloat`、`cstdlib`、`numbers`、OpenCV、有用资源、实例、测验，以及来源清单中尚未归入前述模块的 C++ 目录项。

- [ ] 按内容合同完成；OpenCV 题不强制安装 OpenCV，使用 API 识别/静态题或纯数据 fixture。
- [ ] 添加全路线分级测试与结业挑战，断言 C++ 覆盖 100%，运行路线 E2E。
- [ ] 提交 `content(cpp): complete Cpp route` 后停止。

---

## Phase H — 跨语言整合与发布审计

> 2026-09-05 当前门禁：用户已批准启动Phase H并发放任务。Task55从dc84ecad066cceceadabbae7fc9247bae9015d89开始，任务包交用户转发，尚未实际执行；Task56等待Task55正式接受，不继承Phase G批量特批。正式范围与必要接入补充见 `项目md/Phase-H-Task55-56-Trae任务包.md`。Phase G浏览器E2E例外不自动豁免Phase H发布检查。较早的Phase H冻结记录由此更新覆盖。

### Task 55: 跨语言概念对照完整映射

**Files:** `content/concepts.yaml`、`apps/api/src/hard_api/content/comparison.py`、`apps/api/src/hard_api/api/comparison.py`、`apps/api/tests/content/test_comparison.py`、`apps/web/src/features/compare/**`、`tests/e2e/comparison.spec.ts`、`docs/audit/task-55/**`

- [ ] 先测试每个 concept 的语言槽位、语义差异、代码例、来源课时链接和缺失槽位行为。
- [ ] 对四路线共同概念建立人工审校映射；对不等价概念明确“仅该语言”或差异说明，不强行类比。
- [ ] 页面支持概念筛选和四列/手机分段对照，所有代码转义且可打开对应课时。
- [ ] 运行概念引用完整性、API、组件和 E2E 测试。
- [ ] 提交 `feat(compare): complete cross-language concept map` 后停止。

### Task 56: 全系统发布验收与本地启动包

**Files:** `scripts/start-hard.ps1`、`scripts/stop-hard.ps1`、`scripts/release-check.ps1`、`README.md`、`docs/user-guide.md`、`docs/security/runner-boundary.md`、`docs/audit/release/**`

- [ ] 从干净项目依赖状态运行 bootstrap、迁移、内容校验、API/Web 构建和所有测试；不得跳过慢测试。
- [ ] 证明四个 runner 的成功、编译失败、超时、输出溢出、进程清理和缺工具降级。
- [ ] 证明四门路线来源覆盖均为 100%，参考解全部通过，全文无未解决占位符和 `fixture_only`。
- [ ] 用空数据库完成四路线入口、Python 全学习闭环、每语言至少一题真实编译、复习、搜索、对照、成长、备份恢复和手机草稿恢复。
- [ ] 执行键盘、触摸、对比度、减少动态效果、桌面视觉对照、手机无溢出检查；截图写入发布审计目录。
- [ ] `start-hard.ps1` 默认仅本机访问；LAN 必须显式开关并再次警告。`stop-hard.ps1` 必须清理 API/Web 与 runner 子进程。
- [ ] README 只写用户真正需要的启动、停止、手机访问、数据位置、恢复和安全边界。
- [ ] 运行 `scripts/release-check.ps1`，保存命令、退出码、覆盖率、内容数量、工具版本、截图索引和限制。
- [ ] 提交 `release: certify Hard version 1` 后停止，等待最终项目审计。

---

## 项目经理最终审计清单

- [ ] 56 个任务均有单独审核记录，历史中无跨任务混合提交。
- [ ] 当前工作树干净，`git show --check` 无空白错误，锁文件与 OpenAPI 无漂移。
- [ ] Python、Java、C#、C++ 来源清单全部 `expected == implemented == validated == reference_solutions_passed`。
- [ ] 所有后端、前端、内容、runner、E2E 和发布检查通过，覆盖率达到全局阈值。
- [ ] 选定桌面视觉目标得到落实，手机使用纵向路线且核心功能等价。
- [ ] 无 AI、云账号、Docker、运行时抓取、公共暴露或未经批准的防火墙变更。
- [ ] 数据、依赖、缓存、备份、导出与 runner 工作区均位于 D 盘。
- [ ] 已实际恢复备份，已实际清理超时子进程，已实际验证四个编译/解释器。
- [ ] 已向用户说明无容器 runner 不能安全执行恶意代码，以及无 LAN 登录会暴露给同网设备。
