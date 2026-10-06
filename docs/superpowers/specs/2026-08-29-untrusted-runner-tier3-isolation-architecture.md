# Untrusted Runner Tier 3 isolation architecture

**类型：** Phase F 阻断性架构与授权决策项  
**状态：** FUTURE MULTI-USER HARDENING / CURRENT PHASE F NON-BLOCKING  
**登记日期：** 2026-08-29  
**阶段基线：** `6246473bf565be308c1505921ec1219beb30803c`  
**共同主责：** 策划总控 + P001 | AI员工 | Hard架构与管理  
**最终授权：** 用户

> **2026-08-30 当前范围：** Hard 为单用户、本地、个人学习平台；不以 hostile/untrusted code execution 为当前 Phase F 验收目标。Task 41-RMT-PRE 已取消，Remote Runner/production sandbox 转为未来多人在线版本安全强化事项。当前 Task 41 为 `TRUSTED_LOCAL_LEARNING_ONLY` 本地 Runner。

## 1. 触发条件

- Task 41-PRE：`BLOCKED`。
- Task 41-SBX Gate A：`COMPLETE`。
- Tier 1 Create Process In Sandbox：`UNSUPPORTED_FOR_THIS_PATH`，当前主机缺少 `processmodel.dll`。
- Tier 2 Classic AppContainer：`security contract FAIL`，因为 `C:\Windows\win.ini` 仍可读。
- Tier 2 LPAC：security contract `UNPROVEN`；launch path `UNSUPPORTED_ON_CURRENT_HOST`。
- Task 41-SBX：`BLOCKED`；Gate C 未启动。

Tier 1 / Tier 2 没有可进入完整 hostile-code 安全矩阵的候选；Tier 3-PRE 返回 `HOST_UNSUPPORTED_EDITION`。Remote Runner 曾被选择，后于 2026-08-30 因 trusted-local 当前产品范围而取消，现仅作为未来多人在线版本强化项。

## 2. 必须比较的 Tier 3 候选

1. 隔离 Runner Service / Remote Sandbox；
2. Windows Container；
3. 本地 VM / Hyper-V；
4. Windows Sandbox 类方案；
5. 其他能由 OS、hypervisor 或独立受信服务强制宿主文件系统 allowlist 隔离的候选。

## 3. 必须回答的问题

每个候选必须给出：

- 文件系统隔离边界及未挂载宿主路径为什么不可见；
- workspace、TEMP、固定 .NET SDK、离线 NuGet/cache 的挂载和权限模型；
- 原 Task 41-PRE / Task 41-SBX 文件绕过矩阵的复测方案；
- host localhost、Hard `8000`、frontend `4173`、LAN、Internet 隔离和必要 IPC 模型；container guest 自身 loopback 可以存在，但不得绕过 host / external network 隔离；
- handle、token、socket、设备、共享目录和宿主服务泄漏边界；
- Windows 当前版本、.NET SDK `10.0.100` 和 D 盘路径兼容性；
- 性能、启动时延、并发、清理、镜像/快照生命周期和失败关闭；
- 本地优先产品体验、离线能力、部署与长期运维影响；
- 需要修改的产品架构、公共合同和专业 Session 分工；
- 可复核原型、独立安全复测和最终 E2E 计划。

## 4. 正式授权门禁

用户已于 2026-08-29 正式授权进入 Tier 3。授权范围为：完成候选比较、选择一个推荐方案，并为该方案形成一个最小、可回滚、可审计的原型任务包。该授权不等于 Task 41 解冻，也不允许在候选尚未选定时同时安装或实施多个 Tier 3 方案。

若推荐方案需要以下动作，架构报告和原型任务包必须逐项明确，并在实际执行时接受系统运行时审批：

- 安装或启用 Windows Feature；
- 管理员权限；
- 下载、构建或导入 VM / Container 镜像；
- 创建、启动或修改 Hyper-V、Windows Sandbox、Container runtime；
- 修改系统策略、Code Integrity、Defender、防火墙、网络、系统目录 ACL；
- 新建远程服务、账户、凭据或外部基础设施；
- 修改冻结产品架构或公共合同；
- 写入共享工作树、正式产品数据或既有 Git 状态。

授权不包含关闭 Code Integrity、Defender 或其他安全能力，不包含无边界网络暴露，不包含并行尝试多个需要系统变化的候选。安全边界正式定义为 host filesystem allowlist isolation：只显式挂载 per-run workspace、per-run TEMP 和受信 SDK/toolchain；未显式 mount 的 host filesystem 必须不可见。container guest image 自身的 `C:\Windows` 不属于 host leak。

Docker Desktop 仅作为 prototype runtime 候选。任何用户代码容器都不得获得 Docker daemon、`\\.\pipe\docker_engine`、其他 host named pipe、runtime socket、runtime CLI/API 凭据或控制 runtime 的 capability。

## 5. 决策输出

架构与管理 Session 必须返回：

1. Tier 3 候选比较矩阵；
2. 推荐方案与明确拒绝方案；
3. 推荐方案的信任边界和攻击面；
4. 需要用户批准的全部系统、权限、下载、镜像、网络和基础设施变化；
5. 分阶段实施计划、主责 Session、文件/环境范围和回滚方案；
6. 原型验收矩阵及同等级安全 PRE-GATE；
7. 独立安全复测和 Phase F 后续集成顺序；
8. 结论：`DECISION READY` 或 `BLOCKED`。

## 6. Tier 3-PRE 主机兼容性门禁（历史完成）

原型正式下发前必须完成 `Tier 3-PRE — Windows Container Host Compatibility Gate`。该门禁只读核对 Windows Edition、build、Containers Feature availability、Hyper-V Feature availability、SLAT、BIOS virtualization、RAM 和 Docker Windows-container eligibility。

结论只能是：

- `HOST_SUPPORTED`；
- `HOST_UNSUPPORTED_EDITION`；
- `HOST_UNSUPPORTED_HARDWARE`；
- `HOST_REQUIRES_OS_CHANGE`。

历史信息 `Build = 22631.6199`、`EditionID = CoreCountrySpecific` 只能作为复核输入。若正式证据确认当前 Edition 属于 Windows Home 类，则返回 `HOST_UNSUPPORTED_EDITION`。任何非 `HOST_SUPPORTED` 结论都禁止安装 runtime、启用 Feature 或下载/构建/导入 image。

正式结果：`HOST_UNSUPPORTED_EDITION`。因此不得安装 Docker Desktop、启用 Containers/Hyper-V 或处理本机 Windows container image；该路线已停止推进。

完整门禁合同见 `docs/superpowers/plans/2026-08-29-tier3-pre-windows-container-host-compatibility.md`。

## 7. 通用 Tier 3 原型安全合同

### 7.1 Host filesystem allowlist

- per-run workspace：允许显式 mount，读写权限按题目运行合同控制；
- per-run TEMP：允许显式 mount，必须运行独享并在结束后清理；
- trusted SDK/toolchain：只能显式授权，优先封装在 fixed runner image 内；若必须挂载则只读/只执行；
- 未显式 mount 的 host filesystem：必须对用户代码不可见；
- guest image 自身文件系统不是 host filesystem leak，但不得借 guest 路径访问 host 文件；
- 不得把 host daemon、named pipe、socket、credential、token、设备或敏感 handle 暴露给用户代码。

### 7.2 Network

用户代码必须无法到达 host localhost、Hard API `8000`、frontend `4173`、LAN 和 Internet。container guest 自身 loopback 可以用于 guest 内部受控进程，但不得成为访问 host、LAN 或 Internet 的旁路。

### 7.3 Fixed runner image 与 .NET SDK

最终方案优先使用 fixed runner image，并同时满足：

- 镜像内 `dotnet --version` 实测为精确 `10.0.100`；
- 镜像以不可变 digest 锁定并记录构建来源、SBOM/组件信息与复现步骤；
- 不得以 rolling `10.0` SDK tag 冒充精确 SDK；
- 普通路径不得联网 restore；
- `.csproj`、NuGet、MSBuild、编译器参数与 `/unsafe` 继续由服务端合同控制。

## 8. Remote Runner 主路线

用户正式选择 C 方案：Remote Runner Service / 独立远程沙箱。权威架构、信任边界、20 项矩阵、费用与凭据授权边界见 `docs/superpowers/specs/2026-08-29-remote-runner-service-architecture.md`。

Remote Runner 的工具链身份是 exact `.NET SDK 10.0.100` + immutable/pinned image or runtime + digest/hash；`D:\DevTools\dotnet\dotnet.exe` 仅作为本地参考。Hard API 只通过 authenticated encrypted channel 访问 trusted control plane，sandbox 用户代码 `network = NONE`，且不得获得任何 runtime control capability。

## 9. 当前门禁（2026-08-30 覆盖）

- Tier 3-PRE：`HOST_UNSUPPORTED_EDITION`；本机 Windows Container 路线 `STOPPED`。
- Remote Runner / production sandbox：未来多人在线版本强化项，当前停止。
- Task 41-RMT-PRE：`CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE`。
- Task 41：`READY FOR DISPATCH / TRUSTED_LOCAL_LEARNING_ONLY`。
- Task 42–46：等待 Task 41 独立审计与前端门禁。
- Phase G：`FROZEN`。

历史 Tier 3 条件不再是当前 Task 41 前置。若未来开放多人在线、陌生用户或不可信代码执行，必须重新建立和授权本安全项目。
