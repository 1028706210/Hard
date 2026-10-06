# Tier 3-PRE Host Compatibility Gate 登记

**登记日期：** 2026-08-29  
**登记人：** 策划总控  
**来源：** Tier 3 架构报告外部复核  
**Phase F 基线：** `6246473bf565be308c1505921ec1219beb30803c`

## 外部复核结论

- Hyper-V-isolated Windows Container 当时作为候选方向保留；后续 Tier 3-PRE 已返回 `HOST_UNSUPPORTED_EDITION`，当前本机主路线已停止。
- 当前不得直接下发 Tier 3 原型。
- 原型之前新增 `Tier 3-PRE — Windows Container Host Compatibility Gate`。
- 历史主机信息 `Build = 22631.6199`、`EditionID = CoreCountrySpecific` 必须只读复核；不得把历史值直接当作最终门禁结论。
- 客户端 Windows 的 Windows containers 需要受支持的 Windows Edition。若正式核对确认当前 Edition 属于 Home 类，门禁应返回 `HOST_UNSUPPORTED_EDITION`。

## 已冻结的安全合同修订

### Host filesystem allowlist isolation

Tier 3 的文件边界从笼统“workspace-only”修订为宿主文件系统 allowlist：

- 允许挂载 per-run workspace；
- 允许挂载 per-run TEMP；
- 允许显式授权且只读/只执行的 trusted SDK/toolchain；
- 未显式 mount 的 host filesystem 必须不可见；
- container guest image 自身的 `C:\Windows` 不属于 host filesystem leak；
- 禁止 Docker daemon、host named pipe、runtime socket、宿主凭据或其他 runtime control capability 进入用户代码容器。

### Network isolation

用户代码必须无法到达：

- host localhost；
- Hard API `8000`；
- frontend `4173`；
- LAN；
- Internet。

不要求 container guest 自身 loopback 消失，但 guest loopback 不得成为访问 host 或外网的旁路。

### Fixed .NET SDK image

- 最终方案优先使用 fixed runner image；
- 镜像内必须实测精确 `.NET SDK 10.0.100`；
- 最终镜像必须锁定不可变 digest；
- 不得用 rolling `10.0` SDK tag 冒充 `10.0.100`；
- build 与 run 路径必须离线、失败关闭，并保持服务端控制的项目文件和 `/unsafe` 合同。

## 当前门禁状态

- Tier 3-PRE：`HOST_UNSUPPORTED_EDITION`，已完成。
- 本机 Hyper-V-isolated Windows Container 路线：`STOPPED`。
- Remote Runner/production sandbox：未来多人在线版本安全强化项，当前停止。
- Task 41-RMT-PRE：`CANCELLED_AS_NOT_REQUIRED_FOR_CURRENT_PRODUCT_SCOPE`。
- Task 41：`READY FOR DISPATCH / TRUSTED_LOCAL_LEARNING_ONLY`。
- Tier 3 prototype：`FROZEN`。
- Task 41：`READY FOR DISPATCH / TRUSTED_LOCAL_LEARNING_ONLY`。
- Task 42–46：`FROZEN`。
- Phase G：`FROZEN`。

Tier 3-PRE 未返回 `HOST_SUPPORTED`，因此本机 container runtime、Feature 和 image 动作继续禁止。当前可信本地 Task 41 不再依赖生产级 Sandbox；未来多人在线/不可信执行必须重启独立安全项目。
