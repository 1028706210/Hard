$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$verifyScript = Join-Path $repoRoot 'scripts\verify-toolchain.ps1'
$bootstrapScripts = @(
    (Join-Path $repoRoot 'scripts\bootstrap-python.ps1'),
    (Join-Path $repoRoot 'scripts\bootstrap-dotnet.ps1'),
    (Join-Path $repoRoot 'scripts\bootstrap-msys2.ps1')
)
$msys2BootstrapScript = Join-Path $repoRoot 'scripts\bootstrap-msys2.ps1'

$verificationScriptExists = Test-Path -LiteralPath $verifyScript
if ($verificationScriptExists) {
    . $verifyScript
}

Describe 'D-drive toolchain health checks' {
    It 'rejects C-drive install roots before any bootstrap download starts' {
        $missingBootstrapScripts = @($bootstrapScripts | Where-Object { -not (Test-Path -LiteralPath $_) })
        $missingBootstrapScripts.Count | Should Be 0

        if ($missingBootstrapScripts.Count -gt 0) {
            return
        }

        foreach ($bootstrapScript in $bootstrapScripts) {
            {
                & $bootstrapScript `
                    -InstallRoot 'C:\DevTools\blocked' `
                    -InstallerUri 'https://example.invalid/installer' `
                    -ExpectedSha256 ('0' * 64)
            } | Should Throw '安装目标不得位于 C: 盘'
        }
    }

    It 'uses the MSYS2 GUI installer arguments for the fixed D-drive root' {
        . $msys2BootstrapScript `
            -InstallerUri 'https://example.invalid/msys2-x86_64-latest.exe' `
            -ExpectedSha256 ('0' * 64) `
            -WhatIf

        $installerArguments = Get-Msys2GuiInstallerArguments -InstallRoot 'D:\DevTools\msys64'

        ($installerArguments -join '|') | Should Be 'in|--confirm-command|--accept-messages|--root|D:/DevTools/msys64'
    }

    It 'rejects an MSYS2 self-extracting archive before any setup action' {
        {
            & $msys2BootstrapScript `
                -InstallerUri 'https://example.invalid/msys2-base-x86_64-latest.sfx.exe' `
                -ExpectedSha256 ('0' * 64) `
                -WhatIf
        } | Should Throw 'SFX'
    }

    It 'resumes MSYS2 provisioning from a recognized partial installation' {
        . $msys2BootstrapScript `
            -InstallerUri 'https://example.invalid/msys2-x86_64-latest.exe' `
            -ExpectedSha256 ('0' * 64) `
            -WhatIf

        $partialInstallRoot = Join-Path $TestDrive 'partial-msys64'
        $msys2BinDirectory = Join-Path $partialInstallRoot 'usr\bin'
        New-Item -ItemType Directory -Force -Path $msys2BinDirectory | Out-Null
        foreach ($executable in @('bash.exe', 'pacman.exe')) {
            New-Item -ItemType File -Force -Path (Join-Path $msys2BinDirectory $executable) | Out-Null
        }

        (Get-Msys2BootstrapAction -InstallRoot $partialInstallRoot) | Should Be 'Provision'

        $unknownInstallRoot = Join-Path $TestDrive 'unknown-msys64'
        New-Item -ItemType Directory -Force -Path $unknownInstallRoot | Out-Null
        Set-Content -LiteralPath (Join-Path $unknownInstallRoot 'unexpected.txt') -Value 'keep' -Encoding Ascii

        (Get-Msys2BootstrapAction -InstallRoot $unknownInstallRoot) | Should Be 'Reject'
    }

    It 'plans MSYS2 shell initialization, two updates, and GCC installation' {
        . $msys2BootstrapScript `
            -InstallerUri 'https://example.invalid/msys2-x86_64-latest.exe' `
            -ExpectedSha256 ('0' * 64) `
            -WhatIf

        $commands = @(Get-Msys2BashCommands `
            -CacheDirectory 'D:\DevTools\cache\msys2' `
            -GccPackage 'mingw-w64-ucrt-x86_64-gcc')

        $commands.Count | Should Be 4
        $commands[0] | Should Be ' '
        $commands[1] | Should Be 'pacman --noconfirm --cachedir D:/DevTools/cache/msys2 -Syuu'
        $commands[2] | Should Be 'pacman --noconfirm --cachedir D:/DevTools/cache/msys2 -Syuu'
        $commands[3] | Should Be 'pacman --noconfirm --cachedir D:/DevTools/cache/msys2 -S --needed mingw-w64-ucrt-x86_64-gcc'
    }

    It 'rejects Codex and Workbuddy Python executable paths' {
        if (-not $verificationScriptExists) {
            $verificationScriptExists | Should Be $true
            return
        }

        foreach ($internalPythonPath in @(
            'C:\Users\tester\.codex\python\python.exe',
            'C:\Users\tester\Workbuddy\runtime\python.exe'
        )) {
            $report = Get-ToolHealthReport `
                -Name 'python' `
                -Path $internalPythonPath `
                -VersionPattern '^Python\s+3\.13\.\d+$' `
                -RequiredRoot 'D:\DevTools\python'

            $report.healthy | Should Be $false
            $report.detail | Should Match 'Codex|Workbuddy'
        }
    }

    It 'rejects a fixed install root that passes through a reparse point' {
        if (-not $verificationScriptExists) {
            $verificationScriptExists | Should Be $true
            return
        }

        $reparseFixture = Join-Path $repoRoot ('.pester-reparse-' + [guid]::NewGuid().ToString('N'))
        $reparseTarget = Join-Path $reparseFixture 'toolchain-target'
        $reparseParent = Join-Path $reparseFixture 'DevTools'

        try {
            New-Item -ItemType Directory -Force -Path $reparseTarget | Out-Null
            New-Item -ItemType Junction -Path $reparseParent -Target $reparseTarget | Out-Null

            $linkedPythonRoot = Join-Path $reparseParent 'python'
            {
                Assert-ManagedInstallRoot `
                    -InstallRoot $linkedPythonRoot `
                    -ExpectedRoot $linkedPythonRoot `
                    -ToolName 'Python'
            } | Should Throw '重解析点'
        }
        finally {
            if (Test-Path -LiteralPath $reparseFixture) {
                Remove-Item -LiteralPath $reparseFixture -Recurse -Force
            }
        }
    }

    It 'marks a tool without the required version as unhealthy' {
        if (-not $verificationScriptExists) {
            $verificationScriptExists | Should Be $true
            return
        }

        $toolWithoutVersion = Join-Path $TestDrive 'python.cmd'
        Set-Content -LiteralPath $toolWithoutVersion -Value '@echo Python runtime' -Encoding Ascii

        $report = Get-ToolHealthReport `
            -Name 'python' `
            -Path $toolWithoutVersion `
            -VersionPattern '^Python\s+3\.13\.\d+$' `
            -RequiredRoot $TestDrive

        $report.healthy | Should Be $false
        ($null -eq $report.version) | Should Be $true
        $report.detail | Should Match '版本'
    }

    It 'marks a matching version command with a nonzero exit code as unhealthy' {
        if (-not $verificationScriptExists) {
            $verificationScriptExists | Should Be $true
            return
        }

        $failingTool = Join-Path $TestDrive 'failing-python.cmd'
        Set-Content -LiteralPath $failingTool -Value @('@echo Python 3.13.9', '@exit /b 7') -Encoding Ascii

        $report = Get-ToolHealthReport `
            -Name 'python' `
            -Path $failingTool `
            -VersionPattern '^Python\s+3\.13\.\d+$' `
            -RequiredRoot $TestDrive

        $report.version | Should Be '3.13.9'
        $report.healthy | Should Be $false
        $report.detail | Should Match '退出码 7'
    }

    It 'returns the documented JSON health report fields' {
        if (-not $verificationScriptExists) {
            $verificationScriptExists | Should Be $true
            return
        }

        $toolWithoutVersion = Join-Path $TestDrive 'unknown-version.cmd'
        Set-Content -LiteralPath $toolWithoutVersion -Value '@echo unknown' -Encoding Ascii

        $report = Get-ToolHealthReport `
            -Name 'python' `
            -Path $toolWithoutVersion `
            -VersionPattern '^Python\s+3\.13\.\d+$' `
            -RequiredRoot $TestDrive

        $reportFields = @($report.PSObject.Properties.Name) -join ','
        foreach ($field in @('name', 'path', 'version', 'healthy', 'detail')) {
            $reportFields | Should Match "(^|,)$field(,|$)"
        }
    }
}
