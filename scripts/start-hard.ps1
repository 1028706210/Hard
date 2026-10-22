[CmdletBinding()]
param(
    [string]$ProjectRoot = '',
    [int]$ApiPort = 8000,
    [int]$WebPort = 4173,
    [int]$HealthTimeoutSeconds = 30
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $ProjectRoot) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
if (-not $ProjectRoot.ToUpperInvariant().StartsWith('D:')) {
    throw "Hard 项目必须位于 D 盘：$ProjectRoot"
}

$venvPython = $null
foreach ($candidate in @('python.exe', 'python.cmd', 'python.bat')) {
    $candidatePath = Join-Path $ProjectRoot (".venv\Scripts\$candidate")
    if (Test-Path -LiteralPath $candidatePath -PathType Leaf) {
        $venvPython = $candidatePath
        break
    }
}
$webRoot = Join-Path $ProjectRoot 'apps\web'
$nodeModules = Join-Path $webRoot 'node_modules'
$viteEntry = Join-Path $nodeModules 'vite\bin\vite.js'
$contentDir = Join-Path $ProjectRoot 'content'
$runDirectory = Join-Path $ProjectRoot '.tool-cache\hard-start'
$runStatePath = Join-Path $runDirectory 'run.json'

function Test-TcpPortOpen {
    param([int]$Port)
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        return $client.ConnectAsync('127.0.0.1', $Port).Wait(500)
    } catch {
        return $false
    } finally {
        $client.Close()
    }
}

function Stop-StartedTree {
    param([int[]]$ProcessIds)
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        foreach ($processId in $ProcessIds) {
            if ($processId -gt 0) {
                & taskkill.exe /PID $processId /T /F 2>&1 | Out-Null
            }
        }
    } finally {
        $ErrorActionPreference = $previousPreference
    }
}

# 1) 重复启动保护：存在未清理的运行状态即视为已在运行。
if (Test-Path -LiteralPath $runStatePath -PathType Leaf) {
    throw "Hard 已在运行（发现运行状态文件 $runStatePath）。请先运行 scripts\stop-hard.ps1 停止上一次实例。"
}

# 2) 启动前依赖校验，任何缺失都以清晰错误终止。
$missing = @()
if (-not $venvPython) { $missing += "后端虚拟环境 $(Join-Path $ProjectRoot '.venv\Scripts\python.exe')（先运行 scripts\bootstrap-project.ps1）" }
if (-not (Test-Path -LiteralPath $viteEntry -PathType Leaf)) { $missing += "前端依赖 $nodeModules（先运行 scripts\bootstrap-project.ps1）" }
if (-not (Test-Path -LiteralPath $contentDir -PathType Container)) { $missing += "课程内容目录 $contentDir" }
if ($missing.Count -gt 0) {
    throw ("启动前检查失败，缺少：`n - " + ($missing -join "`n - "))
}

# 3) 外部端口冲突检查（无运行状态但端口被其他程序占用）。
if (Test-TcpPortOpen -Port $ApiPort) {
    throw "端口 $ApiPort 已被其他程序占用：Hard 无法在该端口启动。请释放端口或用 -ApiPort 指定其他端口。"
}
if (Test-TcpPortOpen -Port $WebPort) {
    throw "端口 $WebPort 已被其他程序占用：Hard 无法在该端口启动。请释放端口或用 -WebPort 指定其他端口。"
}

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw '未在 PATH 中找到 node.exe，无法启动前端。'
}
$nodeExecutable = (Get-Command node).Source

New-Item -ItemType Directory -Force -Path $runDirectory | Out-Null
$apiLogPath = Join-Path $runDirectory 'api.log'
$webLogPath = Join-Path $runDirectory 'web.log'

# 4) 启动后端与前端（仅本机回环），失败时整树回收。
$started = @()
try {
    & $venvPython (Join-Path $PSScriptRoot 'prepare-hard.py') $ProjectRoot
    if ($LASTEXITCODE -ne 0) { throw "数据库准备失败，退出码 $LASTEXITCODE；服务尚未启动。" }

    $apiProcess = Start-Process -FilePath $venvPython `
        -ArgumentList @('-m', 'uvicorn', 'hard_api.main:app', '--app-dir', ('"' + (Join-Path $ProjectRoot 'apps\api\src') + '"'), '--host', '127.0.0.1', '--port', "$ApiPort") `
        -WorkingDirectory $ProjectRoot -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $apiLogPath -RedirectStandardError (Join-Path $runDirectory 'api.err.log')
    $started += $apiProcess.Id

    $previousApiUrl = $env:HARD_API_URL
    try {
        $env:HARD_API_URL = "http://127.0.0.1:$ApiPort"
        $webProcess = Start-Process -FilePath $nodeExecutable `
            -ArgumentList @(('"' + $viteEntry + '"'), '--host', '127.0.0.1', '--port', "$WebPort", '--strictPort') `
            -WorkingDirectory $webRoot -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput $webLogPath -RedirectStandardError (Join-Path $runDirectory 'web.err.log')
    } finally {
        $env:HARD_API_URL = $previousApiUrl
    }
    $started += $webProcess.Id

    # 5) 健康检查：API 必须数据库/工具链就绪；前端等 TCP 监听。
    $deadline = (Get-Date).AddSeconds($HealthTimeoutSeconds)
    $apiHealthy = $false
    $webReady = $false
    while ((Get-Date) -lt $deadline) {
        if (-not $apiHealthy) {
            if (Test-TcpPortOpen -Port $ApiPort) {
                try {
                    $live = Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 -Uri "http://127.0.0.1:$ApiPort/api/v1/health/ready"
                    if ($live.StatusCode -eq 200) { $apiHealthy = $true }
                } catch {
                }
            }
        }
        if (-not $webReady) {
            if (Test-TcpPortOpen -Port $WebPort) { $webReady = $true }
        }
        if ($apiHealthy -and $webReady) { break }
        Start-Sleep -Milliseconds 300
    }

    if (-not ($apiHealthy -and $webReady)) {
        $detail = @()
        if (-not $apiHealthy) { $detail += "API 就绪检查未通过（127.0.0.1:$ApiPort/api/v1/health/ready）" }
        if (-not $webReady) { $detail += "前端未在 127.0.0.1:$WebPort 监听" }
        throw ("启动失败：健康检查超时。`n - " + ($detail -join "`n - ") + "`n日志：$apiLogPath / $webLogPath")
    }

    # 6) 记录运行状态，供 stop-hard.ps1 精确回收本次启动链。
    $state = @{
        api_pid = $apiProcess.Id
        web_pid = $webProcess.Id
        api_started_ticks = $apiProcess.StartTime.ToUniversalTime().Ticks.ToString()
        web_started_ticks = $webProcess.StartTime.ToUniversalTime().Ticks.ToString()
        api_executable = $apiProcess.Path
        web_executable = $webProcess.Path
        api_port = $ApiPort
        web_port = $WebPort
        started_at = (Get-Date).ToString('o')
        project_root = $ProjectRoot
    }
    $state | ConvertTo-Json | Set-Content -LiteralPath $runStatePath -Encoding UTF8

    Write-Output 'Hard 已启动（仅本机访问）。'
    Write-Output "  API：http://127.0.0.1:$ApiPort"
    Write-Output "  Web：http://127.0.0.1:$WebPort"
    Write-Output "  数据：$ProjectRoot\data（数据库）、backups（自动备份）、exports（手动导出）、runner-work（运行工作区），全部位于 D 盘。"
    Write-Output '  手机访问属可选 LAN 模式：需在设置页显式开启并确认；同网络设备可访问数据并运行代码。'
    Write-Output '  安全边界：Runner 仅适合运行你自己编写的学习代码（TRUSTED_LOCAL_LEARNING_ONLY），不能安全运行恶意代码。'
    Write-Output '  停止：powershell -NoProfile -ExecutionPolicy Bypass -File scripts\stop-hard.ps1'
} catch {
    Stop-StartedTree -ProcessIds $started
    if (Test-Path -LiteralPath $runStatePath) {
        Remove-Item -LiteralPath $runStatePath -Force
    }
    throw
}
