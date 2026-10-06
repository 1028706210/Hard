# Windows D 盘工具链

本项目只在 `D:\DevTools` 下管理可配置语言工具。三个引导脚本均拒绝 C 盘目标、Codex/Workbuddy 路径、非固定安装目录，以及路径中已有的 junction 或符号链接；不会修改系统级 PATH、注册表或用户级包管理器配置。

| 工具 | 固定安装路径 | 健康检查 | 目标版本 |
| --- | --- | --- | --- |
| Python | `D:\DevTools\python\python.exe` | `python --version` | 3.13.x |
| Java | 现有 `javac` 路径 | `javac -version` | 17.x |
| .NET | `D:\DevTools\dotnet\dotnet.exe` | `dotnet --version` | 10.x |
| MSYS2 GCC | `D:\DevTools\msys64\ucrt64\bin\g++.exe` | `g++ --version` | 可识别 GCC 版本 |

## 缓存与不变更系统设置

每个引导脚本只为自己的 PowerShell 进程设置下列缓存位置，不调用 `setx`、不编辑系统配置：

- npm：`D:\DevTools\cache\npm`
- pnpm store：`D:\DevTools\cache\pnpm-store`
- pip：`D:\DevTools\cache\pip`
- NuGet：`D:\DevTools\cache\nuget-packages` 与 `D:\DevTools\cache\nuget-http`
- MSYS2：`D:\DevTools\cache\msys2`；脚本将该目录显式传给 `pacman --cachedir`

如需在当前终端为 npm、pnpm、pip 或 NuGet 设置同样的临时缓存，可运行：

```powershell
. .\scripts\verify-toolchain.ps1
Set-ToolchainProcessCacheDefaults
```

关闭终端后这些环境变量自然失效。

## 运行引导脚本

下载工具、写入 `D:\DevTools` 前必须先取得项目批准。脚本只接受 HTTPS 安装器 URL 和官方发布页给出的 64 位 SHA-256 值；校验失败时不执行安装器。先用 `-WhatIf` 审阅目标，再在获批后移除它。

```powershell
$pythonUri = Read-Host 'Python 3.13 官方安装器 HTTPS URL'
$pythonSha256 = Read-Host 'Python 3.13 官方 SHA-256'
.\scripts\bootstrap-python.ps1 -InstallerUri $pythonUri -ExpectedSha256 $pythonSha256 -WhatIf
```

`.NET` 和 MSYS2 使用相同的受控输入方式：

```powershell
$dotnetUri = Read-Host '.NET 官方 dotnet-install.ps1 HTTPS URL'
$dotnetSha256 = Read-Host '.NET 官方 SHA-256'
.\scripts\bootstrap-dotnet.ps1 -InstallerUri $dotnetUri -ExpectedSha256 $dotnetSha256 -WhatIf

$msys2Uri = Read-Host 'MSYS2 官方 GUI 安装器 HTTPS URL（msys2-x86_64-*.exe，非 .sfx.exe）'
$msys2Sha256 = Read-Host 'MSYS2 官方 SHA-256'
.\scripts\bootstrap-msys2.ps1 -InstallerUri $msys2Uri -ExpectedSha256 $msys2Sha256 -WhatIf
```

MSYS2 脚本只接受官方 GUI 安装器 `msys2-x86_64-*.exe`，拒绝 SFX 安装包 `msys2-base-x86_64-*.sfx.exe`。脚本以 GUI 安装器的自动化参数 `in --confirm-command --accept-messages --root D:/DevTools/msys64` 固定安装根目录；SFX 的提取参数不同，不能混用。随后脚本通过 `D:\DevTools\msys64\usr\bin\bash.exe -lc` 进行首次初始化、两轮 `pacman --noconfirm -Syuu`，再安装 UCRT64 GCC。

引导脚本是幂等且保守的：已存在且健康的安装会直接返回健康报告；目标目录已有其他内容或缓存中的安装器哈希不匹配时会停止，绝不覆盖现有安装。若 GUI 安装已完成但更新或 GCC 安装失败，且目录中已有 `usr\bin\bash.exe` 与 `usr\bin\pacman.exe`，再次运行会跳过安装器并从初始化和两轮更新继续；其他非空目录仍会拒绝覆盖。

## 健康报告

Java 不由本项目安装；健康检查只检测现有的 `javac` 是否为 17.x。其余三个工具必须位于上表固定路径。

```powershell
.\scripts\verify-toolchain.ps1
.\scripts\verify-toolchain.ps1 -Output docs\setup\toolchain-lock.json
```

输出是 JSON 数组，每个元素严格包含 `name`、`path`、`version`、`healthy`、`detail`。任意工具缺失、版本不符、版本命令非零退出或路径不合规则脚本以非零退出；第二条命令仅在 D 盘写入报告。

## 脚本测试

使用 Windows PowerShell 5.1 运行：

```powershell
Invoke-Pester -Script .\tests\scripts\verify-toolchain.Tests.ps1 -EnableExit
```

若 Pester 未安装，先取得项目批准，再在 Windows PowerShell 5.1 中执行：

```powershell
Install-Module -Name Pester -RequiredVersion 3.4.0 -Scope CurrentUser
```

`-EnableExit` 会使测试失败时以非零退出码结束 PowerShell 进程。测试覆盖 C 盘安装目标、MSYS2 GUI/SFX 安装器区分、可恢复的 MSYS2 中断安装、两轮更新计划、Codex/Workbuddy Python 路径、重解析点绕过、缺失版本、非零版本命令和 JSON 健康报告字段。当前任务不会运行任何引导安装器。
