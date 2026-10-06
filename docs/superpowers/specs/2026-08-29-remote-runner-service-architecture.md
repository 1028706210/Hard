# Untrusted C# Remote Runner Service Architecture

**类型：** Phase F Tier 3 当前权威主路线  
**状态：** CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE  
**登记日期：** 2026-08-29  
**正式起始基线：** `6246473bf565be308c1505921ec1219beb30803c`  
**路线选择人：** 用户  
**门禁维护：** 策划总控

> **2026-08-30 范围覆盖裁决：** Hard 当前是单用户、本地、个人编程学习平台，仅执行用户本人编写和信任的学习代码。停止 E2B/Remote Runner/Firecracker 原型与 hostile-code matrix；不得创建 E2B Account/API Key/Sandbox/Template。本文件保留为未来多人在线/不可信代码版本的安全强化参考，不再阻塞当前 Phase F。

## 1. 路线裁决

用户正式选择 **C 方案 — Remote Runner Service / 独立远程沙箱执行**。

```text
Hard API
→ authenticated Runner Client
→ Remote Runner Service trusted control plane
→ per-submission isolated sandbox
→ pinned .NET SDK 10.0.100 runtime/image
→ ephemeral workspace
→ sanitized result
```

Hyper-V-isolated Windows Container 停止作为当前本机主路线推进。相关历史实验和合同保留为审计证据，不删除、不改写为成功：

- `Task 41-PRE = BLOCKED`；
- `Task 41-SBX = BLOCKED`；
- `Tier 3-PRE = HOST_UNSUPPORTED_EDITION`；
- 本机 Windows Container prototype 路线：`STOPPED / NOT AUTHORIZED TO CONTINUE`。

## 2. 信任边界

本地 Hard API 不再直接执行不可信 C#。用户源码、输入和受控 hidden-test payload 只能通过经过认证和加密的服务通道进入 Remote Runner trusted control plane，再由控制面注入一次性 sandbox。

远程 sandbox 不得获得：

- 用户本机文件系统、用户主目录或 Hard 项目目录；
- `.git`；
- 本地账号、token、cookie、SSH key 或其他凭据；
- 正式 `data`、`backups`、`exports`；
- Hard 数据库直接权限；
- Docker/container runtime socket、named pipe、daemon API、orchestrator token 或控制面凭据；
- 其他 submission 的 workspace 或可写缓存。

Remote Runner trusted control plane 与 untrusted sandbox 是两个不同信任域。控制面可接收经过认证的任务、注入私有测试并清洗结果；sandbox 不能调用或控制控制面。

## 3. 文件系统合同

正式边界是 **host filesystem allowlist isolation + immutable guest runtime**。

Sandbox 内允许：

- per-run workspace：`READ / WRITE`；
- per-run TEMP：`READ / WRITE`；
- 固定 runtime / SDK / framework：`READ / EXECUTE`；
- immutable sandbox image 基础文件：`READ / EXECUTE`。

必须拒绝：

- remote host 未授权文件和 host secret sentinel；
- 其他 submission workspace；
- host credential、metadata、control-plane secret；
- runtime control socket / named pipe / daemon API；
- shared writable NuGet、build 或临时 cache；
- 未显式 allowlist 的 host mount、volume、device 和 handle。

每个 submission 必须使用不同的 sandbox 身份、workspace 和 TEMP。销毁后不得被后续 submission 重新挂载或恢复。必须执行 A 写入、B 读取的 cross-submission isolation 测试。

## 4. .NET 工具链身份

- 精确版本：`.NET SDK 10.0.100`；
- 工具链来自 immutable/pinned image 或 runtime；
- 必须记录 image digest 或等价不可变 hash；
- `dotnet --version` 必须在 sandbox 内实测为 `10.0.100`；
- 禁止 floating / rolling SDK tag；
- 普通构建使用受控项目模板与 `dotnet build --no-restore`；
- 不允许 sandbox 联网 restore；
- `/unsafe`、`.csproj`、NuGet、MSBuild 和编译器参数继续遵守既有服务端控制合同。

`D:\DevTools\dotnet\dotnet.exe` 仅保留为本地工具链参考，不是 Remote Runner 路径合同，也不得要求远程环境复制该盘符或目录布局。

## 5. 网络与服务通道

### 5.1 允许的控制面通道

Hard API → Remote Runner Service 只允许使用明确认证、加密、可撤销、可审计的服务通道。原型至少要求 TLS 和服务身份认证；不得暴露无认证公网端口。任务 ID 必须不可预测，认证失败、重放、过期或篡改请求必须失败关闭。

### 5.2 Sandbox 网络

用户代码 `network = NONE`，必须无法访问：

- Internet；
- remote host / LAN；
- Hard API；
- host localhost services；
- cloud metadata service；
- Remote Runner control plane；
- runtime / orchestration API。

Sandbox 自身 loopback 可以存在，但不得路由到宿主控制面、metadata、LAN 或 Internet。

## 6. Hidden Test 与结果清洗

Hidden Test 和 Reference Solution 永远不进入 Hard frontend 或公共 API。

允许的私有路径是：

```text
Hard API
→ authenticated encrypted channel
→ Remote Runner trusted control plane
→ private per-run sandbox injection
```

Sandbox 完成或失败后立即销毁。公共 API 只能接收并返回经过清洗的：

- `status`；
- `stdout` / `stderr` safe subset；
- sanitized diagnostics；
- test result。

禁止泄露 hidden-test 内容、reference solution、remote host path、image internals、control-plane endpoint、credential、token、stack trace secret 或其他 submission 数据。

## 7. Task 41-RMT-PRE — Remote Runner Viability Gate

该 Gate 不是 `CSharpRunner` 实现，不修改正式公共 API 合同。它可以创建隔离原型、必要原型代码、fixtures 和安全证据，但不得把原型凭据或 provider 资源写入正式项目数据。

必须验证：

1. Remote sandbox 能创建和销毁；
2. sandbox 内 SDK 精确等于 `10.0.100`；
3. Hello World 可 build/run；
4. `dotnet build --no-restore` 成功；
5. per-run workspace 可读写；
6. remote host filesystem 未授权部分不可见；
7. host secret sentinel 为 `DENY`；
8. submission A 不能读取 submission B；
9. Internet/LAN/host network 为 `DENY`；
10. Hard API / trusted control plane 为 `DENY`；
11. runtime/container socket 为 `DENY`；
12. timeout 生效；
13. output limit 生效；
14. process tree cleanup 生效；
15. workspace/TEMP cleanup 生效；
16. hidden test 不泄露；
17. diagnostics 不泄露 remote host path；
18. 至少 2 个并发 submission 彼此隔离且可完成；
19. failed job 失败关闭；
20. service unavailable 时不得 fallback 到本机普通进程。

Task 41-PRE 原始路径绕过矩阵必须在 remote host sentinel / mount 边界上做同等级复测，包括绝对路径、`..`、规范化、编码构造、`System.IO`、Reflection、Delegate 和 Dynamic。不能用源码扫描或 API 黑名单代替 sandbox 强制边界。

## 8. 停止条件

以下任一项出现，立即停止并登记 `Task 41-RMT-PRE = BLOCKED`：

- 用户代码读取 remote host secret；
- cross-submission 数据泄漏；
- sandbox 接触 runtime control socket；
- sandbox 访问 Hard API 或 Remote Runner control plane；
- sandbox 可访问 Internet 或未授权 LAN；
- hidden test / reference solution 泄漏；
- 必须 fallback 到本机普通进程；
- 必须降低原安全合同；
- 只有通过未授权付费、长期资源、生产凭据或无认证公网端口才能继续；
- 证据缺失、清理不可证明或失败未关闭。

## 9. 产品体验与成本证据

原型必须记录每次运行和至少 2 并发场景的：

- sandbox 创建耗时；
- build/run 耗时；
- total latency；
- cleanup 时间；
- CPU / memory / storage 等资源摘要；
- 单次运行大致资源成本及计价假设；
- service unavailable 的用户可见错误与重试边界。

性能数字不降低安全门禁；无法获得可信成本或计价信息必须登记为付费决策前证据缺口。

## 10. 授权边界

当前已授权：

- 架构和内部协议设计；
- Remote Runner 短期、最小、可回收 prototype；
- 最小 sandbox 验证；
- 必要原型代码、fixtures 和安全矩阵；
- 不产生持续费用的临时资源使用。

当前未自动授权：

- 产生持续云费用或购买套餐；
- 创建付费长期服务器、长期公网 IP、持久卷或常驻服务；
- 写入真实生产凭据、用户 token 或正式数据库；
- 暴露无认证公网端口；
- 把 prototype 直接作为生产环境；
- 修改正式公共 API 或解冻 Task 41。

若可行候选要求 provider account、token、付费资源或长期基础设施，必须在产生费用或创建资源前停止并向用户提交 provider、费用、区域、数据处理、凭据、销毁和替代方案清单。

## 11. 结论与解冻条件（历史，当前已被范围裁决覆盖）

Task 41-RMT-PRE 结论只能是 `PASS` 或 `BLOCKED`。

Task 41 只有在以下条件同时成立后才能由策划总控登记为 `READY FOR DISPATCH`：

```text
Task 41-RMT-PRE = PASS
+ Remote Runner Prototype = PASS
+ 独立安全复测 = PASS
+ 同等级 Task 41-PRE remote matrix 复测 = PASS
+ 策划总控正式登记
```

上述公式仅适用于未来 hostile/untrusted 或多人在线执行版本。当前 trusted-local Task 41 已 `READY FOR DISPATCH`；Task 42–46 仍等待 Task 41 独立审计和前端门禁，Phase G 继续 `FROZEN`。

## 12. 专业会话边界（历史，不再执行）

- Task 41-RMT-PRE 主责：部署与运维 Session；只在正式下发后执行原型和环境证据。
- 架构合同复核：架构与管理 Session；只核对协议、信任边界和 provider / resource 决策，不替代原型执行。
- 独立安全复测：测试与审计 Session；只在 prototype 报告完成后定向下发。
- 后端、前端、内容与课程：当前不接收 Remote Runner prototype 任务，继续冻结各自 Phase F 实施。
