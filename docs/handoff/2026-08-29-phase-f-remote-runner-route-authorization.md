# Phase F Tier 3 Remote Runner 路线授权登记

> **2026-08-30 覆盖裁决：** `Task 41-RMT-PRE = CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE`。E2B/Remote Runner/Firecracker/hostile-code matrix 全部停止，不得创建 E2B Account/API Key/Sandbox/Template。Remote Runner 仅作为未来多人在线版本安全强化项保留；当前 Task 41 改为 `TRUSTED_LOCAL_LEARNING_ONLY` 的本地 Runner，并已 `READY FOR DISPATCH`。

**登记日期：** 2026-08-29  
**授权人：** 用户  
**登记人：** 策划总控  
**Phase F 基线：** `6246473bf565be308c1505921ec1219beb30803c`

## 正式路线裁决

用户明确选择：**C 方案 — Remote Runner Service / 独立远程沙箱执行**。

Hyper-V-isolated Windows Container 停止作为当前本机主路线推进。历史结论保留：

- `Task 41-PRE = BLOCKED`；
- `Task 41-SBX = BLOCKED`；
- `Tier 3-PRE = HOST_UNSUPPORTED_EDITION`；
- `Task 41 = READY FOR DISPATCH / TRUSTED_LOCAL_LEARNING_ONLY`（2026-08-30 覆盖）；
- `Task 42–46 = FROZEN`；
- `Phase G = FROZEN`。

## 新主路线

```text
Hard API
→ authenticated Runner Client
→ Remote Runner Service trusted control plane
→ per-submission isolated sandbox
→ pinned .NET SDK 10.0.100 runtime/image
→ ephemeral workspace
→ sanitized result
```

本地 Hard API 不直接执行不可信 C#；Remote Runner service unavailable 时必须失败关闭，不得 fallback 到本机普通进程。

## 当前授权

已授权：架构/内部协议设计、短期最小 Remote Runner prototype、必要原型代码、sandbox 验证和安全矩阵。

未自动授权：持续云费用、购买套餐、付费长期服务器、生产凭据、无认证公网端口、正式生产部署或公共 API 变更。涉及 provider/account/token 或付费长期资源时，必须在产生费用或创建资源前重新向用户报告。

## 下一门禁（历史，已取消）

`Task 41-RMT-PRE = CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE`，不得继续下发或执行。

以下原 Task 41 解冻公式已由 2026-08-30 trusted-local 范围裁决覆盖，仅作为未来多人在线版本历史参考：

```text
Task 41-RMT-PRE = PASS
+ Remote Runner Prototype = PASS
+ 独立安全复测 = PASS
+ 同等级 Task 41-PRE remote matrix 复测 = PASS
+ 策划总控正式登记
```
