[CmdletBinding()]
param(
    [string]$ProjectRoot = '',
    [switch]$SkipE2E
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ($SkipE2E) { throw '正式发布检查不允许 SkipE2E；所有必需门禁必须执行。' }

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
if (-not $venvPython) {
    throw "缺少项目虚拟环境：$(Join-Path $ProjectRoot '.venv\Scripts\python.exe')（先运行 scripts\bootstrap-project.ps1）。"
}
$webRoot = Join-Path $ProjectRoot 'apps\web'
$vitestEntry = Join-Path $webRoot 'node_modules\vitest\vitest.mjs'
$viteEntry = Join-Path $webRoot 'node_modules\vite\bin\vite.js'
$playwrightEntry = Join-Path $webRoot 'node_modules\@playwright\test\cli.js'
foreach ($entry in @($vitestEntry, $viteEntry, $playwrightEntry)) {
    if (-not (Test-Path -LiteralPath $entry -PathType Leaf)) {
        throw "缺少前端依赖入口：$entry（先运行 scripts\bootstrap-project.ps1）。"
    }
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    throw '未在 PATH 中找到 node.exe，无法执行前端检查。'
}
$nodeExecutable = (Get-Command node).Source

# 优先调用实际 Node 入口（.bin 启动脚本路径在部分环境失效；pnpm store 不可写时 pnpm 不可用）。
$runId = (Get-Date).ToString('yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N').Substring(0,8)
$logDirectory = Join-Path $ProjectRoot "docs\audit\release\runs\$runId\logs"
New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
# Keep child-process temporary state in a fresh, writable project directory.
# Shared user pytest folders may be owned by another Windows session.
$temporaryDirectory = Join-Path $ProjectRoot ".tool-cache\release-temp\$runId"
New-Item -ItemType Directory -Force -Path $temporaryDirectory | Out-Null
$env:TEMP = $temporaryDirectory
$env:TMP = $temporaryDirectory
$env:PYTHONIOENCODING = 'utf-8'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$script:failedStep = $null
$script:failedExitCode = 0
$script:stepIndex = 0

function Invoke-ReleaseStep {
    param(
        [string]$Name,
        [string]$Executable,
        [string[]]$Arguments,
        [string]$WorkingDirectory
    )
    $script:stepIndex += 1
    $logPath = Join-Path $logDirectory ("{0:D2}-{1}.log" -f $script:stepIndex, $Name)
    Write-Output "==> $Name"
    $stepStarted = (Get-Date).ToString('o')
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    Push-Location $WorkingDirectory
    try {
        $output = & $Executable @Arguments 2>&1
        $code = $LASTEXITCODE
    } finally {
        Pop-Location
        $ErrorActionPreference = $previousPreference
    }
    # Set-Content 即使步骤无输出也会建立日志文件，保证每步留痕。
    $output | Set-Content -LiteralPath $logPath -Encoding UTF8
    @{name=$Name; executable=$Executable; arguments=$Arguments; cwd=$WorkingDirectory; started=$stepStarted; ended=(Get-Date).ToString('o'); exit_code=$code} |
        ConvertTo-Json -Depth 4 | Set-Content -LiteralPath ($logPath + '.json') -Encoding UTF8
    foreach ($line in @($output)) {
        Write-Output $line
    }
    if ($code -ne 0) {
        $script:failedStep = $Name
        $script:failedExitCode = $code
        Write-Output "步骤 $Name 失败，退出码 $code（日志：$logPath）。停止后续检查。"
        throw "步骤 $Name 失败，退出码 $code。"
    }
    Write-Output "步骤 $Name 通过（退出码 0，日志：$logPath）。"
}

$timestamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
Write-Output "Hard release-check 开始：$timestamp（项目：$ProjectRoot）"

try {
    foreach ($language in @('python', 'java', 'csharp', 'cpp')) {
        Invoke-ReleaseStep -Name "content-validate-$language" `
            -Executable $venvPython `
            -Arguments @((Join-Path $ProjectRoot 'tools\content\validate.py'), '--language', $language, '--require-complete') `
            -WorkingDirectory $ProjectRoot
    }

    Invoke-ReleaseStep -Name 'content-execution-and-originality' `
        -Executable $venvPython `
        -Arguments @((Join-Path $ProjectRoot 'scripts\release-content.py'), '--output', (Split-Path -Parent $logDirectory)) `
        -WorkingDirectory $ProjectRoot

    Invoke-ReleaseStep -Name 'api-contract-drift' `
        -Executable 'powershell' `
        -Arguments @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', (Join-Path $ProjectRoot 'scripts\export-openapi.ps1'), '-Check') `
        -WorkingDirectory $ProjectRoot

    Invoke-ReleaseStep -Name 'backend-tests' `
        -Executable $venvPython `
        -Arguments @('-m', 'pytest', 'apps\api\tests', '-q', '-p', 'no:cacheprovider', '--disable-warnings') `
        -WorkingDirectory $ProjectRoot

    Invoke-ReleaseStep -Name 'core-coverage-gate' `
        -Executable $venvPython `
        -Arguments @((Join-Path $ProjectRoot 'apps\api\tests\core_coverage_gate.py')) `
        -WorkingDirectory $ProjectRoot

    Invoke-ReleaseStep -Name 'backend-coverage' `
        -Executable $venvPython `
        -Arguments @('-m', 'pytest', 'apps\api\tests', '-q', '-p', 'no:cacheprovider', '--disable-warnings', '--cov=hard_api', '--cov-report=term', '--cov-fail-under=85') `
        -WorkingDirectory $ProjectRoot

    Invoke-ReleaseStep -Name 'frontend-tests' `
        -Executable $nodeExecutable `
        -Arguments @($vitestEntry, 'run', '--coverage', '--coverage.thresholds.lines', '80') `
        -WorkingDirectory $webRoot

    Invoke-ReleaseStep -Name 'frontend-build' `
        -Executable $nodeExecutable `
        -Arguments @($viteEntry, 'build') `
        -WorkingDirectory $webRoot

    if (-not $SkipE2E) {
        # 旅程类 E2E 要求提供截图目录；发布运行即把桌面/手机证据留存在发布审计目录。
        $screenshotsDirectory = Join-Path (Split-Path -Parent $logDirectory) 'screenshots'
        New-Item -ItemType Directory -Force -Path $screenshotsDirectory | Out-Null
        $env:HARD_VISUAL_AUDIT_DIR = $screenshotsDirectory
        # python 旅程对全局“继续学习”位置敏感（任何课时页访问都会推进它），
        # 单独先跑以获得全新隔离库；其余电池第二步运行，所有用例仍全部执行。
        Invoke-ReleaseStep -Name 'release-e2e-python-journey' `
            -Executable $nodeExecutable `
            -Arguments @($playwrightEntry, 'test', 'tests/e2e/python-journey.spec.ts', '--config', 'playwright.config.ts', '--output', (Join-Path $ProjectRoot '.tool-cache\playwright-results-release-python')) `
            -WorkingDirectory $webRoot

        $batteryFiles = Get-ChildItem -LiteralPath (Join-Path $webRoot 'tests\e2e') -Filter '*.spec.ts' -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -ne 'python-journey.spec.ts' } |
            ForEach-Object { "tests/e2e/$($_.Name)" }
        Invoke-ReleaseStep -Name 'release-e2e' `
            -Executable $nodeExecutable `
            -Arguments (@($playwrightEntry, 'test', '--config', 'playwright.config.ts', '--output', (Join-Path $ProjectRoot '.tool-cache\playwright-results-release')) + @($batteryFiles)) `
            -WorkingDirectory $webRoot
    }
} catch {
    if ($script:failedStep) {
        exit $script:failedExitCode
    }
    throw
}

Write-Output "release-check 全部通过：$((Get-Date).ToString('o'))。证据：$logDirectory"
exit 0
