# Phase F Tier 3 授权与 Tier 3-PRE 修订登记

**授权日期：** 2026-08-29  
**授权人：** 用户  
**登记人：** 策划总控  
**基线：** `6246473bf565be308c1505921ec1219beb30803c`

> **当前覆盖裁决：** 2026-08-30 用户将当前范围调整为单用户可信本地学习代码；Remote Runner 与生产级 Sandbox 不再阻塞 Phase F，Task 41-RMT-PRE 已取消。以下内容仅为历史授权与审计记录。

## 授权决定

用户明确授权进入 Tier 3。

本授权允许策划总控与架构与管理 Session：

1. 完成 Tier 3 候选比较；
2. 选择一个推荐方案；
3. 为该方案形成一个最小、可回滚、可审计的原型任务包；
4. 明确所需 Windows Feature、管理员权限、镜像、下载、网络、系统策略、新基础设施、命令、回滚和证据；
5. 确定原型主责 Session 与独立安全复测 Session。

## 执行边界

- 当前不解冻 Task 41、Task 42–46 或 Phase G。
- 当前不允许在未选型时同时安装或实施多个 Tier 3 候选。
- 架构与管理 Session 不直接替代专业实施 Session 修改产品代码或机器环境。
- 选定方案的实际执行必须使用精确任务包，并接受系统运行时审批。
- 禁止关闭 Code Integrity、Defender 或其他安全能力。
- 禁止无边界网络暴露、无回滚系统变化或放宽 workspace-only 合同。

## 外部复核后的架构方向

Tier 3 架构报告外部复核后，Hyper-V-isolated Windows Container 方向保留。但当前历史主机信息为 `Build = 22631.6199`、`EditionID = CoreCountrySpecific`，客户端 Windows containers 的 Edition 支持资格尚未形成正式只读证据。

因此原型前新增 `Tier 3-PRE — Windows Container Host Compatibility Gate`。该门禁只读核对 Edition、build、Containers / Hyper-V Feature availability、SLAT、BIOS virtualization、RAM 和 Docker Windows-container eligibility；不得安装 Docker、启用 Feature 或处理 image。

结论只能是 `HOST_SUPPORTED`、`HOST_UNSUPPORTED_EDITION`、`HOST_UNSUPPORTED_HARDWARE`、`HOST_REQUIRES_OS_CHANGE`。任何非 `HOST_SUPPORTED` 结论都禁止原型环境变化；`HOST_SUPPORTED` 也只允许进入下一道独立授权门禁。

Tier 3 安全合同同步修订为 host filesystem allowlist isolation、host/LAN/Internet 网络隔离、精确 .NET SDK `10.0.100` fixed image + locked digest，以及用户代码禁止 Docker daemon / named pipe / runtime control capability。

## 下一门禁

Tier 3-PRE 后续已返回 `HOST_UNSUPPORTED_EDITION`，本机 Hyper-V-isolated Windows Container 路线停止。Remote Runner 随后也因 2026-08-30 trusted-local 范围裁决取消；当前下一任务是 `Task 41 = READY FOR DISPATCH / TRUSTED_LOCAL_LEARNING_ONLY`。

原型必须通过与 Task 41-PRE / Task 41-SBX 同等级的文件系统、路径绕过、网络、handle/IPC、进程清理和 .NET 运行矩阵。通过前不得解冻 Task 41。
