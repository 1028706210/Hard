[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param(
    [string]$InstallRoot = 'D:\DevTools\dotnet',

    [Parameter(Mandatory = $true)]
    [string]$InstallerUri,

    [Parameter(Mandatory = $true)]
    [string]$ExpectedSha256,

    [string]$Version = '10.0.100'
)

. (Join-Path $PSScriptRoot 'verify-toolchain.ps1')

Assert-ManagedInstallRoot -InstallRoot $InstallRoot -ExpectedRoot 'D:\DevTools\dotnet' -ToolName '.NET'
$null = Set-ToolchainProcessCacheDefaults

$dotnetPath = Join-Path $InstallRoot 'dotnet.exe'
$report = Get-ToolHealthReport -Name 'dotnet' -Path $dotnetPath -VersionPattern '^\s*10\.\d+\.\d+\s*$' -RequiredRoot $InstallRoot
if ($report.healthy) {
    Write-Output $report
    return
}

Assert-InstallDirectoryAvailable -InstallRoot $InstallRoot -ToolName '.NET'

if ($PSCmdlet.ShouldProcess($InstallRoot, "安装 .NET SDK $Version")) {
    $installer = Get-VerifiedInstaller `
        -InstallerUri $InstallerUri `
        -ExpectedSha256 $ExpectedSha256 `
        -CacheDirectory (Join-Path $script:CacheRoot 'installers') `
        -ToolName '.NET'

    $arguments = @(
        '-NoProfile',
        '-ExecutionPolicy',
        'Bypass',
        '-File',
        $installer,
        '-InstallDir',
        $InstallRoot,
        '-Version',
        $Version,
        '-NoPath'
    )
    $process = Start-Process -FilePath 'powershell.exe' -ArgumentList $arguments -Wait -PassThru
    if ($process.ExitCode -ne 0) {
        throw ".NET 安装器以退出码 $($process.ExitCode) 结束。"
    }

    $report = Get-ToolHealthReport -Name 'dotnet' -Path $dotnetPath -VersionPattern '^\s*10\.\d+\.\d+\s*$' -RequiredRoot $InstallRoot
    if (-not $report.healthy) {
        throw ".NET 安装后健康检查失败：$($report.detail)"
    }

    Write-Output $report
}
