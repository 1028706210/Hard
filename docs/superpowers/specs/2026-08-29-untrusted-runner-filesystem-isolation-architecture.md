# Untrusted Runner filesystem isolation architecture

**类型：** Phase F 架构安全决策项  
**状态：** TIER 1 / TIER 2 BLOCKED；TIER 3 DECISION REQUIRED  
**登记日期：** 2026-08-29  
**阶段基线：** `6246473bf565be308c1505921ec1219beb30803c`  
**主责：** P001 | AI员工 | Hard架构与管理  
**合同裁决：** 策划总控；最终授权与阶段放行：用户

## 1. 触发原因

Task 41-PRE 已完成并返回 `BLOCKED`。在 Windows 普通用户权限、固定 .NET SDK `10.0.100` 和 Hard 等价进程启动条件下：

- workspace 相对读写：`ALLOW`，符合合同；
- workspace 外访问拒绝：`DENY 0/15`，不符合合同；
- `C:\Windows\win.ini`、`..`、`Path.GetFullPath`、字符串/`char[]`/Base64 构造路径、`System.IO`、`FileStream`、`FileInfo`、`Directory`、Reflection、Delegate、InvokeMember 等访问或绕过均成立。

现有 workspace host-side path validation、cwd/env 控制、timeout、output limit 与 process-tree cleanup 只能约束宿主准备和进程生命周期，不能强制 .NET 子进程只访问 workspace。

本轮 PRE 未修改正式项目文件或 `.git`，未安装软件，未创建 `CSharpRunner`，未产生 commit。

## 2. 决策目标

选择一个可以由 OS / hypervisor / 独立隔离服务真实强制的架构，使不受信任 Runner 进程：

- 可以读写自己的临时 workspace；
- 不能读取、写入或枚举 workspace 外的宿主文件；
- 不能通过路径规范化、编码、全限定 API、Reflection、Delegate、Dynamic 或其他等价方式绕过；
- 保留 timeout、output limit、process-tree cleanup、workspace cleanup 和失败关闭；
- 能在 Hard 的本地优先产品约束下被安装、启动、审计和维护。

## 3. 必须比较并验证的候选

1. **独立/远程隔离 Runner**：Container、VM 或 sandbox service。
2. **Windows AppContainer**。
3. **其他 OS 级方案**：只有能够强制 workspace-only 文件访问的方案才可进入候选。

可以记录其他方案作为拒绝项，但不得仅凭理论描述宣布满足合同。

## 4. 明确不能作为通过依据的措施

- Job Object 单独使用；
- 仅修改 cwd、TEMP、PATH 或其他环境变量；
- host-side path validation；
- 源码关键词扫描、API 黑名单、编码特征扫描；
- 只依赖 Runner timeout、输出限制或进程树清理；
- 未经实验证明的“低权限独立用户 + workspace ACL”。普通低权限用户仍可能读取 `C:\Windows` 等公共可读文件，因此必须证明所有 workspace 外访问被 OS 强制拒绝。

## 5. 候选方案评价矩阵

每个候选至少回答：

- 隔离边界由什么 OS / hypervisor / service 机制强制；
- 对原 PRE 15 个拒绝场景的预期和实际结果；
- Windows 当前版本和 .NET SDK `10.0.100` 的兼容性；
- 是否需要管理员权限、安装、下载、网络、系统策略或防火墙变化；
- workspace 挂载/授权方式以及宿主其他路径为什么不可见或不可读；
- 进程创建、超时、输出限制、进程树终止和残留清理；
- 离线运行、D 盘工具链/数据、性能和并发影响；
- 故障时是否失败关闭；
- 实施范围、公共合同影响、部署和维护成本；
- 可自动化的同等级 PRE-GATE 复测方案。

## 6. 权限和停止条件

本决策项只授权架构比较、只读项目核对和不修改产品实现的安全验证。不得实现 `CSharpRunner`，不得解冻 Task 41，不得修改公共 API 或课程内容。

若验证需要以下任一动作，必须停止并请求用户授权：

- 安装或下载容器、VM、沙箱或 SDK；
- 管理员权限或系统策略变更；
- 防火墙、网络暴露或远程服务账户；
- 修改冻结产品架构或公共合同；
- 正式产品数据、共享工作树或既有 Git 状态变化。

## 7. 架构报告要求

架构与管理 Session 必须返回：

1. 候选方案比较矩阵；
2. 每项验证的环境、方法、原始结果和可复核证据；
3. 推荐方案与明确拒绝方案；
4. 需要用户批准的权限、安装、下载、网络或运维变化；
5. 实施阶段、主责 Session、允许路径和依赖顺序建议；
6. 同等级 Task 41-PRE 复测计划；
7. 结论：`DECISION READY` 或 `BLOCKED`。

## 8. 2026-08-29 Tier 1 / Tier 2 初始候选决策（已被 SBX 实验结果取代）

本节保留 Task 41-SBX 执行前的初始候选路线，供审计父链使用。第 11 节实验结果已经证明该路线在当前主机无有效 Tier 1 / Tier 2 候选，因此本节不得继续被解释为当前推荐方案，也不能视为 `Task 41-PRE PASS`。

推荐的 Hard C# Runner 首选隔离架构为：

```text
Hard API / Runner Manager
→ local sandbox broker
→ AppContainer / LPAC / Windows Sandbox API
→ 最小 ACL / capability
→ dotnet build/run inside temporary workspace
```

真正的安全边界必须来自 Windows OS access check，而不是 `cwd`、`TEMP/TMP`、`PATH`、host-side path validation、Job Object、源码扫描、API 黑名单或字符串/Base64 特征扫描。这些措施只能作为辅助控制。

实现路径优先级：

1. **Tier 1：** 只读探测当前主机是否支持 Windows 官方 Create Process In Sandbox / `Experimental_CreateProcessInSandbox` 能力；若可用，优先用该 API 构造最小 AppContainer sandbox prototype。
2. **Tier 2：** Classic AppContainer / LPAC + local sandbox broker + 最小 ACL 授权。
3. **Tier 3：** Windows container / 本地 VM / Windows Sandbox / Hyper-V 类强隔离方案。Tier 3 如涉及安装系统组件、管理员权限、镜像或系统策略，必须先停止并请求单独授权，不得自行执行。

## 9. Task 41-SBX — Windows Sandbox / AppContainer Prototype Gate

`Task 41-SBX` 是独立安全原型门禁，不是 `CSharpRunner` 实现任务。目标是证明一个真实的 OS 级 workspace-only 隔离原型是否可行。验证顺序必须是最小原生/探针进程、.NET runtime、.NET SDK build。

### 9.1 文件系统授权合同

- workspace：`READ / WRITE`。
- 本次运行专属 `TEMP`：`READ / WRITE`。
- `D:\DevTools\dotnet\`：`READ / EXECUTE ONLY`。
- 必要 runtime / sdk / packs：`READ / EXECUTE ONLY`。
- NuGet/cache：优先 `READ ONLY`；如确需写缓存，必须使用本次运行独享的临时 cache，不允许多个 Submission 共享可写 cache。
- 宿主其他路径：`DENY`。

必须拒绝：`C:\Windows\win.ini`、任意绝对路径、`..` 逃逸、`Path.GetFullPath` 规范化逃逸、字符串拼接路径、`char[]` 构造路径、Base64/编码构造路径、`Environment` + `Path` API、`System.IO` 全限定 API、`FileStream`、`FileInfo`、`Directory`、`DirectoryInfo`、Reflection、Delegate、Dynamic / InvokeMember。

安全判定不能基于 API 名称或源码内容。扫描 `File.ReadAllText`、`System.IO`、`C:\`、`..`、Reflection，或使用正则/AST 黑名单，都不能作为 `PASS` 依据。必须由 Windows OS access check 实际拒绝。

### 9.2 分阶段门禁

- **Gate A — Host capability：** 只读检查 `processmodel.dll`、`Experimental_CreateProcessInSandbox` / 对应 sandbox API、当前 Windows build 支持情况；不得安装组件。若不支持，只标记该实现路径 `UNSUPPORTED_FOR_THIS_PATH`，继续评估 classic AppContainer / LPAC，不直接判整个 Phase F `BLOCKED`。
- **Gate B — Minimal sandbox probe：** 先运行最小探针，不直接进入完整 .NET SDK。必须验证 workspace 内 relative read/write 为 `ALLOW`，workspace 外 `C:\Windows\win.ini` 和 `..` escape 为 `DENY`。
- **Gate C — Full bypass matrix：** 重新执行 Task 41-PRE 同等级安全矩阵，必须达到 `15/15 DENY` + workspace `ALLOW` 全部通过。
- **Gate D — .NET runtime：** 验证 `dotnet app.dll` 可正常运行，同时保证 workspace 外读取仍为 `DENY`。
- **Gate E — .NET SDK：** 固定 `D:\DevTools\dotnet\dotnet.exe` 与 `.NET SDK 10.0.100`，验证受控离线 `dotnet build --no-restore`，同时保持 filesystem isolation 不退化。

### 9.3 网络、Handle 和 Job Object

Sandbox 默认不得授予网络 capability。至少验证 HTTP、TCP、DNS、localhost、`127.0.0.1:8000`、`127.0.0.1:4173`、LAN 均为 `DENY`。除非未来某类受控题目另有正式合同，否则普通 C# Runner 无网络权限。

sandbox broker 启动不受信任进程时默认禁止继承宿主全部 handle，不得使用无约束 `inheritHandles = true`。只允许显式白名单 `stdin`、`stdout`、`stderr` 和必要 IPC handle，不得把文件、socket、token 或其他敏感宿主 handle 泄漏给 sandbox 子进程。

Job Object 可以继续用于 process tree、kill-on-close、timeout、CPU / memory 和 cleanup，但 `Job Object != filesystem isolation`，不能单独作为 `Task 41-SBX PASS` 依据。

“采用 AppContainer”本身不是 `PASS`。只有真实实验满足 workspace `ALLOW`、全部 workspace 外路径 `DENY`、绕过矩阵 `DENY`、网络 `DENY`、handle 不泄漏，才能视为隔离原型通过。必要时应比较 AppContainer 与 LPAC 的实际权限差异。

### 9.4 结论枚举与解冻条件

`Task 41-SBX` 最终结论只能是：

- `PASS`：证明所选 sandbox 实现满足完整安全合同。
- `BLOCKED`：当前可行方案无法满足安全合同，或必须降低门禁。
- `UNSUPPORTED_FOR_THIS_PATH`：仅表示某一具体实现路径当前主机不可用，应继续下一优先级方案。

本节原定的 `Task 41-SBX = PASS` 解冻路径已因 Task 41-SBX 最终 `BLOCKED` 而关闭。新的解冻前提以第 11 节和 Tier 3 决策文件为准：Tier 3 选定、用户正式授权、原型完成、同等级安全矩阵与独立安全复测均 `PASS`，并由策划总控正式登记。

## 10. 当前门禁

- Task 41-PRE：`BLOCKED`。
- Tier 1 Create Process In Sandbox：`UNSUPPORTED_FOR_THIS_PATH`。
- Tier 2 Classic AppContainer：`security contract FAIL`。
- Tier 2 LPAC security contract：`UNPROVEN`；launch path：`UNSUPPORTED_ON_CURRENT_HOST`。
- Task 41-SBX：`BLOCKED`。
- Tier 3-PRE：`HOST_UNSUPPORTED_EDITION`；本机 Windows Container 路线 `STOPPED`。
- Remote Runner / production sandbox：未来多人在线版本强化项，当前停止。
- Task 41-RMT-PRE：`CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE`。
- Task 41：`READY FOR DISPATCH / TRUSTED_LOCAL_LEARNING_ONLY`。
- Task 42–46：等待 Task 41 独立审计与前端门禁。
- Phase G：`FROZEN`。

2026-08-30 产品范围裁决已覆盖上述历史门禁：当前只执行用户本人可信学习代码，Task 41 不再等待生产级 Sandbox。未来多人在线/不可信执行必须重新启用本安全项目。

## 11. Task 41-SBX Gate A / Gate B-DIAG 最终结果

### 11.1 Gate A 与 Tier 1

Gate A 已 `COMPLETE`。当前主机缺少 `processmodel.dll`，Create Process In Sandbox / `Experimental_CreateProcessInSandbox` 对应 API 无法加载，因此 Tier 1 只登记为 `UNSUPPORTED_FOR_THIS_PATH`。

### 11.2 Classic AppContainer

Classic AppContainer 实际结果：workspace relative read/write = `ALLOW`；`..` escape = `DENY`；`Path.GetFullPath` escape = `DENY`；`C:\Windows\win.ini = ALLOW`。

正式结论：Classic AppContainer = `security contract FAIL`，不能满足 Hard 的 workspace-only filesystem isolation 合同。

### 11.3 LPAC Gate B-DIAG

Gate B 初始为 `LAUNCH BLOCKED`。LPAC Launch Viability Diagnostic 已完成，最终 launch path = `UNSUPPORTED_ON_CURRENT_HOST`：

- Microsoft 签名的 `where.exe` / `cmd.exe` 使用 LPAC 创建路径时，`CreateProcessW → ERROR_NOT_SUPPORTED (50)`；
- 相同映像在 Classic AppContainer 下可正常启动；
- 未签名 .NET TinyProbe + LPAC 返回 `ERROR_INVALID_IMAGE_HASH (577)`；
- 官方 attribute 模型已核对：`SECURITY_CAPABILITIES`、`ALL_APPLICATION_PACKAGES_POLICY`、`OPT_OUT=1`、`AttributeCount=2`、`EXTENDED_STARTUPINFO_PRESENT`；结构大小和生命周期已检查；
- capability、appName、Unicode env 等变体不能消除错误 50；
- 未以安装证书、关闭 Code Integrity、修改 Defender、修改系统策略、修改系统目录 ACL、安装 Feature 或提权作为绕过方式。

LPAC security contract = `UNPROVEN`，因为 LPAC 子进程未能启动。该结论不得泛化为 LPAC 技术本身不安全或在所有平台不可用。

### 11.4 最终裁决

Gate C 未启动，Tier 2 没有有效候选。`Task 41-SBX = BLOCKED`。下一步转入独立 Tier 3 架构决策与正式授权门禁。

## 12. Tier 3 外部复核与主机兼容性前置门禁

Tier 3 架构报告外部复核后，保留 Hyper-V-isolated Windows Container 方向。在原型正式下发前新增 `Tier 3-PRE — Windows Container Host Compatibility Gate`，只读核对 Windows Edition、build、Containers / Hyper-V Feature availability、SLAT、BIOS virtualization、RAM 和 Docker Windows-container eligibility。

历史信息 `Build = 22631.6199`、`EditionID = CoreCountrySpecific` 不能替代正式门禁。最终结论只能是 `HOST_SUPPORTED`、`HOST_UNSUPPORTED_EDITION`、`HOST_UNSUPPORTED_HARDWARE`、`HOST_REQUIRES_OS_CHANGE`。任何非 `HOST_SUPPORTED` 结论都禁止安装 runtime、启用 Feature 或处理 image；`HOST_SUPPORTED` 也不自动授权这些变化。

Tier 3 安全合同修订如下：

- 文件系统采用 host filesystem allowlist isolation：只显式允许 per-run workspace、per-run TEMP 和 trusted SDK/toolchain；未 mount 的 host filesystem 必须不可见。container guest image 自身 `C:\Windows` 不属于 host leak。
- 网络必须阻断 host localhost、Hard `8000`、frontend `4173`、LAN 和 Internet；不要求 guest 自身 loopback 消失。
- 最终方案优先 fixed runner image，内含实测精确 `.NET SDK 10.0.100` 并锁定不可变 digest；不得用 rolling `10.0` tag 冒充精确版本。
- Docker Desktop 仅为 prototype runtime 候选；用户代码不得获得 Docker daemon、host named pipe、runtime socket、凭据或 runtime control capability。

完整合同见 `docs/superpowers/plans/2026-08-29-tier3-pre-windows-container-host-compatibility.md`。

## 13. Remote Runner Service 路线切换

Tier 3-PRE 正式返回 `HOST_UNSUPPORTED_EDITION`，Hyper-V-isolated Windows Container 停止作为当前本机主路线。用户正式选择 Remote Runner Service / 独立远程沙箱执行。

安全边界继续采用 host filesystem allowlist isolation + immutable guest runtime，并新增 cross-submission 隔离、authenticated encrypted control-plane channel、sandbox `network = NONE`、hidden-test private injection、sanitized result 和 service unavailable 无本机 fallback。

Task 41-RMT-PRE 已于 2026-08-30 取消；Remote Runner 合同和 20 项计划只保留为未来强化参考。当前下一任务为 `Task 41 = READY FOR DISPATCH / TRUSTED_LOCAL_LEARNING_ONLY`。
