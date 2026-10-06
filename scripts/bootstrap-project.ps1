[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$managedPython = 'D:\DevTools\python\python.exe'
$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
$requirementsLock = Join-Path $projectRoot 'apps\api\requirements.lock'
$pnpmStore = Join-Path $projectRoot '.tool-cache\pnpm-store'

if (-not (Test-Path -LiteralPath $managedPython -PathType Leaf)) {
    throw "未找到项目指定 Python：$managedPython"
}

if (-not (Test-Path -LiteralPath $requirementsLock -PathType Leaf)) {
    throw "缺少后端锁文件：$requirementsLock"
}

if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
    if ($PSCmdlet.ShouldProcess($venvPython, '使用 D 盘 Python 创建项目虚拟环境')) {
        & $managedPython -m venv (Join-Path $projectRoot '.venv')
        if ($LASTEXITCODE -ne 0) {
            throw "创建 .venv 失败，退出码 $LASTEXITCODE。"
        }
    }
}

if ($PSCmdlet.ShouldProcess($projectRoot, '安装锁定的 Python 与 pnpm 依赖')) {
    & $venvPython -m pip install --disable-pip-version-check --requirement $requirementsLock
    if ($LASTEXITCODE -ne 0) {
        throw "安装 Python 依赖失败，退出码 $LASTEXITCODE。"
    }

    Push-Location $projectRoot
    try {
        & pnpm install --frozen-lockfile --store-dir $pnpmStore
        if ($LASTEXITCODE -ne 0) {
            throw "安装 pnpm 依赖失败，退出码 $LASTEXITCODE。"
        }
    }
    finally {
        Pop-Location
    }
}
