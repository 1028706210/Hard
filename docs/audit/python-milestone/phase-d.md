# Phase D Python 路线复审记录

## 课程与来源覆盖

- 课程：84 节课、84 份练习、252 道知识题、84 道代码题、11 个模块挑战。
- 可执行用例：95 条公开用例、190 条隐藏用例；190 条隐藏用例都与其公开用例的 `(stdin, stdout, exit_code, assertion)` 合同不同。
- 选项位置：每个模块的知识题正确答案均分布在 `a`、`b`、`c`，没有“整模块都选 a”的伪题库。
- 覆盖：Python `expected=implemented=validated=reference_solutions_passed=84`，`unassigned=0`，路线覆盖率 100%。每模块的来源主要知识点到 Hard 章节映射位于 `../task-22/coverage.json` 至 `../task-31/coverage.json` 的 `source_section_mapping`；每项均对应“概念定义与适用场景 / 语法、API 与边界 / 常见错误与实践建议”。
- 历史归属说明：`python-subprocess`、`python-treading`、`python-asyncio` 在此前 Task 26 中从模块 IO/OOP 调整到并发网络模块，以使来源主题与课程模块一致；本轮没有修改 `content/sources.yaml`。

## 题目、Runner 与安全边界

- 结构化 Runner 合同包含 stdin、精确 stdout、退出码和服务端断言；验证器拒绝不足三至四个选项、答案位置单一、少于两条隐藏用例或隐藏用例与公开用例重复的内容。
- 正式 Hello World 动态参考解与全部其他模块参考解均在临时 Runner 工作区通过。针对性 API 回归证明：只打印公开输出 `Hello, Hard!` 的提交失败隐藏测试；动态实现通过 `1` 条公开和 `2` 条隐藏用例。
- 异步、线程、子进程、数据库、Selenium、Scrapy 与 PyQt 练习采用本地协程、有限线程、纯命令计划、SQL 参数化结构、fake WebDriver、URL fixture 或纯状态函数；没有扩大网络、GUI、数据库或子进程权限。
- 公开 API、OpenAPI 与历史记录继续只暴露题面、starter code 和公开测试说明；参考解、隐藏输入/输出及隐藏断言没有写入公开材料。

## 双端纵向旅程与视觉证据

- `python-journey.spec.ts` 参数化执行桌面 `1440×1024` 和手机 `390×844` 两套旅程，并通过 `X-Hard-E2E-Client` 在本地 E2E 服务中使用彼此独立的空白临时数据库、备份、导出和 Runner 目录。
- 两套均覆盖：首页进入、读课、笔记、收藏、搜索、错误与正确知识题、Python Runner、评分、复习、成长、导出、数据修改、安全导入及恢复验证。手机额外真实打开主导航、课时目录、编辑器和结果面板。
- 当前运行截图：`desktop-home-start-1440x1024.png`、`desktop-lesson-1440x1024.png`、`desktop-assessment-1440x1024.png`、`desktop-growth-1440x1024.png`，以及对应的 `mobile-*-390x844.png`。PowerShell 图像检查确认每张截图的真实像素尺寸与文件名一致。
- 常规检查未设置 `HARD_VISUAL_AUDIT_DIR`，不会改写跟踪截图；只有显式视觉审计命令更新本目录。

## 覆盖率

- 后端定向命令：`.venv\Scripts\python.exe -m pytest apps/api/tests/learning/test_scoring.py apps/api/tests/learning/test_review.py apps/api/tests/backup apps/api/tests/runners/test_python.py apps/api/tests/runners/test_manager.py --cov=hard_api.learning.scoring --cov=hard_api.learning.review --cov=hard_api.backup.service --cov=hard_api.runners.python --cov=hard_api.runners.manager --cov-branch --cov-fail-under=95`，退出 `0`、71 项通过；评分、复习、备份服务、Python Runner 与 RunManager 均为 `100%` 语句和分支覆盖。
- 后端全量命令：`.venv\Scripts\python.exe -m pytest apps/api/tests -q --disable-warnings --cov=hard_api --cov-branch --cov-fail-under=85`，退出 `0`；`hard_api` 综合覆盖率 `93.046%`（语句 `94.754%`、分支 `84.588%`），满足总覆盖率不低于 `85%` 的门禁。
- 前端：经授权新增且仅新增 `@vitest/coverage-v8@4.1.11`。`apps/web` 的 `vitest run --coverage.enabled --coverage.provider=v8` 退出 `0`，16 个文件、49 项测试通过，行覆盖率 `83.66%`（425/508），满足不低于 `80%`。覆盖 JSON 只写入 `.tool-cache/vitest-coverage`。

## 环境限制

- 未修改 Windows 防火墙、未公开私网端口、未访问来源正文以外的网站。
- 所有 E2E 数据在 `.tool-cache/live-e2e-*`；正式 `data/`、`backups/`、`exports/`、`runner-work/` 未被写入。
- 原创性检查的本地算法和覆盖测试已通过。来源连通性恢复后，以 `30` 秒读取上限重新扫描十个 Python 模块，均返回有效且无连续中文匹配；检查器只在内存读取页面，不保存网页内容、正文或匹配文本。
