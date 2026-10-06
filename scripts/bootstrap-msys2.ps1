[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param(
    [string]$InstallRoot = 'D:\DevTools\msys64',

    [Parameter(Mandatory = $true)]
    [string]$InstallerUri,

    [Parameter(Mandatory = $true)]
    [string]$ExpectedSha256,

    [ValidatePattern('^[A-Za-z0-9@._+:-]+$')]
    [string]$GccPackage = 'mingw-w64-ucrt-x86_64-gcc'
)

. (Join-Path $PSScriptRoot 'verify-toolchain.ps1')

function Assert-Msys2GuiInstallerUri {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$InstallerUri
    )

    $installerPath = ([Uri]$InstallerUri).AbsolutePath
    if ($installerPath -match '(?i)\.sfx\.exe$') {
        throw 'MSYS2 SFX 安装包使用另一套参数，当前脚本仅支持 GUI 安装器。'
    }

    if ($installerPath -notmatch '(?i)\.exe$') {
        throw '当前脚本仅支持 MSYS2 GUI .exe 安装器。'
    }
}

function Get-Msys2GuiInstallerArguments {
    [OutputType([string[]])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$InstallRoot
    )

    return @(
        'in',
        '--confirm-command',
        '--accept-messages',
        '--root',
        $InstallRoot.Replace('\', '/')
    )
}

function Get-Msys2BootstrapAction {
    [OutputType([string])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$InstallRoot
    )

    $msys2BinDirectory = Join-Path $InstallRoot 'usr\bin'
    $bashPath = Join-Path $msys2BinDirectory 'bash.exe'
    $pacmanPath = Join-Path $msys2BinDirectory 'pacman.exe'
    if ((Test-Path -LiteralPath $bashPath -PathType Leaf) -and
        (Test-Path -LiteralPath $pacmanPath -PathType Leaf)) {
        return 'Provision'
    }

    if (-not (Test-Path -LiteralPath $InstallRoot)) {
        return 'Install'
    }

    if (Test-Path -LiteralPath $InstallRoot -PathType Leaf) {
        return 'Reject'
    }

    if (@(Get-ChildItem -LiteralPath $InstallRoot -Force -ErrorAction Stop).Count -gt 0) {
        return 'Reject'
    }

    return 'Install'
}

function Get-Msys2BashCommands {
    [OutputType([string[]])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$CacheDirectory,

        [Parameter(Mandatory = $true)]
        [ValidatePattern('^[A-Za-z0-9@._+:-]+$')]
        [string]$GccPackage
    )

    $msys2Cache = $CacheDirectory.Replace('\', '/')
    return @(
        ' ',
        "pacman --noconfirm --cachedir $msys2Cache -Syuu",
        "pacman --noconfirm --cachedir $msys2Cache -Syuu",
        "pacman --noconfirm --cachedir $msys2Cache -S --needed $GccPackage"
    )
}

function Invoke-Msys2BashCommand {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$BashPath,

        [Parameter(Mandatory = $true)]
        [string]$Command,

        [Parameter(Mandatory = $true)]
        [string]$Description
    )

    $process = Start-Process `
        -FilePath $BashPath `
        -ArgumentList @('-lc', ('"{0}"' -f $Command)) `
        -Wait `
        -PassThru
    if ($process.ExitCode -ne 0) {
        throw "$Description 以退出码 $($process.ExitCode) 结束。请修复后重新运行脚本；脚本会保留当前 MSYS2 安装。"
    }
}

Assert-ManagedInstallRoot -InstallRoot $InstallRoot -ExpectedRoot 'D:\DevTools\msys64' -ToolName 'MSYS2'
Assert-Msys2GuiInstallerUri -InstallerUri $InstallerUri
$null = Set-ToolchainProcessCacheDefaults

$gccPath = Join-Path $InstallRoot 'ucrt64\bin\g++.exe'
$report = Get-ToolHealthReport -Name 'msys2-gcc' -Path $gccPath -VersionPattern '\b\d+\.\d+\.\d+\b' -RequiredRoot $InstallRoot
if ($report.healthy) {
    Write-Output $report
    return
}

$bootstrapAction = Get-Msys2BootstrapAction -InstallRoot $InstallRoot
if ($bootstrapAction -eq 'Reject') {
    throw 'MSYS2 目标目录已有内容，但未找到可恢复的 MSYS2 bash 与 pacman；拒绝覆盖。'
}

if ($PSCmdlet.ShouldProcess($InstallRoot, '安装或恢复 MSYS2 UCRT64 GCC')) {
    if ($bootstrapAction -eq 'Install') {
        Assert-InstallDirectoryAvailable -InstallRoot $InstallRoot -ToolName 'MSYS2'

        $installer = Get-VerifiedInstaller `
            -InstallerUri $InstallerUri `
            -ExpectedSha256 $ExpectedSha256 `
            -CacheDirectory (Join-Path $script:CacheRoot 'installers') `
            -ToolName 'MSYS2'

        $installerArguments = Get-Msys2GuiInstallerArguments -InstallRoot $InstallRoot
        $process = Start-Process -FilePath $installer -ArgumentList $installerArguments -Wait -PassThru
        if ($process.ExitCode -ne 0) {
            throw "MSYS2 GUI 安装器以退出码 $($process.ExitCode) 结束。"
        }

        if ((Get-Msys2BootstrapAction -InstallRoot $InstallRoot) -ne 'Provision') {
            throw 'MSYS2 GUI 安装器未在目标目录提供 bash 与 pacman，拒绝继续。'
        }
    }

    $msys2BinDirectory = Join-Path $InstallRoot 'usr\bin'
    $bashPath = Join-Path $msys2BinDirectory 'bash.exe'
    $msys2Cache = $env:MSYS2_CACHE_DIR
    New-Item -ItemType Directory -Force -Path $msys2Cache | Out-Null
    $env:MSYSTEM = 'UCRT64'

    $commands = @(Get-Msys2BashCommands -CacheDirectory $msys2Cache -GccPackage $GccPackage)
    Invoke-Msys2BashCommand -BashPath $bashPath -Command $commands[0] -Description 'MSYS2 首次初始化'
    Invoke-Msys2BashCommand -BashPath $bashPath -Command $commands[1] -Description 'MSYS2 第一轮系统更新'
    Invoke-Msys2BashCommand -BashPath $bashPath -Command $commands[2] -Description 'MSYS2 第二轮系统更新'
    Invoke-Msys2BashCommand -BashPath $bashPath -Command $commands[3] -Description 'MSYS2 GCC 安装'

    $report = Get-ToolHealthReport -Name 'msys2-gcc' -Path $gccPath -VersionPattern '\b\d+\.\d+\.\d+\b' -RequiredRoot $InstallRoot
    if (-not $report.healthy) {
        throw "MSYS2 安装后健康检查失败：$($report.detail)"
    }

    Write-Output $report
}
