# 本地语言工具链验证（Task 2）

验证日期：2026-08-23。完整的机器可读锁文件见 `docs/setup/toolchain-lock.json`。

## 已锁定的可执行文件

| 工具 | 可执行路径 | 版本 | 安装目录体积 |
| --- | --- | --- | --- |
| Python | `D:\DevTools\python\python.exe` | 3.13.13 | 116.82 MiB |
| Java | `C:\Program Files\Common Files\Oracle\Java\javapath\javac.exe`（JDK home：`C:\Program Files\Java\jdk-17`） | 17.0.7 | 289.71 MiB |
| .NET SDK | `D:\DevTools\dotnet\dotnet.exe` | 10.0.100 | 769.95 MiB |
| MSYS2 UCRT64 GCC | `D:\DevTools\msys64\ucrt64\bin\g++.exe` | 16.2.0 | 800.24 MiB |

Python、.NET 与 MSYS2 均位于 `D:\DevTools`；Java 是验证到的现有 JDK 17，没有被本任务重新安装或移动。

## 安装来源与可重复命令

所有安装器均通过 HTTPS 下载到 `D:\DevTools\cache\installers`，并在运行前校验 SHA-256。

- Python 3.13.13：`https://www.python.org/ftp/python/3.13.13/python-3.13.13-amd64.exe`
  - SHA-256：`3c9c81d80f91c002ced86d645422d81432c68c7d9b6b0e974768ca2e449a4d00`
- .NET 安装脚本：`https://raw.githubusercontent.com/dotnet/install-scripts/v2026.07.21/src/dotnet-install.ps1`
  - 固定签名发布标签：`v2026.07.21`
  - SHA-256：`3bb07bc8025211836c1e4f9d3f6a044e55b1fb6eec518a6c78851d04e210442b`
  - SDK：`10.0.100`
- MSYS2 GUI 安装器：`https://github.com/msys2/msys2-installer/releases/download/2026-06-11/msys2-x86_64-20260611.exe`
  - SHA-256：`3150d7d9aa5dedd900a7f52300d4d918271e3a8fc47de94848818fd5a430e6b0`

获批后可使用相同的固定输入重新执行引导脚本；健康安装会直接返回，不会重复下载：

```powershell
.\scripts\bootstrap-python.ps1 -InstallerUri 'https://www.python.org/ftp/python/3.13.13/python-3.13.13-amd64.exe' -ExpectedSha256 '3c9c81d80f91c002ced86d645422d81432c68c7d9b6b0e974768ca2e449a4d00'
.\scripts\bootstrap-dotnet.ps1 -InstallerUri 'https://raw.githubusercontent.com/dotnet/install-scripts/v2026.07.21/src/dotnet-install.ps1' -ExpectedSha256 '3bb07bc8025211836c1e4f9d3f6a044e55b1fb6eec518a6c78851d04e210442b' -Version '10.0.100'
.\scripts\bootstrap-msys2.ps1 -InstallerUri 'https://github.com/msys2/msys2-installer/releases/download/2026-06-11/msys2-x86_64-20260611.exe' -ExpectedSha256 '3150d7d9aa5dedd900a7f52300d4d918271e3a8fc47de94848818fd5a430e6b0'
```

MSYS2 的 GUI 首次启动卡在其内部 `pacman-key --refresh-keys` 时，未删除任何已有内容；保留 `D:\DevTools\msys64` 后通过 MSYS2 shell 完成了两轮更新和 GCC 安装：

```powershell
$env:MSYSTEM = 'UCRT64'
& 'D:\DevTools\msys64\usr\bin\bash.exe' -lc 'pacman --noconfirm --cachedir D:/DevTools/cache/msys2 -Syuu'
& 'D:\DevTools\msys64\usr\bin\bash.exe' -lc 'pacman --noconfirm --cachedir D:/DevTools/cache/msys2 -Syuu'
& 'D:\DevTools\msys64\usr\bin\bash.exe' -lc 'pacman --noconfirm --cachedir D:/DevTools/cache/msys2 -S --needed mingw-w64-ucrt-x86_64-gcc'
```

## 四语言 Hello World 与 C++20

验证工作目录为 `D:\projects\1\Hard-task1\.tool-cache\task2-hello`。所有源码、编译产物、临时项目和输出文件均在 D 盘：

| 语言 | 输出文件 | 输出 |
| --- | --- | --- |
| Python | `python\hello.out` | `hello-python` |
| Java | `java\hello.out` | `hello-java` |
| .NET | `dotnet\hello.out` | `Hello, World!` |
| C++20 | `cpp\hello.out` | `hello-cpp` |

Java 产物为 `java\classes\Hello.class`；.NET 临时项目包含 `dotnet\Hello.csproj`、`Program.cs`、`bin` 与 `obj`；C++20 产物为 `cpp\hello.exe`。C++ 编译和运行通过 `MSYSTEM=UCRT64` 的登录 shell 执行，以提供 GCC 子进程所需的 UCRT64 DLL 搜索路径。

## 缓存清理

引导脚本不自动删除缓存或用户文件。先审阅目标，再移除 `-WhatIf` 执行以下命令：

```powershell
Remove-Item -LiteralPath 'D:\DevTools\cache\installers\python-3.13.13-amd64.exe' -WhatIf
Remove-Item -LiteralPath 'D:\DevTools\cache\installers\dotnet-install.ps1' -WhatIf
Remove-Item -LiteralPath 'D:\DevTools\cache\installers\msys2-x86_64-20260611.exe' -WhatIf
```

MSYS2 包缓存位于 `D:\DevTools\cache\msys2`。它可缩短未来的包安装；如需清理，先以 `-WhatIf` 审阅精确路径，并且不要删除 `D:\DevTools\python`、`D:\DevTools\dotnet`、`D:\DevTools\msys64` 或现有 Java 安装。
