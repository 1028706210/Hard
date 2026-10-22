[CmdletBinding()]
param(
    [string]$ProjectRoot = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $ProjectRoot) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path

$runStatePath = Join-Path $ProjectRoot '.tool-cache\hard-start\run.json'
if (-not (Test-Path -LiteralPath $runStatePath -PathType Leaf)) {
    Write-Output '未发现正在运行的 Hard 实例（缺少运行状态文件），无需停止。'
    exit 0
}

$state = Get-Content -LiteralPath $runStatePath -Raw | ConvertFrom-Json

if ($state.project_root -ne $ProjectRoot) {
    throw '运行记录属于其他项目；拒绝停止或发送 LAN 请求。'
}

function Get-OwnedProcess {
    param([int]$ProcessId, [string]$StartedAt, [string]$Executable)
    $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if (-not $process) { return $null }
    if ($process.StartTime.ToUniversalTime().Ticks.ToString() -ne $StartedAt -or $process.Path -ne $Executable) {
        throw "PID $ProcessId 身份不符；保留记录，拒绝终止其他程序。"
    }
    return $process
}

# Validate both identities before any side effects; old records fail closed.
$apiOwned = Get-OwnedProcess $state.api_pid $state.api_started_ticks $state.api_executable
$webOwned = Get-OwnedProcess $state.web_pid $state.web_started_ticks $state.web_executable

# LAN closes with the verified API process tree. Do not send requests to a
# recorded port: after a crash it may belong to another application.

# 2) 仅回收本次启动链记录的进程树（前端先停，后端后停）。
function Stop-RecordedTree {
    param([int]$ProcessId, [string]$Label, [string]$StartedAt, [string]$Executable)
    if ($ProcessId -le 0) { return }
    $alive = Get-OwnedProcess $ProcessId $StartedAt $Executable
    if (-not $alive) {
        Write-Output "$Label 进程 $ProcessId 已退出。"
        return
    }
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & taskkill.exe /PID $ProcessId /T /F 2>&1 | Out-Null
        $killCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    if ($killCode -ne 0) { throw "停止 $Label 失败：taskkill 退出码 $killCode；保留运行记录。" }
    if (-not $alive.WaitForExit(5000)) { throw "停止 $Label 超时；保留运行记录。" }
    Write-Output "已停止 $Label 进程树（PID $ProcessId）。"
}

Stop-RecordedTree $state.web_pid 'Web' $state.web_started_ticks $state.web_executable
Stop-RecordedTree $state.api_pid 'API' $state.api_started_ticks $state.api_executable

# 3) 等待端口释放；未释放视为失败，绝不误杀其他程序。
$deadline = (Get-Date).AddSeconds(10)
$portsFreed = $false
while ((Get-Date) -lt $deadline) {
    $apiListening = Get-NetTCPConnection -LocalPort $state.api_port -State Listen -ErrorAction SilentlyContinue
    $webListening = Get-NetTCPConnection -LocalPort $state.web_port -State Listen -ErrorAction SilentlyContinue
    if (-not $apiListening -and -not $webListening) {
        $portsFreed = $true
        break
    }
    Start-Sleep -Milliseconds 300
}

if (-not $portsFreed) {
    throw "停止失败：端口 $($state.api_port)/$($state.web_port) 仍未释放，请手动核查残留进程。"
}

Remove-Item -LiteralPath $runStatePath -Force
Write-Output '已停止：Hard API 与前端进程已退出，端口已释放，运行状态文件已清理。'
