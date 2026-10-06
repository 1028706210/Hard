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
    Invoke-CheckedCommand -Description '后端依赖不可用，请运行 scripts\\bootstrap-project.ps1' -Command {
        & $venvPython -c 'import alembic, fastapi, httpx, markdown_it, psutil, sqlalchemy, yaml'
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
