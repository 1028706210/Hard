[CmdletBinding()]
param(
    [ValidateSet('Smoke', 'Api', 'Web', 'E2E', 'Content', 'All')]
    [string]$Mode = 'Smoke'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
$pnpmStore = Join-Path $projectRoot '.tool-cache\pnpm-store'
$pnpmLock = Join-Path $projectRoot 'pnpm-lock.yaml'
$backendRequirementsLock = Join-Path $projectRoot 'apps\api\requirements.lock'
$coreCoverageGate = Join-Path $projectRoot 'apps\api\tests\core_coverage_gate.py'

function Assert-DDrivePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [AllowEmptyString()]
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return
    }

    if ($Value.Trim() -match '^(?i)c:') {
        throw "$Name 不允许指向 C: 盘：$Value"
    }
}

function Set-ProjectCacheDefaults {
    if ($projectRoot -notmatch '^(?i)d:(?:[\\/]|$)') {
        throw "项目根目录必须位于 D: 盘：$projectRoot"
    }

    foreach ($name in @('HARD_DATA_DIR', 'HARD_BACKUP_DIR', 'HARD_EXPORT_DIR', 'HARD_RUNNER_WORK_DIR')) {
        Assert-DDrivePath -Name $name -Value ([Environment]::GetEnvironmentVariable($name, 'Process'))
    }

    $cacheDefaults = [ordered]@{
        NPM_CONFIG_CACHE = 'D:\DevTools\cache\npm'
        npm_config_store_dir = $pnpmStore
        PIP_CACHE_DIR = 'D:\DevTools\cache\pip'
        NUGET_PACKAGES = 'D:\DevTools\cache\nuget-packages'
        NUGET_HTTP_CACHE_PATH = 'D:\DevTools\cache\nuget-http'
        DOTNET_CLI_HOME = 'D:\DevTools\cache\dotnet-cli'
        MSYS2_CACHE_DIR = 'D:\DevTools\cache\msys2'
    }

    foreach ($entry in $cacheDefaults.GetEnumerator()) {
        $configured = [Environment]::GetEnvironmentVariable($entry.Key, 'Process')
        Assert-DDrivePath -Name $entry.Key -Value $configured
        if ([string]::IsNullOrWhiteSpace($configured)) {
            [Environment]::SetEnvironmentVariable($entry.Key, $entry.Value, 'Process')
        }
    }
}

function Assert-BackendAsgiDependency {
    if (-not (Test-Path -LiteralPath $backendRequirementsLock -PathType Leaf)) {
        throw "缺少后端锁文件：$backendRequirementsLock"
    }

    if (-not (Select-String -Path $backendRequirementsLock -Pattern '^uvicorn==\d+\.\d+\.\d+$' -Quiet)) {
        throw '后端锁文件缺少 ASGI 运行依赖 uvicorn。'
    }
}

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Description,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Description，退出码 $LASTEXITCODE。"
    }
}

if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
    throw "缺少 .venv：请先运行 $projectRoot\scripts\bootstrap-project.ps1。"
}

Set-ProjectCacheDefaults
Assert-BackendAsgiDependency

$nodeVersion = @(& node --version 2>&1) -join [Environment]::NewLine
if ($LASTEXITCODE -ne 0) {
    throw "无法读取 Node.js 版本：$nodeVersion"
}

if ($nodeVersion.Trim() -ne 'v24.17.0') {
    throw "Node.js 版本必须为 v24.17.0，当前为 $($nodeVersion.Trim())。"
}

$pnpmVersion = @(& pnpm --version 2>&1) -join [Environment]::NewLine
if ($LASTEXITCODE -ne 0) {
    throw "无法读取 pnpm 版本：$pnpmVersion"
}

if ($pnpmVersion.Trim() -ne '11.19.0') {
    throw "pnpm 版本必须为 11.19.0，当前为 $($pnpmVersion.Trim())。"
}

if (-not (Test-Path -LiteralPath $pnpmLock -PathType Leaf)) {
    throw "缺少 pnpm 锁文件：$pnpmLock"
}

function Test-PnpmLock {
    Invoke-CheckedCommand -Description 'pnpm 锁文件漂移，请运行 pnpm install 重新生成 pnpm-lock.yaml' -Command {
        & pnpm install --frozen-lockfile --ignore-scripts --store-dir $pnpmStore
    }
}

function Test-ApiDependencies {
    Test-ApiCoreCoverage

    Invoke-CheckedCommand -Description '后端依赖不可用，请运行 scripts\\bootstrap-project.ps1' -Command {
        & $venvPython -c 'import alembic, fastapi, httpx, markdown_it, psutil, sqlalchemy, uvicorn, yaml'
    }
}

function Test-ApiCoreCoverage {
    if (-not (Test-Path -LiteralPath $coreCoverageGate -PathType Leaf)) {
        throw "缺少后端核心覆盖率门禁：$coreCoverageGate"
    }

    $temporaryRoot = Join-Path $projectRoot '.tool-cache\check-temp'
    $previousTemp = $env:TEMP
    $previousTmp = $env:TMP
    try {
        New-Item -ItemType Directory -Force -Path $temporaryRoot | Out-Null
        $env:TEMP = $temporaryRoot
        $env:TMP = $temporaryRoot
        Invoke-CheckedCommand -Description '后端核心覆盖率门禁失败' -Command {
            & $venvPython $coreCoverageGate
        }
    }
    finally {
        $env:TEMP = $previousTemp
        $env:TMP = $previousTmp
    }
}

function Test-WebTooling {
    $webPackage = Join-Path $projectRoot 'apps\web\package.json'
    if (Test-Path -LiteralPath $webPackage -PathType Leaf) {
        Invoke-CheckedCommand -Description '前端工具链检查失败' -Command {
            & pnpm --dir (Join-Path $projectRoot 'apps\web') run check
        }
    }

    $openApiExporter = Join-Path $projectRoot 'scripts\export-openapi.ps1'
    if (Test-Path -LiteralPath $openApiExporter -PathType Leaf) {
        Invoke-CheckedCommand -Description 'OpenAPI 合同检查失败' -Command {
            & $openApiExporter -Check
        }
    }
}

function Test-E2ETooling {
    $webPackage = Join-Path $projectRoot 'apps\web\package.json'
    if (Test-Path -LiteralPath $webPackage -PathType Leaf) {
        Invoke-CheckedCommand -Description '端到端工具链检查失败' -Command {
            & pnpm --dir (Join-Path $projectRoot 'apps\web') run check:e2e
        }
    }
}

function Test-ContentTooling {
    $validator = Join-Path $projectRoot 'tools\content\validate.py'
    if (Test-Path -LiteralPath $validator -PathType Leaf) {
        Invoke-CheckedCommand -Description '内容校验失败' -Command {
            & $venvPython $validator
        }
    }
}

Test-PnpmLock

switch ($Mode) {
    'Api' { Test-ApiDependencies }
    'Web' { Test-WebTooling }
    'E2E' { Test-E2ETooling }
    'Content' { Test-ContentTooling }
    'All' {
        Test-ApiDependencies
        Test-WebTooling
        Test-E2ETooling
        Test-ContentTooling
    }
}

Write-Output "检查通过：$Mode"
