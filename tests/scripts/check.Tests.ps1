$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$checkScript = Join-Path $repoRoot 'scripts\check.ps1'
$managedPythonRoot = 'D:\DevTools\python'

function New-CheckFixture {
    param(
        [switch]$IncludeUvicorn,
        [int]$CoverageExitCode = 0
    )

    $fixtureRoot = Join-Path $repoRoot ('.pester-check-' + [guid]::NewGuid().ToString('N'))
    $scriptDirectory = Join-Path $fixtureRoot 'scripts'
    $pythonEnvironment = Join-Path $fixtureRoot '.venv'
    $commandDirectory = Join-Path $fixtureRoot 'test-bin'
    $requirementsDirectory = Join-Path $fixtureRoot 'apps\api'
    $gateDirectory = Join-Path $fixtureRoot 'apps\api\tests'

    New-Item -ItemType Directory -Force -Path $scriptDirectory, $pythonEnvironment, $commandDirectory, $requirementsDirectory, $gateDirectory | Out-Null
    New-Item -ItemType Junction -Path (Join-Path $pythonEnvironment 'Scripts') -Target $managedPythonRoot | Out-Null
    Copy-Item -LiteralPath $checkScript -Destination (Join-Path $scriptDirectory 'check.ps1')
    Set-Content -LiteralPath (Join-Path $fixtureRoot 'pnpm-lock.yaml') -Value 'lockfileVersion: 9.0' -Encoding Ascii

    $requirements = @('fastapi==0.141.1')
    if ($IncludeUvicorn) {
        $requirements += 'uvicorn==0.30.6'
    }
    Set-Content -LiteralPath (Join-Path $requirementsDirectory 'requirements.lock') -Value $requirements -Encoding Ascii
    Set-Content -LiteralPath (Join-Path $gateDirectory 'core_coverage_gate.py') -Value "raise SystemExit($CoverageExitCode)" -Encoding Ascii

    Set-Content -LiteralPath (Join-Path $commandDirectory 'node.cmd') -Value @(
        '@echo off',
        'if "%~1"=="--version" echo v24.17.0',
        'exit /b 0'
    ) -Encoding Ascii
    Set-Content -LiteralPath (Join-Path $commandDirectory 'pnpm.cmd') -Value @(
        '@echo off',
        'if "%~1"=="--version" echo 11.19.0',
        'exit /b 0'
    ) -Encoding Ascii

    return [pscustomobject]@{
        Root = $fixtureRoot
        Script = Join-Path $scriptDirectory 'check.ps1'
        CommandDirectory = $commandDirectory
    }
}

function Remove-CheckFixture {
    param([Parameter(Mandatory = $true)]$Fixture)

    if (Test-Path -LiteralPath $Fixture.Root) {
        Remove-Item -LiteralPath $Fixture.Root -Recurse -Force
    }
}

function Invoke-FixtureCheck {
    param(
        [Parameter(Mandatory = $true)]$Fixture,
        [Parameter(Mandatory = $true)][string]$Mode
    )

    $originalPath = $env:PATH
    $environmentNames = @(
        'NPM_CONFIG_CACHE',
        'npm_config_store_dir',
        'PIP_CACHE_DIR',
        'NUGET_PACKAGES',
        'NUGET_HTTP_CACHE_PATH',
        'DOTNET_CLI_HOME',
        'MSYS2_CACHE_DIR'
    )
    $originalValues = @{}
    foreach ($name in $environmentNames) {
        $originalValues[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
    }
    try {
        $env:PATH = "$($Fixture.CommandDirectory);$originalPath"
        & $Fixture.Script -Mode $Mode
    }
    finally {
        $env:PATH = $originalPath
        foreach ($name in $environmentNames) {
            [Environment]::SetEnvironmentVariable($name, $originalValues[$name], 'Process')
        }
    }
}

function Get-FixtureCheckFailure {
    param(
        [Parameter(Mandatory = $true)]$Fixture,
        [Parameter(Mandatory = $true)][string]$Mode
    )

    try {
        $null = Invoke-FixtureCheck -Fixture $Fixture -Mode $Mode
    }
    catch {
        return $_.Exception.Message
    }

    return $null
}

Describe 'Phase D local run preflight' {
    It 'fails smoke when the backend lock omits the ASGI runtime dependency' {
        $fixture = New-CheckFixture
        try {
            $failure = Get-FixtureCheckFailure -Fixture $fixture -Mode Smoke
            ($null -eq $failure) | Should Be $false
            $failure | Should Match 'ASGI.*uvicorn'
        }
        finally {
            Remove-CheckFixture -Fixture $fixture
        }
    }

    It 'fails smoke for C-drive product data and cache configuration' {
        $fixture = New-CheckFixture -IncludeUvicorn
        $originalValues = @{
            HARD_DATA_DIR = $env:HARD_DATA_DIR
            HARD_BACKUP_DIR = $env:HARD_BACKUP_DIR
            HARD_EXPORT_DIR = $env:HARD_EXPORT_DIR
            HARD_RUNNER_WORK_DIR = $env:HARD_RUNNER_WORK_DIR
            NPM_CONFIG_CACHE = $env:NPM_CONFIG_CACHE
            npm_config_store_dir = $env:npm_config_store_dir
            PIP_CACHE_DIR = $env:PIP_CACHE_DIR
            NUGET_PACKAGES = $env:NUGET_PACKAGES
            NUGET_HTTP_CACHE_PATH = $env:NUGET_HTTP_CACHE_PATH
        }

        try {
            foreach ($name in $originalValues.Keys) {
                foreach ($resetName in $originalValues.Keys) {
                    if ($null -eq $originalValues[$resetName]) {
                        Remove-Item -Path ("Env:{0}" -f $resetName) -ErrorAction SilentlyContinue
                    }
                    else {
                        Set-Item -Path ("Env:{0}" -f $resetName) -Value $originalValues[$resetName]
                    }
                }
                Set-Item -Path ("Env:{0}" -f $name) -Value 'C:\blocked\path'
                $failure = Get-FixtureCheckFailure -Fixture $fixture -Mode Smoke
                ($null -eq $failure) | Should Be $false
                $failure | Should Match 'C:'
            }
        }
        finally {
            foreach ($name in $originalValues.Keys) {
                if ($null -eq $originalValues[$name]) {
                    Remove-Item -Path ("Env:{0}" -f $name) -ErrorAction SilentlyContinue
                }
                else {
                    Set-Item -Path ("Env:{0}" -f $name) -Value $originalValues[$name]
                }
            }
            Remove-CheckFixture -Fixture $fixture
        }
    }

    It 'fails smoke for a drive-relative C-drive cache path' {
        $fixture = New-CheckFixture -IncludeUvicorn
        $originalCache = $env:NPM_CONFIG_CACHE
        try {
            $env:NPM_CONFIG_CACHE = 'C:blocked-cache'
            $failure = Get-FixtureCheckFailure -Fixture $fixture -Mode Smoke
            ($null -eq $failure) | Should Be $false
            $failure | Should Match 'C:'
        }
        finally {
            [Environment]::SetEnvironmentVariable('NPM_CONFIG_CACHE', $originalCache, 'Process')
            Remove-CheckFixture -Fixture $fixture
        }
    }

    It 'fails API mode when the backend core coverage gate fails' {
        $fixture = New-CheckFixture -IncludeUvicorn -CoverageExitCode 17
        try {
            $failure = Get-FixtureCheckFailure -Fixture $fixture -Mode Api
            ($null -eq $failure) | Should Be $false
            $failure | Should Match '核心覆盖率.*17'
        }
        finally {
            Remove-CheckFixture -Fixture $fixture
        }
    }

    It 'publishes a loopback-only manual run contract with migration, FTS readiness, and port checks' {
        $guide = Join-Path $repoRoot 'docs\setup\phase-d-local-run.md'

        (Test-Path -LiteralPath $guide) | Should Be $true
        $content = Get-Content -Raw -LiteralPath $guide
        $content | Should Match 'migrate_database'
        $content | Should Match 'ensure_content_index'
        $content | Should Match '--host 127\.0\.0\.1'
        $content | Should Match '/api/v1/health/ready'
        $content | Should Match 'Get-NetTCPConnection'
        $content | Should Match 'Ctrl\+C'
    }
}
