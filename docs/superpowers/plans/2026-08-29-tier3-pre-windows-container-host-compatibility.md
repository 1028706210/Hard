# Tier 3-PRE — Windows Container Host Compatibility Gate

**类型：** Phase F / Tier 3 原型前置只读门禁  
**状态：** COMPLETE / HOST_UNSUPPORTED_EDITION / LOCAL ROUTE STOPPED  
**登记日期：** 2026-08-29  
**正式起始基线：** `6246473bf565be308c1505921ec1219beb30803c`  
**推荐架构方向：** Hyper-V-isolated Windows Container  
**主责：** P001 | AI员工 | Hard部署与运维  
**合同复核：** P001 | AI员工 | Hard架构与管理  
**门禁登记：** 策划总控

## 1. 目的

在安装 Docker Desktop 或其他 container runtime、启用 Containers / Hyper-V、下载或构建镜像、修改系统策略之前，只读判断当前 Windows 主机是否具备运行 Hyper-V-isolated Windows Container 原型的资格。

历史只读信息显示当前主机可能为：

```text
Build = 22631.6199
EditionID = CoreCountrySpecific
```

该信息是门禁输入线索，不替代本门禁的正式证据。客户端 Windows 的 Windows containers 支持范围、Windows Feature 可用性与硬件虚拟化能力必须在同一份报告中重新核对。

## 2. 绝对执行边界

本门禁只允许读取和报告主机状态。禁止：

- 安装 Docker Desktop、Docker Engine、containerd 或其他 runtime；
- 启用或禁用 Containers、Hyper-V、Virtual Machine Platform、WSL 或其他 Windows Feature；
- 下载、拉取、构建、导入或运行任何 container image；
- 创建 VM、container、虚拟交换机、网络、服务、账户或计划任务；
- 修改 BIOS / UEFI、系统策略、注册表、BCD、防火墙、Defender、Code Integrity 或 ACL；
- 请求重启、提权后变更系统，或把管理员权限用于写入操作；
- 修改产品源码、创建 Phase F 实现工作树、实现 `CSharpRunner`；
- 用 Docker 当前是否已安装替代 Windows-container eligibility 判定。

只读查询因权限不足而无法取得权威结果时，不得猜测为 `HOST_SUPPORTED`。

## 3. 必须收集的证据

### 3.1 Windows 版本与版本号

报告必须包含原始值：

- `ProductName`；
- `EditionID`；
- `DisplayVersion`；
- `CurrentBuild`；
- `UBR`；
- 组合后的完整 build。

客户端 Windows containers 必须符合 Microsoft 与所选 prototype runtime 的 Windows-container 支持版本。Windows Home 类 Edition（包括经正式核对属于 Home 的 `CoreCountrySpecific`）不得判为支持。

### 3.2 Windows Feature availability

分别只读核对：

- `Containers` 是否存在、是否对当前 Edition 可用、当前状态；
- `Microsoft-Hyper-V-All` 是否存在、是否对当前 Edition 可用、当前状态；
- 如 runtime 官方前置条件另有只读依赖项，只能记录，不能启用。

“Feature 存在但未启用”与“当前 Edition 根本不提供该 Feature”必须分开报告。

### 3.3 硬件虚拟化

报告必须包含：

- CPU 是否为 64 位；
- SLAT / `SecondLevelAddressTranslationExtensions`；
- VM Monitor Mode Extensions；
- BIOS / UEFI virtualization 是否启用；
- DEP / NX 可用性；
- `HypervisorPresent`；
- 物理 RAM 总量。

本项目按 Docker Desktop Windows containers 原型候选的较严格口径要求至少 `8 GB` RAM；Microsoft Hyper-V 的较低最低值不能覆盖 runtime 自身要求。

### 3.4 Docker Windows-container eligibility

必须根据 Docker 官方 Windows containers 支持矩阵明确给出：

- 当前 Edition 是否允许 Windows containers；
- 当前 build 是否满足要求；
- Hyper-V 与 Containers Feature 是否可用；
- SLAT、BIOS virtualization、RAM 是否满足；
- Docker Desktop 是否仅能运行 Linux containers；
- 结论依据是 host eligibility，而不是通过安装或启动 Docker 试错。

Docker Desktop 只作为 prototype runtime 候选，不是最终产品合同，也不是本门禁允许安装的组件。

## 4. 唯一结论枚举

最终结论只能是以下四项之一：

### `HOST_SUPPORTED`

只有在以下条件全部有权威只读证据时成立：

- Edition 支持客户端 Windows containers；
- build 满足 Microsoft 与候选 runtime 要求；
- Containers 与 Hyper-V Feature 对当前 Edition 可用且已处于满足原型前提的启用状态；
- 64 位、SLAT、VM Monitor Mode、DEP/NX、BIOS virtualization、RAM 全部满足，且不需要 BIOS/UEFI 配置变化或重启才能生效；
- Docker Windows-container eligibility 为真；
- 不需要变更 Windows Edition 或升级 build 才具备资格。

只有 `HOST_SUPPORTED` 才允许策划总控进入“是否单独授权 prototype runtime / image 等环境变化”的下一道决策，仍不得自动安装任何东西。

### `HOST_UNSUPPORTED_EDITION`

当前 Edition 不支持客户端 Windows containers，或只能运行 Linux containers。该结论优先于通过安装 runtime 试错；不得安装 runtime、Feature 或 image。

### `HOST_UNSUPPORTED_HARDWARE`

CPU 架构、SLAT、VM Monitor Mode、DEP/NX、BIOS virtualization 能力或 RAM 存在不可满足的硬件缺口。不得安装 runtime、Feature 或 image。

### `HOST_REQUIRES_OS_CHANGE`

Edition 与硬件原则上可支持，但 build 升级、Feature 启用、BIOS/UEFI 配置、待生效重启或其他 OS 级变化是前置条件。该结论不授权这些变化；不得安装 runtime、Feature 或 image，必须先返回策划总控和用户形成新的精确授权门禁。

判定优先级为：Edition 不支持 → `HOST_UNSUPPORTED_EDITION`；硬件能力不支持 → `HOST_UNSUPPORTED_HARDWARE`；其余必须改变 OS / Feature / firmware 才能继续 → `HOST_REQUIRES_OS_CHANGE`；全部资格证据齐备 → `HOST_SUPPORTED`。

## 5. 报告格式

执行报告必须逐项给出：

1. 查询时间、主机标识的非敏感摘要、执行权限级别；
2. 每项只读查询命令；
3. 原始输出或完整证据文件路径；
4. Edition、build、Feature、SLAT、BIOS virtualization、RAM 和 Docker eligibility 判定表；
5. 唯一最终结论；
6. 结论与官方支持矩阵的逐项映射；
7. 未能读取的字段及原因；
8. 明确声明未安装 runtime、未启用 Feature、未下载 image、未修改系统与产品文件。

任何证据缺失、冲突或查询失败都不能输出 `HOST_SUPPORTED`。

## 6. 后续门禁

- `HOST_SUPPORTED`：只表示主机具备进入原型环境变化授权评审的资格。策划总控需另行形成安装/Feature/image/network/rollback 精确任务包并由用户授权，Tier 3 原型仍为 `FROZEN`。
- 其余三个结论：Tier 3 Windows Container 原型保持 `BLOCKED`，不得安装 runtime、Feature 或 image。该历史门禁不再阻塞 2026-08-30 明确限定的 trusted-local Task 41；未来多人在线/不可信执行仍受约束。
- 无论结论为何，都不直接解冻 Task 41。

## 6A. 2026-08-29 正式结果与路线处置

- Tier 3-PRE：`HOST_UNSUPPORTED_EDITION`。
- Hyper-V-isolated Windows Container：停止作为当前本机主路线推进。
- 禁止继续安装本机 runtime、启用 Containers/Hyper-V 或处理 Windows container image。
- Remote Runner 后续也因 trusted-local 范围裁决取消；本文件作为未来多人在线安全强化的历史证据保留，不再作为当前待执行任务。

## 7. 权威支持来源

- Microsoft Learn：Windows containers 环境准备与客户端 Windows 版本要求  
  `https://learn.microsoft.com/en-us/virtualization/windowscontainers/quick-start/set-up-environment?tabs=dockerce`
- Microsoft Learn：Windows containers 支持策略  
  `https://learn.microsoft.com/en-us/troubleshoot/windows-server/containers/support-for-windows-containers-docker-on-premises-scenarios`
- Microsoft Learn：Hyper-V 硬件要求  
  `https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/host-hardware-requirements`
- Docker Docs：Install Docker Desktop on Windows  
  `https://docs.docker.com/desktop/setup/install/windows-install/`
