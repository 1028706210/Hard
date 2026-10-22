# Phase D 本机 Python 路线运行

本说明只提供 Phase D 的手动本机运行流程，不替代未来 Phase H 的启动包。所有命令默认仅绑定 `127.0.0.1`；不要启用 LAN、Docker、防火墙规则或公网访问。

## 前置条件与 D 盘缓存

在项目根目录运行。项目根、数据、备份、导出、Runner 工作目录与缓存都必须位于 D 盘。当前环境中的 `pnpm` 可执行文件可能来自 Codex 的 C 盘运行时；这是环境运行时路径，不是项目数据或 store。不要自动迁移或安装它。

```powershell
$projectRoot = (Resolve-Path .).Path
if ($projectRoot -notmatch '^(?i)D:') { throw 'Hard 必须从 D 盘项目目录运行。' }

$env:NPM_CONFIG_CACHE = 'D:\DevTools\cache\npm'
$env:npm_config_store_dir = Join-Path $projectRoot '.tool-cache\pnpm-store'
$env:PIP_CACHE_DIR = 'D:\DevTools\cache\pip'
$env:NUGET_PACKAGES = 'D:\DevTools\cache\nuget-packages'
$env:NUGET_HTTP_CACHE_PATH = 'D:\DevTools\cache\nuget-http'
```

若缺少 `.venv` 或 `node_modules`，先取得下载/安装授权，再运行 `scripts\bootstrap-project.ps1`。本说明不会安装任何工具。

## 预检、迁移与内容索引

先确认端口没有被其他程序使用。发现监听后停止，不要杀死不明进程或改用 LAN 地址。

```powershell
$listeners = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
    Where-Object { $_.LocalPort -in 8000, 4173 }
if ($listeners) { $listeners | Format-Table LocalAddress, LocalPort, OwningProcess; throw '8000 或 4173 已被占用。' }

.\scripts\check.ps1 -Mode Smoke
.\scripts\check.ps1 -Mode Api
```

在启动 API 前，显式执行迁移、内容载入与 FTS 索引；这会使用 `Settings` 的 D 盘相对路径，不要把任何 `HARD_*` 路径配置到 C 盘。

```powershell
$env:PYTHONPATH = Join-Path $projectRoot 'apps\api\src'
$prepareDatabase = @'
from hard_api.backup.service import LocalBackupService
from hard_api.content.repository import ContentRepository
from hard_api.core.config import Settings
from hard_api.db.migrations import migrate_database
from hard_api.search.service import SearchService

settings = Settings.from_environment()
migrate_database(settings.database_path, backup_provider=LocalBackupService(settings.backup_dir))
repository = ContentRepository(settings.content_dir)
if repository.isolated_errors:
    raise RuntimeError(repository.isolated_errors)
SearchService(settings.database_path, repository).ensure_content_index()
'@
& .\.venv\Scripts\python.exe -c $prepareDatabase
```

## 手动启动与 readiness

在两个独立 PowerShell 窗口中启动 API 与 Web。不要添加 `--host 0.0.0.0`，不要选择 RFC1918 地址。

```powershell
# 窗口 A：API，仅 loopback
& .\.venv\Scripts\python.exe -m uvicorn hard_api.main:app --app-dir .\apps\api\src --host 127.0.0.1 --port 8000
```

```powershell
# 窗口 B：Web 开发服务器，仅 loopback；Vite 将 /api 转发到 127.0.0.1:8000
pnpm --dir .\apps\web exec vite --host 127.0.0.1 --port 4173 --strictPort
```

在第三个窗口验证 API 已就绪；非 200 响应必须按错误处理，不要继续学习流程。

```powershell
$ready = Invoke-WebRequest 'http://127.0.0.1:8000/api/v1/health/ready' -UseBasicParsing
if ($ready.StatusCode -ne 200) { throw "readiness 返回 $($ready.StatusCode)" }
Start-Process 'http://127.0.0.1:4173'
```

## 停止与端口释放

分别在窗口 A 和窗口 B 按 `Ctrl+C` 停止服务。随后只检查端口是否释放；若仍有监听，记录 OwningProcess 并交由对应 Session 处理，不要终止不明进程。

```powershell
$remaining = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
    Where-Object { $_.LocalPort -in 8000, 4173 }
if ($remaining) { $remaining | Format-Table LocalAddress, LocalPort, OwningProcess; throw '本机服务停止后端口未释放。' }
```

## 本阶段边界

- 不创建 `start-hard.ps1`、`stop-hard.ps1` 或 `release-check.ps1`；这些属于 Phase H。
- 不执行 Docker、LAN 开关、防火墙命令、端口转发或公共隧道。
- 正式 `data/`、`backups/`、`exports/` 与 `runner-work/` 不用于测试；出现 readiness、迁移或 FTS 失败时停止并报告。
