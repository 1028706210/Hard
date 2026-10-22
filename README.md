# Hard — 本地编程学习平台

Hard 是一个在本机 Windows 上运行的编程学习平台，提供 Python、Java、C#、C++ 四条学习路线：课时与示例、知识题、可真实运行的代码题与挑战、复习队列、全文搜索、跨语言概念对照、成长报告，以及本机备份导出与恢复。全部数据保存在本机 D 盘，默认仅监听 `127.0.0.1`。

## 技术栈与当前状态

前端采用 **Vue 3、TypeScript、Vite、Vue Router、Pinia、Monaco Editor**；后端采用 **Python、FastAPI、SQLAlchemy、SQLite / FTS5、Alembic**。课程由 Markdown / YAML / JSON 管理，通过 OpenAPI 维护接口契约，使用 pytest、Vitest 和 Playwright 分层验证。

截至 2026-10-21，核心学习流程已通过本机试运行验收：282 个课时与 282 份练习通过结构校验，45 个跨语言概念包含 111 个可用语言映射；后端 269 项、前端 117 项、浏览器 53 项测试通过。课程内容仍在逐章深化，69 个缺失映射明确保留。当前结果不等于完整课程认证或公网生产部署。

项目说明与简历素材见 [技术栈、进度与简历说明](docs/project-resume.md)，证据见 [前端与试运行验收](docs/audit/frontend-complete-20261020/README.md)和[内容深化汇总](docs/audit/content-depth-20261021/README.md)。

![Hard 首页知识星链](docs/audit/frontend-complete-20261020/showcase-home.png)

## 快速开始

本机已有依赖时，双击项目根目录的 **启动 Hard.cmd** 即可启动并自动打开浏览器；用完双击 **停止 Hard.cmd**。这两个入口自动定位项目，不需要手动切换目录或输入命令。启动或停止失败时窗口会保留具体错误。运行期间关闭网页不会停止后台服务；再次启动前先使用停止入口。命令行方式仍可用于自定义端口。

前置条件：Windows、项目位于 D 盘、已按 `docs/setup/windows-d-drive.md` 配置 D 盘工具链（受管 Python、node/pnpm）。首次使用先初始化依赖（需要 .venv 与 node_modules 缺失时的安装授权）：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\bootstrap-project.ps1
```

启动（默认 API `127.0.0.1:8000`、Web `127.0.0.1:4173`，可分别用 `-ApiPort` / `-WebPort` 覆盖）：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start-hard.ps1
```

启动成功后会打印 Web 地址；浏览器打开 `http://127.0.0.1:4173` 即可学习。

首次启动会自动准备数据库，复用项目既有的“迁移前备份、失败恢复”流程；已是最新版本时不重复迁移。只有 API 就绪检查通过后才显示启动成功，数据库准备失败时不会启动服务。

停止（只回收本次启动记录的 API/Web 进程树，不触碰其他程序）：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\stop-hard.ps1
```

## 数据与目录

全部位于项目根（D 盘）下：

| 目录 | 用途 |
| --- | --- |
| `data\` | SQLite 数据库（学习进度、复习、搜索索引） |
| `backups\` | 自动备份 |
| `exports\` | 手动导出的备份归档（zip） |
| `runner-work\` | 代码运行器的临时工作区 |
| `.tool-cache\` | 工具链缓存与启动运行状态 |

## 安全边界

- 默认仅本机访问（`127.0.0.1`），不修改防火墙、不做端口转发或公网暴露。
- 手机访问属可选 LAN 模式：必须在“设置与数据 → 手机访问”显式选择私网地址并确认风险；每次重启后回到仅本机。详见 `docs/setup/phone-access.md`。
- 代码运行器仅适合运行你自己编写的学习代码（TRUSTED_LOCAL_LEARNING_ONLY），不能安全运行恶意代码。详见 `docs/security/runner-boundary.md`。

## 发布自检

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\release-check.ps1
```

正式检查不支持跳过 E2E。它串行执行四路线静态校验、逐模块真实参考解/隐藏用例/固定输出拒绝与联网原创性、后端与核心覆盖、前端测试和构建、全部浏览器旅程。每轮证据写入 `docs/audit/release/runs/<运行编号>/`，步骤旁的 JSON 保存命令、时间和退出码；任何失败都停止发布检查并返回非零。联网检查失败必须重试或报告未覆盖，不能按历史结果放行。

依次执行四路线内容校验、后端测试与覆盖率门禁、前端测试与构建、发布 E2E，任一步非零即停止并保留日志（`docs\audit\release\logs\`）。

## 更多文档

- 使用指南：`docs/user-guide.md`
- 运行器安全边界：`docs/security/runner-boundary.md`
- 环境与工具链：`docs/setup/windows-d-drive.md`、`docs/setup/toolchain-verification.md`
- 手机访问：`docs/setup/phone-access.md`
