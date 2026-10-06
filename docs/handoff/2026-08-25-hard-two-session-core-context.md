# Hard 两个现有会话核心交接

**快照日期：** 2026-08-29  
**用途：** 新建 Session 时快速恢复项目上下文，不依赖复制完整聊天记录  
**来源会话：**

- `P001 | AI员工 | Hard项目策划`
- `P001 | AI员工 | Hard项目执行`

## 1. 项目目标

Hard 是一个本地优先的编程学习网站，面向“懂一点基础，但理解不深、还不能独立完成项目”的学习者。首批完整路线为 Python、Java、C#、C++，桌面和手机都能使用。

核心价值不是展示教程目录，而是形成可验证的学习闭环：

```text
选择路线 → 阅读原创中文课时 → 完成知识题/代码题
→ 获得评分与反馈 → 更新掌握度和解锁状态
→ 错题复习/搜索/笔记 → 查看成长 → 备份恢复
```

课程目录参考菜鸟教程，但正文、示例和练习必须原创；不得复制长段落、原测验、图片或评论。

## 2. 已确认的产品与环境决策

- 产品名称：`Hard`。
- 本地优先，不依赖云服务才能学习。
- 首批语言：Python、Java、C#、C++；以后可扩展更多路线。
- 桌面 `1440x1024` 与手机 `390x844` 保持核心功能一致。
- 学完课时和完成练习后可得分，并形成掌握度、复习、成长和徽章数据。
- 工具链和项目数据优先放在 D 盘；C 盘空间不足。
- Docker 暂缓，只有进入明确部署需求时再加入。
- 私有 LAN 可供手机访问，但不得自动修改防火墙或暴露公网。
- 不设独立 AI Session；未来 AI 能力必须经过架构 RFC。

## 3. 当前产品架构

- 前端：Vue 3 + TypeScript + Vite + Pinia + Vue Router + Monaco。
- 后端：FastAPI + Pydantic + SQLAlchemy + Alembic。
- 数据：SQLite + FTS5，可恢复迁移与本地备份。
- 内容：Git 管理的 Markdown/YAML/JSON；内容验证器和原创性检查。
- Runner：统一任务管理器调用各语言本地适配器，限制超时、输出、源码、stdin 和工作目录。
- 合同：`/api/v1` + OpenAPI 生成客户端；公开合同不得泄露参考解、隐藏测试或内部私密字段。

权威文件：

- `TASKS.md`
- `docs/superpowers/specs/2026-08-23-hard-programming-learning-platform-design.md`
- `docs/superpowers/specs/2026-08-25-hard-multi-session-development-architecture.md`
- `docs/design/hard-homepage-visual-target.png`

## 4. 两个会话的核心职责与经验

### 4.1 `P001 | AI员工 | Hard项目策划`

承担项目经理、架构师和独立审计者角色：

- 通过问答确定目标、环境、功能边界和价值。
- 生成产品规格与 56 个任务的实现计划。
- 审计每阶段提交、文件范围、测试、截图、安全和风险。
- 审计不通过时生成详细修复任务，并明确标注 `【发给 Terra】`。
- 未明确放行前冻结下一阶段。

重要经验：

- 自动化全绿不等于产品通过；需要真实页面、真实 Runner、真实迁移和真实恢复证据。
- 对评分、隐藏测试、幂等、离线状态、LAN 和备份必须使用失败关闭策略。
- 用户要求按阶段批量执行，任务书必须详细，不能只写简单 Task 标题。
- 汇报同时给出阶段完成度和任务数量，避免仅用 `N/56` 造成误解。

### 4.2 `P001 | AI员工 | Hard项目执行`

曾承担 Terra 实施角色：

- 阅读任务书和设计规格，测试优先实施并提交证据。
- 早期按单 Task 执行；之后按用户要求改为阶段批量执行。
- 每阶段完成后停止，等待项目经理统一审计。
- 审计修复只处理本阶段，不跨入下一阶段。

第一次 Phase D 交付已完整完成 **Task 22–32**，连续提交如下：

| Task | 提交 | 交付 |
|---|---|---|
| 22 | `123084a` | Python 入门与环境 |
| 23 | `e624f49` | Python 语法与核心类型 |
| 24 | `aeac6f8` | Python 集合与控制流 |
| 25 | `ebee1c8` | Python 函数、迭代与作用域 |
| 26 | `5b80b63` | Python 模块、IO、异常与面向对象 |
| 27 | `50c5371` | Python 标准库与数据格式 |
| 28 | `658706c` | Python 并发与网络 |
| 29 | `d4fdd88` | Python 数据库与部署专题 |
| 30 | `eb91317` | Python 自动化、UI 与 Web 工具 |
| 31 | `677c80a` | Python 新兴专题、测验与结业 |
| 32 | `1d32e4c` | Python 纵向闭环里程碑审计 |

这组提交证明“第一次 Task 22–32 任务已全部完成”。Phase D 尚未进行首次统一审计；当前工作树仍有执行会话留下的未提交修改和审计产物候选，审计时必须单独核对，不能预先视为审计修复或已验收交付。

该会话的历史职责已被六个专业 Session 取代，核心信息保存后于 2026-08-25 归档。它不再接收大任务或小任务；需要时可以恢复查看历史，但不得重新作为默认执行入口。

## 5. 项目进度快照

| 阶段 | 范围 | 状态 |
|---|---|---|
| Phase A | Task 1–5，工具链与工程骨架 | 已完成并复审 |
| Phase B | Task 6–12，内容规范、数据和学习引擎 | 已完成并复审 |
| Phase C | Task 13–21，Runner、完整 Web 闭环、备份和 LAN | 已完成并复审 |
| Phase D | Task 22–32，完整 Python 路线与里程碑 | 已完成统一审计，`FINAL PASS` |
| Phase E | Task 33–40，Java 路线 | 已完成最终统一审计，用户已结束 Phase E |
| Phase F | Task 41、前端门禁、Task 42–46，C# 路线 | Trusted local scope；RMT-PRE 已取消；Task 41 READY；Task 42–46 等待前序；Phase G 冻结 |
| Phase G | Task 47–56，C++、跨语言整合与发布 | 冻结 |

快照时仓库：

- 路径：`D:\projects\1\Hard-task1`
- Phase F 正式起始基线：`6246473bf565be308c1505921ec1219beb30803c`。
- `D:\projects\1\Hard-task1\.git` 当前仍指向不存在的 worktree 元数据目录，不能从该共享目录可靠取得分支、HEAD 或 status；不得擅自修复、清理、覆盖、暂存或提交现场文件。
- Phase E 的旧审计工作树、执行遗留和交接材料继续按原样保护；新任务必须从精确提交创建独立工作树，但本次规划修订未创建 Phase F 工作树。

## 6. 当前门禁

1. Task 41-PRE 已正式登记为 `BLOCKED`：workspace 相对读写 `ALLOW`，应拒绝场景 `DENY 0/15`，现有基础设施不能形成 .NET 子进程文件系统权限边界。
2. Task 41-SBX 已正式登记为 `BLOCKED`：Tier 1 缺少 `processmodel.dll`，为 `UNSUPPORTED_FOR_THIS_PATH`；Classic AppContainer 因 `C:\Windows\win.ini = ALLOW` 而安全合同失败；LPAC 子进程无法启动，launch path 为 `UNSUPPORTED_ON_CURRENT_HOST`，安全合同保持 `UNPROVEN`。
3. 2026-08-30 用户将 Hard 当前范围限定为单用户、本地、个人编程学习平台，只运行本人编写和信任的学习代码。
4. Task 41-RMT-PRE = `CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE`；E2B/Remote Runner/Firecracker/hostile matrix 停止，不得创建 E2B Account/API Key/Sandbox/Template。
5. Task 41 = `READY FOR DISPATCH / TRUSTED_LOCAL_LEARNING_ONLY`；它不是恶意代码安全沙箱，不得宣传可安全运行陌生用户、恶意或不可信代码。
6. Task 42–46 等待 Task 41 独立审计和前端门禁；Phase G 继续 `FROZEN`。未来开放多人在线/不可信执行时必须重新启用独立 Sandbox / Remote Runner 安全项目。
7. C# 普通运算符归 Task 42 / `csharp-foundations`；用户自定义运算符重载唯一归 Task 43 / `csharp-oop`。
8. 普通 Exercise 固定 `allow_unsafe=false`；只有服务端私有 Metadata / 内部 allowlist 可设为 `true`，用户、前端和用户构建参数均不得控制。
9. 最终阶段放行仍由用户决定；任务包必须只发给确有职责关系的会话并标注 `【发给 <Session 名称>】`。

## 7. 新 Session 必读规则

1. 先读本文件、新 Session 架构、`TASKS.md` 和当前阶段任务包。
2. 先检查 `git status`、分支、HEAD 和他人未提交修改。
3. 只修改任务包授权路径；越界先申请。
4. 行为变更先产生失败证据，再做最小实现。
5. 不伪造 Runner、评分、内容覆盖、截图或测试结果。
6. 阶段完成后给出提交、逐文件变更、验证、证据、限制和状态，然后停止。
7. 用户消息以 `skiss` 开头时，优先检查并实际使用少量相关 Skills/插件；不为使用而使用。

## 8. 当前会话组织

- 当前唯一总控：`P001 | AI员工 | Hard项目策划`（会话 `01a03911-f574-7340-875c-3e8ccd699caa`）。
- 六个专业会话：
  1. 架构与管理：`01a038ff-bc90-79b2-b722-796217d8eab2`
  2. 后端：`01a038ff-d1a3-7731-baa5-1ae9f6ec2edb`
  3. 前端：`01a038ff-d338-7230-a5a5-f513c90f8c12`
  4. 内容与课程：`01a038ff-d4dd-7601-851f-ec45be960f70`
  5. 测试与审计：`01a038ff-d662-7410-834b-1e66ae598d40`
  6. 部署与运维：`01a038ff-d7e3-75d3-8194-2bae0f536b76`
- 已归档历史会话：`P001 | AI员工 | Hard项目执行`。

以后无论大任务还是小任务，均由项目策划 Session 判断主责与必要依赖，只发送给真正相关的专业会话。当前下一任务是后端主责的 Task 41 Trusted Local Learning Runner；部署与运维已收到 RMT-PRE 立即停止通知。总控上下文过长时，先更新本交接文件和阶段分发记录，再新建策划会话；新会话确认状态后归档旧会话。
