$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$releaseCheckScript = Join-Path $repoRoot 'scripts\release-check.ps1'

function New-ReleaseFixture {
    param([string]$PythonExit = '0', [string]$NodeExit = '0')

    $fixtureRoot = Join-Path $repoRoot ('.pester-release-' + [guid]::NewGuid().ToString('N'))
    $scriptsDirectory = Join-Path $fixtureRoot 'scripts'
    $venvScripts = Join-Path $fixtureRoot '.venv\Scripts'
    $stubDirectory = Join-Path $fixtureRoot 'stub-bin'
    New-Item -ItemType Directory -Force -Path $scriptsDirectory, $venvScripts, $stubDirectory, (Join-Path $fixtureRoot 'apps\web'), (Join-Path $fixtureRoot 'content\python'), (Join-Path $fixtureRoot 'content\java'), (Join-Path $fixtureRoot 'content\csharp'), (Join-Path $fixtureRoot 'content\cpp'), (Join-Path $fixtureRoot 'docs\setup') | Out-Null

    Copy-Item -LiteralPath $releaseCheckScript -Destination (Join-Path $scriptsDirectory 'release-check.ps1')
    Set-Content -LiteralPath (Join-Path $scriptsDirectory 'export-openapi.ps1') -Value 'param([switch]$Check); if (-not $Check) { exit 9 }; exit 0' -Encoding Ascii

    # 桩命令：按配置文件里的退出码退出，并记录被调用的事实与参数。
    Set-Content -LiteralPath (Join-Path $stubDirectory 'python.cmd') -Value @(
        '@echo off',
        'echo %* >> "%~dp0python-calls.log"',
        'set /p CODE=<"%~dp0python-exit.txt" 2>nul',
        'if "%CODE%"=="" set CODE=0',
        'exit /b %CODE%'
    ) -Encoding Ascii
    Set-Content -LiteralPath (Join-Path $stubDirectory 'node.cmd') -Value @(
        '@echo off',
        'echo %* >> "%~dp0node-calls.log"',
        'set /p CODE=<"%~dp0node-exit.txt" 2>nul',
        'if "%CODE%"=="" set CODE=0',
        'exit /b %CODE%'
    ) -Encoding Ascii
    Set-Content -LiteralPath (Join-Path $stubDirectory 'python-exit.txt') -Value $PythonExit -Encoding Ascii
    Set-Content -LiteralPath (Join-Path $stubDirectory 'node-exit.txt') -Value $NodeExit -Encoding Ascii

    New-Item -ItemType Junction -Path $venvScripts -Target $stubDirectory | Out-Null
    # 桩目录内补齐脚本期望的前端入口文件（经 node_modules 联接可见）。
    foreach ($entry in @('vitest\vitest.mjs', 'vite\bin\vite.js', '@playwright\test\cli.js')) {
        $entryPath = Join-Path $stubDirectory $entry
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $entryPath) | Out-Null
        Set-Content -LiteralPath $entryPath -Value '// stub' -Encoding Ascii
    }
    Set-Content -LiteralPath (Join-Path $fixtureRoot 'docs\setup\toolchain-lock.json') -Value '{}' -Encoding Ascii
    Set-Content -LiteralPath (Join-Path $fixtureRoot 'apps\web\package.json') -Value '{"scripts":{"build":"vite build"}}' -Encoding Ascii
    New-Item -ItemType Junction -Path (Join-Path $fixtureRoot 'apps\web\node_modules') -Target $stubDirectory | Out-Null
    foreach ($language in @('python', 'java', 'csharp', 'cpp')) {
        Set-Content -LiteralPath (Join-Path $fixtureRoot "content\$language\course.yaml") -Value 'language: placeholder' -Encoding Ascii
    }

    return @{
        Root = $fixtureRoot
        StubDirectory = $stubDirectory
    }
}

function Remove-ReleaseFixture {
    param([hashtable]$Fixture)
    if (Test-Path $Fixture.Root) {
        # 先摘除联接，避免递归删除进入联接目标。
        foreach ($junction in @(
            (Join-Path $Fixture.Root '.venv\Scripts'),
            (Join-Path $Fixture.Root 'apps\web\node_modules')
        )) {
            if (Test-Path $junction) {
                [System.IO.Directory]::Delete($junction, $false)
            }
        }
        [System.IO.Directory]::Delete($Fixture.Root, $true)
    }
}

Describe 'release-check.ps1' {
    It 'refuses to certify a run with E2E skipped' {
        $output = powershell -NoProfile -ExecutionPolicy Bypass -File $releaseCheckScript -SkipE2E 2>&1
        $LASTEXITCODE | Should Not Be 0
        ($output | Out-String) | Should Not Match '全部通过'
    }
    It 'runs the full ordered battery and exits 0 when every step succeeds' {
        $fixture = New-ReleaseFixture
        try {
            $env:PATH = "$($fixture.StubDirectory);$env:PATH"
            powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $fixture.Root 'scripts\release-check.ps1') -ProjectRoot $fixture.Root 2>&1 | Out-Null
            $env:PATH = $env:PATH.Replace($fixture.StubDirectory + ';', '')
            $LASTEXITCODE | Should Be 0

            $logDirectory = (Get-ChildItem (Join-Path $fixture.Root 'docs\audit\release\runs') -Directory | Select-Object -First 1).FullName + '\logs'
            Test-Path $logDirectory | Should Be $true
            $contractLog = Get-ChildItem -LiteralPath $logDirectory -Filter '*-api-contract-drift.log.json'
            ($contractLog | Get-Content -Raw | ConvertFrom-Json).exit_code | Should Be 0
            $pythonCalls = Get-Content (Join-Path $fixture.StubDirectory 'python-calls.log')
            @($pythonCalls | Where-Object { $_ -match 'validate\.py' }).Count | Should Be 4
            @($pythonCalls | Where-Object { $_ -match 'release-content\.py' }).Count | Should Be 1
            @($pythonCalls | Where-Object { $_ -match 'core_coverage_gate\.py' }).Count | Should Be 1
            $nodeCalls = Get-Content (Join-Path $fixture.StubDirectory 'node-calls.log')
            @($nodeCalls | Where-Object { $_ -match 'vitest' }).Count | Should Be 1
            @($nodeCalls | Where-Object { $_ -match 'vite\.js' }).Count | Should Be 1
            # E2E 分两步：python 旅程单独先跑（对全局继续学习位置敏感），其余电池第二步。
            @($nodeCalls | Where-Object { $_ -match 'cli\.js test' }).Count | Should Be 2
            @($nodeCalls | Where-Object { $_ -match 'cli\.js test' })[0] | Should Match 'python-journey\.spec\.ts'
        } finally {
            Remove-ReleaseFixture $fixture
        }
    }

    It 'propagates the first failing exit code and records the failure in the log' {
        $fixture = New-ReleaseFixture -PythonExit '3'
        try {
            $env:PATH = "$($fixture.StubDirectory);$env:PATH"
            $output = powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $fixture.Root 'scripts\release-check.ps1') -ProjectRoot $fixture.Root 2>&1
            $env:PATH = $env:PATH.Replace($fixture.StubDirectory + ';', '')
            $LASTEXITCODE | Should Be 3
            ($output | Out-String) | Should Match '失败|退出码 3'
            $logDirectory = (Get-ChildItem (Join-Path $fixture.Root 'docs\audit\release\runs') -Directory | Select-Object -First 1).FullName + '\logs'
            Test-Path $logDirectory | Should Be $true
            $metadata = Get-Content (Join-Path $logDirectory '01-content-validate-python.log.json') -Raw | ConvertFrom-Json
            $metadata.exit_code | Should Be 3
        } finally {
            Remove-ReleaseFixture $fixture
        }
    }

    It 'propagates node failures from the frontend battery' {
        $fixture = New-ReleaseFixture -NodeExit '7'
        try {
            $env:PATH = "$($fixture.StubDirectory);$env:PATH"
            powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $fixture.Root 'scripts\release-check.ps1') -ProjectRoot $fixture.Root 2>&1 | Out-Null
            $env:PATH = $env:PATH.Replace($fixture.StubDirectory + ';', '')
            $LASTEXITCODE | Should Be 7
        } finally {
            Remove-ReleaseFixture $fixture
        }
    }
}
