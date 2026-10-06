# 【发给 Trae 执行体】Hard Phase H 正式任务包

发放日期：2026-09-05。P001 用户指令：“通过，发放Phase H任务”。

本包包含整个 Phase H，但只立即放行 Task55。Task56 是完整预备任务，必须等待 Task55 被 P001 正式接受后才能开始。Phase G 批量特批不延伸到 Phase H。

## 1. 当前门禁与执行纪律

```yaml
PHASE_G: ACCEPTED_BY_USER_WITH_E2E_EXCEPTION
START_PHASE_H: YES
PHASE_H: ACTIVE
TASK55: AUTHORIZED_TO_START
TASK56: BLOCKED_BY_TASK55_ACCEPTANCE
AUTO_START_TASK56: NO
EXECUTION_MODE: ONE_TASK_THEN_STOP_FOR_REVIEW
```

你收到本包后可以开始 Task55；本包发放不代表任务已实际开始，也不代表 Task56 获准开始。

先完整读取 C:/Users/李帅朋/.codex/AGENTS.md，检查当前路径上 AGENTS.md / AGENTS.override.md 并遵守；不得修改任何 AGENTS 文件。已读取且未变化的规则不重复加载。再读取本包共享前置条件、当前获授权任务章节，以及 [当前状态](../docs/status/CURRENT.md)。TASKS.md 仅核对当前 Task 55 或 Task 56 条款；设计文档仅读取当前功能对应章节。Phase G 审计仅在核查接受基线、E2E 例外或具体继承问题时读取对应报告段落和精确证据，不默认加载历史日志。全部原验收要求继续有效。

遵循最小正确修改：先查已有能力，先用失败测试锁定行为，再实现；不新增无必要依赖、平行架构或无关重构。每项形成独立原子提交并停止，提交后由 ChatGPT 一审、P001 独立二审和接受。不得仅凭自己或 ChatGPT 的PASS启动下一项。

## 2. 唯一基线与工作树

Task55 起始提交：

```text
dc84ecad066cceceadabbae7fc9247bae9015d89
```

直接父提交：

```text
313a2dc6aafd50120ff638bb181f9f5598a5af17
```

可核查的健康基线工作树：D:/projects/1/Hard-phase-g-cpp-route。

先执行：

```powershell
git -C D:/projects/1/Hard-phase-g-cpp-route rev-parse HEAD
git -C D:/projects/1/Hard-phase-g-cpp-route rev-parse HEAD^
git -C D:/projects/1/Hard-phase-g-cpp-route status --short
```

应与以上完整哈希一致、工作树干净。若不一致，停止报告，不 reset/clean/stash 或覆盖现场，也不得自行换基线。

Task55 使用独立分支 `phase-h/task55-compare`，工作树 `D:/projects/1/Hard-phase-h-task55-compare`。先检查分支和目录是否存在：不存在才从精确基线创建；若存在则检查其来源、HEAD和状态，不覆盖、不重复创建。不要从早期规划线 main 开始。

共享工作树 Hard-task1 只用于读取项目文档和复用环境，不在那里修改产品源码。保留所有历史失败现场、用户修改、stash及交接文件。

## 3. 环境与继承例外

- 使用现有项目 Python：D:/projects/1/Hard-task1/.venv/Scripts/python.exe；PYTHONPATH 必须指向当前执行工作树 apps/api/src。
- 复用现有 D 盘工具链、Hard-task1/node_modules 与离线缓存。允许未跟踪目录联接，不提交联接、缓存、虚拟环境、数据库或构建产物。
- Windows下从 apps/web 运行前端检查；若 .bin 启动脚本路径失效，可以调用现有依赖的实际 Node 入口，记录等价命令，不下载重装依赖。
- 不修改系统PATH、防火墙、分页文件、工具链版本；不创建云账号、Docker、Remote Runner或在线运行依赖。当前仅单用户本地可信学习代码。
- 真实Runner全量测试、全路线内容编译、浏览器E2E串行执行，避免争用内存及固定进程名清理检查。
- Phase G 由于用户明确批准，在浏览器E2E未覆盖的情况下接受；补充规格已在 apps/web/tests/e2e/cpp-journey.spec.ts。该例外不代表E2E已通过，也不自动豁免Task55自身E2E或Task56发布门禁。
- 遇到OOM、端口占用或权限限制，保留准确退出码、已运行/未运行数量和日志。不得降低断言、修改检查器、扩大超时或跳过慢测试伪装通过；只清理本任务确认拥有的进程和临时目录。

## 4. Task55：跨语言概念对照完整映射（现在执行）

### 目标与已有能力

已有 ComparePage.vue 通过读取目录和所有课时取得concept，仅展示四语言课时链接。复用该页面和现有内容仓库，完成真正的语义差异、公开代码示例和课时映射，不新建第二套对照页。

### 授权文件

原任务文件：

- content/concepts.yaml
- apps/api/src/hard_api/content/comparison.py
- apps/api/src/hard_api/api/comparison.py
- apps/api/tests/content/test_comparison.py
- apps/web/src/features/compare/**
- apps/web/tests/e2e/comparison.spec.ts（原任务 tests/e2e 路径对齐现有Playwright目录）
- docs/audit/task-55/**

本次P001补充必要接入范围：

- apps/api/src/hard_api/content/models.py：仅对照元数据的向后兼容模型；当前extra=forbid，不得直接添加无法加载的YAML字段。
- apps/api/src/hard_api/content/parser.py、repository.py、service.py、validation.py：仅当复用现有内容读取和引用校验确有必要时作最小改动。
- apps/api/src/hard_api/main.py：只注册新的只读对照router及必需服务，不重构初始化或Runner。
- apps/web/tests/compare/compare-page.spec.ts：补充真实用户行为的组件回归。
- tools/content/tests/**、apps/api/tests/content/**：仅与概念元数据兼容、课时引用和新接口直接相关的测试。
- packages/contracts/openapi.json 与既有前端生成类型文件：仅按仓库现有方式同步新增只读接口；不得改变旧接口语义。先定位现有生成路径，不新建平行类型体系。

其他文件确需修改时，说明具体依赖和最小范围，交P001处理，不自行扩展到Runner、评分、数据库迁移或其他课程内容。

### 实现与验收要求

1. 列出现有稳定concept ID及四路线实际引用，建立人工审校清单。不得改名或删除已有ID。
2. 每个概念明确 python/java/csharp/cpp 四个槽位：可比较时提供原创简洁说明、语义差异、公开代码例和有效课时链接；不等价或语言特有时明确说明；未有合适课程时给出真实缺失状态。不得强行类比、伪造课程链接或用“暂无内容”掩盖本应完成的映射。
3. 元数据设计保持最小、向后兼容。先在审计记录说明拟采用字段和新只读接口，再实施；复用既有错误体、路由约定和读取服务，不引入动态抓取或AI生成运行依赖。
4. 新接口返回公开映射，不暴露exercise私有参考解、隐藏测试、运行目录或本机路径；已有公开接口及OpenAPI行为保持兼容。
5. 页面支持概念筛选，桌面四列、手机纵向分段；正确展示loading/error/empty/缺失槽位，不以一次失败造成整页静默丢失。
6. 代码作为文本安全转义。用含HTML样式字符串的测试证明不会作为页面HTML执行，不使用未经安全处理的v-html。
7. 课时链接可打开且语言、concept匹配；不按“第一个同名课时”随意制造语义映射。避免逐课时请求整个四路线的无必要请求扇出，优先一次读取现有内容服务聚合结果。
8. 桌面1440x1024和手机390x844真实E2E：筛选、四语言或缺失槽位、语义差异、代码显示、打开课时并返回；每个关键页面无横向溢出。组件可使用受控mock，E2E不得mock API。
9. 记录概念总数、四槽位完整性、人工解释的语言特有/缺失槽位数、无效引用数、截图索引。无效引用必须0。

### 测试与证据

先加失败测试，至少覆盖四槽位、语义区别、代码转义、链接、缺失行为和向后兼容。修复后运行：

```powershell
<PROJECT_PYTHON> -m pytest apps/api/tests/content tools/content/tests -q
<PROJECT_PYTHON> -m pytest apps/api/tests -q
<PROJECT_PYTHON> apps/api/tests/core_coverage_gate.py
```

在apps/web运行既有TypeScript检查、Vitest全套及新增comparison.spec.ts真实Playwright；保存实际命令与退出码，不把占位符原样执行。再做四路线内容校验与生成契约漂移检查。

全局阈值不降：后端总行>=85%，Runner/备份/评分/复习核心按既有gate>=95%，前端总行>=80%。保留环境限制；必要E2E未运行或失败时不能宣告Task55 FINAL PASS。

Task55对照E2E由当前执行体按本任务包明确授权运行；项目完整发布E2E仍归测试与审计主责，不提前执行Task56。

### 提交与停止

提交消息必须为：

```text
feat(compare): complete cross-language concept map
```

一个独立原子提交，直接父提交必须为本包Task55基线。检查完整HEAD、父提交、逐文件变更、git show --check和clean状态。审计退回时只修当前任务并amend，保护其他修改。

完成后停止，提交ChatGPT一审，再将一审及原始证据提交P001二审；未经P001正式接受不得启动Task56。

## 5. Task56：全系统发布验收与本地启动包（预备，暂不执行）

### 解锁条件与基线

只在Task55已被P001正式接受且明确放行Task56后执行。基线使用 `<TASK55_ACCEPTED_COMMIT>`，必须由P001替换为完整接受哈希；不得预填当前候选或自行猜测。工作树/分支在正式解锁时确定，不在Task55期间创建。

### 主责及范围

测试与审计主责全系统验收；部署与运维负责启动/停止/发布检查脚本。若继续使用Trae，由后续Task56授权明确承担这些职责，问题按模块定向处理，不广播或擅自扩大产品改动。

原授权文件：

- scripts/start-hard.ps1
- scripts/stop-hard.ps1
- scripts/release-check.ps1
- README.md
- docs/user-guide.md
- docs/security/runner-boundary.md
- docs/audit/release/**

允许增加直接验证上述脚本的 tests/scripts/**（先检查仓库现有目录惯例）及 apps/web/tests/e2e/release.spec.ts，复用既有语言旅程；对原C++补充E2E进行必要修正仅限审计断言，不改产品行为或减弱门禁。其他模块发现P1时记录复现并交P001定向修复，不在发布任务顺手重构。

### 必须完成

1. 用隔离的干净项目环境验证现有bootstrap、数据库迁移、内容校验、API/Web构建和全套测试。干净不等于删除用户数据或共享依赖；复用离线缓存，确需下载/安装按原工具链授权规则处理。
2. 四个Runner：成功、语法/编译错误、运行错误、超时、输出溢出、运行中取消、子进程树清理、临时目录清理、缺工具降级；不得改真实工具安装来制造缺工具。
3. 四路线来源覆盖100%，expected=implemented=validated=reference_solutions_passed，unassigned=0；真实参考解与隐藏用例全执行，固定输出被拒绝；原创性、概念引用及有效来源通过。产品内容无未解决占位符或fixture_only，正常测试夹具不算产品占位。
4. 从空的隔离数据库完成：四路线入口、Python完整学习闭环、每语言至少一道真实运行题、复习、搜索、对照、成长、备份导出与实际恢复、手机草稿恢复。
5. 补齐Phase G扩展C++真实旅程：结业挑战、分级API解锁、复习评级更新及桌面手机证据。Phase G已接受的OOM例外不得自动沿用为最终发布PASS。
6. 键盘、触摸、对比度、减少动态效果、桌面视觉目标对照、手机无页面级横向溢出；保存新截图并逐张目检，不复用失败截图宣称成功。
7. start-hard.ps1默认仅本机；LAN必须显式开关和风险提示，不改防火墙或公开暴露。stop-hard.ps1只清理本次Hard启动链的API/Web/Runner进程，不终止用户其他程序。
8. 使用既有迁移、备份及恢复能力，证明启动失败回收、重复启动/停止、端口冲突有清晰错误。所有数据/依赖/缓存/备份/导出/Runner工作区位于D盘。
9. README和用户指南只写真实可用的启动、停止、手机访问、数据位置、恢复、安全边界；不宣称trusted-local Runner可以安全运行恶意代码。
10. release-check.ps1真实执行必要检查并准确传播非零退出码；不得跳过慢测试、隐藏失败或通过匹配报告文字代替执行。全局覆盖率阈值同Task55。

### 完成产物与停止条件

docs/audit/release/** 保存完整命令、退出码、覆盖率、四路线数量、工具版本、数据库/恢复证据、截图索引、进程与端口清理、P0/P1/P2和未覆盖项。

提交消息：

```text
release: certify Hard version 1
```

形成独立提交后停止，等待P001最终项目审计。Task56自测通过不等于全项目正式发布。不得自动打版本标签、推送远端、部署、开启LAN或宣称产品已经正式上线。

## 6. 每项统一交付格式

```text
任务：Task N — 名称
基线：完整hash
分支与工作树：
提交：完整hash
父提交：完整hash
变更：逐文件列出及原因
验证：命令 / 退出码 / 数量 / 覆盖率
真实Runner与E2E证据：
截图和审计文件绝对路径：
P0/P1/P2：
未覆盖与环境限制：
git show --check / git status：
状态：已停止，等待ChatGPT一审及P001二审
下一任务：未启动
```

现在唯一执行项：Task55。Task56内容已给出，但前置接受门禁仍有效。
