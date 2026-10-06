# Hard Phase F C# 路线正式执行合同

**合同日期：** 2026-08-29  
**正式起始基线：** `6246473bf565be308c1505921ec1219beb30803c`  
**当前状态：** 2026-08-30 产品范围调整为单用户、本地、个人编程学习平台；`Task 41-RMT-PRE = CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE`；Task 41 Trusted Local Learning Runner = `READY FOR DISPATCH`；Task 42–46 等待前序门禁；Phase G = `FROZEN`  
**权威任务栏：** `TASKS.md` 的 Phase F 章节

## 1. 执行边界

本合同固定 Phase F 的门禁、顺序、授权和验收标准。当前威胁模型仅覆盖用户本人编写和信任的本地学习代码，不以 hostile/untrusted code execution 为 Phase F 验收目标。Task 41 必须公开标注 `TRUSTED_LOCAL_LEARNING_ONLY`，不得宣称为恶意代码安全沙箱。

Phase F 的唯一正式起始基线为 `6246473bf565be308c1505921ec1219beb30803c`。任何未来任务包都必须写明其主责、允许路径、起始提交、前置门禁、验证命令、停止条件、独立提交和回报格式。

## 2. 强制顺序

```text
生产级 Sandbox / Remote Runner 历史研究（保留，不再阻塞当前范围）
→ Task 41-RMT-PRE（CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE）
→ Task 41 Trusted Local Learning Runner（READY FOR DISPATCH）
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

不得并行或跳过依赖。任一环节 `BLOCKED`、前序验证失败、出现 P0/P1、发现新公共合同缺口、必须修改未授权文件、要求安装/下载/提权或要求改变冻结架构时，立即停止后续链。Phase G 只有在 Phase F 最终审计完成且用户明确放行后才可解冻。

## 3. Task 41-PRE 安全可行性门禁

### 3.1 目标

在当前 Windows 权限、当前 Hard Runner 基础设施、不安装额外沙箱、不提升管理员权限、不依赖源码关键词扫描的条件下，证明 C# 用户进程能被可靠限制在临时 workspace 内。

### 3.2 必须通过的矩阵

允许：workspace 内相对文件读写。

必须拒绝：

- `C:\Windows\win.ini`；
- 任意绝对路径访问；
- `..` 规范化逃逸；
- `Path.Combine` / `Path.GetFullPath` 后的逃逸；
- 字符串拼接路径；
- Base64 或其他编码构造路径；
- `System.IO` 全限定 API；
- Reflection、Delegate、Dynamic 等间接绕过。

判定依据必须来自 OS / process / sandbox 层强制隔离。源码关键词、API 黑名单或编码特征扫描只能作为补充诊断，不能成为门禁通过依据。

### 3.3 结论与后果

结论只能是 `PASS` 或 `BLOCKED`：

- `PASS`：完整矩阵通过且机制、环境、原始输出和失败关闭证据可复核；Task 41 才具备下发资格。
- `BLOCKED`：现有基础设施无法可靠隔离 hostile/untrusted code；该历史结论继续有效，但不再阻塞 2026-08-30 明确限定的 trusted-local 当前范围。

### 3.4 2026-08-29 正式执行结果

`Task 41-PRE = BLOCKED`。

验证环境为 Windows 普通用户权限、固定 .NET SDK `10.0.100` 和 Hard 等价进程启动条件。workspace 相对读写按合同为 `ALLOW`；15 个应拒绝场景中，实际 `DENY = 0/15`：

- `C:\Windows\win.ini` 可读；
- `..` 与 `Path.GetFullPath` 规范化逃逸成立；
- 字符串、`char[]`、Base64 构造绝对路径可访问；
- `System.IO` 全限定 API、`FileStream`、`FileInfo`、`Directory` 可访问；
- Reflection、Delegate、InvokeMember 等间接调用可绕过。

现有 workspace host-side path validation、cwd/env 控制、timeout、output limit 和 process-tree cleanup 都不是 .NET 子进程的文件系统权限边界。本轮未修改正式项目文件或 `.git`、未安装软件、未创建 `CSharpRunner`、未产生 commit。

该结果曾冻结 Task 41 和后续链；2026-08-30 用户将当前产品范围调整为 trusted-local 后，Task 41 已另行解冻。该安全结果仍约束未来多人在线/不可信代码版本。

## 3A. Phase F 架构安全决策项（历史，当前不阻塞）

决策项名称：**Untrusted Runner filesystem isolation architecture**。

唯一主责为架构与管理 Session，策划总控只在需要冻结合同、权限或阶段范围裁决时参与。必须至少比较并验证：

1. 独立/远程隔离 Runner：Container、VM 或 sandbox service；
2. Windows AppContainer；
3. 其他能由 OS 强制 workspace-only 文件访问的方案。

Job Object 单独、cwd/TEMP/PATH、源码扫描/API 黑名单不能作为文件系统隔离。“低权限独立用户 + workspace ACL”不得凭理论推断通过，必须实验证明所有 workspace 外访问均被拒绝，包括 `C:\Windows` 等通常对普通用户可读的路径。

以下内容是 Task 41-SBX 执行前登记的 Tier 1 / Tier 2 初始候选架构，现已被 Gate A / Gate B-DIAG 结果取代，不再是当前可实施推荐：

```text
Hard API / Runner Manager
→ local sandbox broker
→ AppContainer / LPAC / Windows Sandbox API
→ 最小 ACL / capability
→ dotnet build/run inside temporary workspace
```

真正安全边界必须来自 Windows OS access check；`cwd`、`TEMP/TMP`、`PATH`、host-side path validation、Job Object、源码扫描、API 黑名单、字符串/Base64 特征扫描只能作为辅助控制，不能作为文件系统隔离依据。

实现路径优先级固定如下：

1. Tier 1：优先只读探测当前主机是否支持 Windows 官方 Create Process In Sandbox / `Experimental_CreateProcessInSandbox` 能力；若可用，优先用该 API 构造最小 AppContainer sandbox prototype。
2. Tier 2：Classic AppContainer / LPAC + local sandbox broker + 最小 ACL 授权。
3. Tier 3：Hyper-V-isolated Windows Container 方向经外部复核保留；原型前必须先执行独立只读 Tier 3-PRE 主机兼容性门禁。任何非 `HOST_SUPPORTED` 结论都禁止安装 runtime、启用 Feature 或处理 image。

## 3B. Task 41-SBX 安全原型门禁（历史，当前不阻塞）

`Task 41-SBX — Windows Sandbox / AppContainer Prototype Gate` 是独立安全原型门禁，不是 `CSharpRunner` 实现任务。

目标是证明一个真实的 OS 级 workspace-only 隔离原型是否可行。必须先验证最小原生/探针进程，再验证 .NET runtime，最后验证固定 .NET SDK build。

### 3B.1 文件系统授权合同

- workspace：`READ / WRITE`。
- 本次运行专属 `TEMP`：`READ / WRITE`。
- `D:\DevTools\dotnet\`：`READ / EXECUTE ONLY`。
- 必要 runtime / sdk / packs：`READ / EXECUTE ONLY`。
- NuGet/cache：优先 `READ ONLY`；如确需写缓存，必须使用本次运行独享的临时 cache，不允许多个 Submission 共享可写 cache。
- 宿主其他路径：`DENY`。

必须拒绝 `C:\Windows\win.ini`、任意绝对路径、`..` 逃逸、`Path.GetFullPath` 规范化逃逸、字符串拼接路径、`char[]` 构造路径、Base64/编码构造路径、`Environment` + `Path` API、`System.IO` 全限定 API、`FileStream`、`FileInfo`、`Directory`、`DirectoryInfo`、Reflection、Delegate、Dynamic / InvokeMember。

以下不能作为 `PASS` 依据：扫描 `File.ReadAllText`、扫描 `System.IO`、扫描 `C:\`、扫描 `..`、扫描 Reflection、正则/AST 黑名单。必须由 Windows OS access check 实际拒绝。

### 3B.2 分阶段门禁

- Gate A — Host capability：只读检查 `processmodel.dll`、`Experimental_CreateProcessInSandbox` / 对应 sandbox API、当前 Windows build 支持情况；不得安装组件。若不支持，只标记该实现路径 `UNSUPPORTED_FOR_THIS_PATH`，继续评估 classic AppContainer / LPAC。
- Gate B — Minimal sandbox probe：先运行最小探针，不直接进入完整 .NET SDK。workspace 内 relative read/write 必须为 `ALLOW`；`C:\Windows\win.ini` 和 `..` escape 必须为 `DENY`。
- Gate C — Full bypass matrix：重新执行 Task 41-PRE 同等级安全矩阵，必须达到 `15/15 DENY` + workspace `ALLOW` 全部通过。
- Gate D — .NET runtime：验证 `dotnet app.dll` 可正常运行，同时 workspace 外读取仍为 `DENY`。
- Gate E — .NET SDK：固定 `D:\DevTools\dotnet\dotnet.exe` 与 `.NET SDK 10.0.100`，验证受控离线 `dotnet build --no-restore`，同时保持 filesystem isolation 不退化。

### 3B.3 网络、Handle 与 Job Object

Sandbox 默认不得授予网络 capability。至少验证 HTTP、TCP、DNS、localhost、`127.0.0.1:8000`、`127.0.0.1:4173`、LAN 均为 `DENY`。除非未来某类受控题目另有正式合同，否则普通 C# Runner 无网络权限。

sandbox broker 启动不受信任进程时，默认禁止继承宿主全部 handle，不得使用无约束 `inheritHandles = true`。只允许显式白名单 `stdin`、`stdout`、`stderr` 和必要 IPC handle；不得把文件、socket、token 或其他敏感宿主 handle 泄漏给 sandbox 子进程。

Job Object 可以继续用于 process tree、kill-on-close、timeout、CPU / memory 和 cleanup，但 `Job Object != filesystem isolation`，不能单独作为 `Task 41-SBX PASS` 依据。

普通 AppContainer 不能自动视为 workspace-only。“采用 AppContainer”本身不是 `PASS`。只有真实实验满足 workspace `ALLOW`、全部 workspace 外路径 `DENY`、绕过矩阵 `DENY`、网络 `DENY`、handle 不泄漏，才能视为隔离原型通过。必要时应比较 AppContainer 与 LPAC 的实际权限差异。

### 3B.4 结论和 Task 41 解冻条件

`Task 41-SBX` 最终结论只能是：

- `PASS`：证明所选 sandbox 实现满足完整安全合同。
- `BLOCKED`：当前可行方案无法满足安全合同，或必须降低门禁。
- `UNSUPPORTED_FOR_THIS_PATH`：仅表示某一具体实现路径当前主机不可用，应继续下一优先级方案。

### 3B.5 Gate A / Gate B-DIAG 最终结果

- Gate A：`COMPLETE`。
- Tier 1 Create Process In Sandbox / `Experimental_CreateProcessInSandbox`：`UNSUPPORTED_FOR_THIS_PATH`，原因是当前主机缺少 `processmodel.dll`，API 无法加载。
- Tier 2 Classic AppContainer：`security contract FAIL`。workspace relative read/write、`..` 与 `Path.GetFullPath` 的局部边界有效，但 `C:\Windows\win.ini = ALLOW`，不满足 workspace-only 合同。
- Tier 2 LPAC Gate B-DIAG：`COMPLETE`；LPAC launch path = `UNSUPPORTED_ON_CURRENT_HOST`。
- Microsoft 签名 `where.exe` / `cmd.exe` 在 LPAC `CreateProcessW` 返回 `ERROR_NOT_SUPPORTED (50)`，相同映像可在 Classic AppContainer 启动。
- 未签名 .NET TinyProbe + LPAC 返回 `ERROR_INVALID_IMAGE_HASH (577)`。
- 官方 LPAC attribute 模型、结构大小、生命周期以及 capability/appName/Unicode env 变体已核对，仍不能消除错误 50。
- 未安装证书，未关闭 Code Integrity，未修改 Defender、系统策略、系统目录 ACL，未安装 Feature，也未把提权作为最终依赖。
- Gate C 未进入；Tier 2 无有效候选。

正式措辞：LPAC security contract = `UNPROVEN`，原因是 LPAC 子进程未能启动；不得泛化为 LPAC 技术本身不安全或全平台不可用。

`Task 41-SBX = BLOCKED`。该历史结论证明当前主机不具备 hostile-code sandbox；2026-08-30 trusted-local 范围裁决后，它不再是当前 Task 41 前置条件。

## 3C. Tier 3 架构与授权门禁（未来多人在线版本强化项）

策划总控与架构与管理 Session 必须共同比较：隔离 Runner Service / Remote Sandbox、Windows Container、本地 VM / Hyper-V、Windows Sandbox 类方案。

用户已于 2026-08-29 授权进入 Tier 3。Tier 3-PRE 最终返回 `HOST_UNSUPPORTED_EDITION`，因此 Hyper-V-isolated Windows Container 作为本机当前主路线停止推进；不得继续安装本机 runtime、启用 Containers/Hyper-V 或处理 Windows container image。

用户随后正式选择 C 方案：Remote Runner Service / 独立远程沙箱。新的执行链从 `Task 41-RMT-PRE` 开始，不再依赖本机 Windows Container capability。

历史 Tier 3-PRE 合同和 `HOST_UNSUPPORTED_EDITION` 结果继续保留，不能删除或改写为成功。Remote Runner 权威合同见 `docs/superpowers/specs/2026-08-29-remote-runner-service-architecture.md`。

### 3C.1 Remote Runner host filesystem allowlist

Remote Runner 的文件系统合同为 host filesystem allowlist isolation + immutable guest runtime：

- 允许 per-run workspace / TEMP 读写；
- 允许固定只读 runtime、SDK、framework 和 immutable image 基础文件；
- remote host 未授权文件、host secrets、其他 submission workspace 和 shared writable cache 必须不可见；
- 用户代码不得获得 runtime/container control socket、named pipe、凭据或 control-plane capability。

### 3C.2 Tier 3 网络合同

Hard API 只通过 authenticated encrypted service channel 访问 Remote Runner trusted control plane。Sandbox 用户代码 `network = NONE`，必须无法到达 Internet、LAN、Hard API、host localhost service、metadata service、control plane 或 runtime API。Sandbox 自身 loopback 可以存在，但不得绕过上述边界。

### 3C.3 Fixed runner image

Remote Runner 必须实测精确 `.NET SDK 10.0.100`，使用 immutable/pinned image or runtime 并记录 digest/hash。禁止 floating SDK tag。`D:\DevTools\dotnet\dotnet.exe` 只作为本地参考，Remote Runner 不要求相同盘符或目录。

## 3D. Task 41-RMT-PRE Remote Runner Viability Gate（已取消）

正式状态：`CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE`。停止 E2B、Remote Runner、Firecracker、20 项 hostile-code matrix、cross-submission、host-secret、control-plane/runtime-socket 和 hostile path bypass 工作。不得创建 E2B Account/API Key/Sandbox/Template。历史计划保留供未来多人在线版本重新授权时参考。

## 4. Task 41 — C# Runner / Trusted Local Learning Environment

### 4.0 范围与非安全声明

- 产品范围：单用户、本地、个人编程学习平台。
- 当前只运行用户本人编写和信任的学习代码。
- 标识：`TRUSTED_LOCAL_LEARNING_ONLY`。
- 本 Runner 不是 hostile/untrusted code 安全沙箱。
- 不得宣称可安全运行陌生用户、恶意代码或不可信第三方代码。
- 未来开放多人在线执行时，必须重新启用独立 Sandbox / Remote Runner 安全项目。

### 4.1 工具链与离线构建

- 固定本地工具链：`D:\DevTools\dotnet\dotnet.exe`，实际 SDK 必须精确为 `10.0.100`；缺失或错误版本必须显式失败，不得自动安装、下载或切换。
- 至少设置：`DOTNET_CLI_TELEMETRY_OPTOUT=1`、`DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1`、`DOTNET_NOLOGO=1`。
- `NUGET_PACKAGES` 必须指向 D 盘受控目录。
- `.csproj` 完全由服务端生成和控制。
- 用户不得提供 `.csproj`、`PackageReference`、NuGet Source、MSBuild 参数、编译器参数、`Import`、`Exec`、`UsingTask` 或自定义项目路径。
- 普通执行路径不得联网 restore；优先使用固定离线模板与 `--no-restore`，依赖不完整时失败关闭。
- 必须覆盖 compile/run、top-level statements、标准 `Program/Main`、per-run workspace、stdin、UTF-8、stdout/stderr、compile/runtime error、hidden tests、timeout、output limit、process-tree/workspace cleanup、RunnerManager queue/cancel 和既有 Python/Java 回归。

### 4.2 `/unsafe` 内部 capability

- 普通 C# Exercise 固定 `allow_unsafe = false`。
- 只有服务端私有 Exercise Metadata / 内部 allowlist 可以设置 `allow_unsafe = true`。
- 用户 Submission 不得提供该字段，前端不得展示或控制该字段。
- 不得因为源码出现 `unsafe` 自动开启。
- 用户不得通过 `.csproj`、MSBuild 参数或编译器参数开启。
- Runner 必须预留该服务端内部 capability，但默认永远关闭并失败关闭。

## 5. 前端语言合同

Monaco/编辑器语言映射必须显式为：

```text
python → python
java → java
csharp → csharp
```

未知语言不得继续伪装为 Python；使用 `plaintext` 或现有产品合同明确规定的 unsupported fallback。前端不得提供 `allow_unsafe`、`.csproj`、NuGet、MSBuild 或编译器参数控制入口。上述行为必须在前端独立验收中被复核，验收通过后才允许进入 Task 42。

## 6. C# 来源归属合同

- 普通 `+`、`-`、`*`、`/`、`%` 运算符基础知识唯一归属 Task 42 / `csharp-foundations`。
- 用户自定义 `operator overload` 唯一归属 Task 43 / `csharp-oop`。
- 同一来源不得重复收录或生成两个 lesson，C# source coverage 必须 `unassigned == 0` 且每个来源恰好归属一次。
- 内容执行 Agent 无权自行改变该归属。
- 当前 `content/sources.yaml` 的实际映射调整属于后续经授权的内容任务，不在本次仅规划修订中修改；必须在 C# 内容统一验收前完成并验证。

## 7. 独立验收与最终放行

- Task 41 完成后，测试与审计 Session 必须独立复核本地固定 SDK、离线构建、项目/参数注入禁止、Runner 生命周期、`allow_unsafe`、隐藏测试保密、Python/Java 回归和 `TRUSTED_LOCAL_LEARNING_ONLY` 声明。不得把历史 hostile-code PRE 矩阵作为当前 PASS 前置条件。
- 前端兼容门禁完成后，测试与审计 Session 必须独立验收显式映射、未知语言 fallback 和不可控的 `allow_unsafe`。
- Task 42–46 必须按顺序独立实现、验证、记录和提交。
- 内容统一验收核对来源、模块、lesson、exercise、参考解、运算符归属、`allow_unsafe` 和 100% 覆盖。
- Phase F 完整 E2E 只能由测试与审计 Session 启动。
- 策划总控只汇总证据、维护基线和门禁；最终阶段放行由用户决定。

## 8. 当前放行状态

- `Task 41-PRE`：**BLOCKED（DENY 合同 0/15 通过）**。
- Tier 1 / Tier 2 架构验证：**COMPLETE；无可进入 Gate C 的有效候选**。
- Task 41-SBX：**BLOCKED**。
- Tier 3-PRE：**HOST_UNSUPPORTED_EDITION；本机 Windows Container 路线停止**。
- Remote Runner / production sandbox：**未来多人在线版本安全强化项；当前停止**。
- Task 41-RMT-PRE：**CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE**。
- Task 41：**READY FOR DISPATCH — Trusted Local Learning Environment**。
- Task 42–46：**等待 Task 41 独立审计和前端门禁，不提前开始**。
- Phase G：**FROZEN**。
