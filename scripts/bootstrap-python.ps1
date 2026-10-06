[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param(
    [string]$InstallRoot = 'D:\DevTools\python',

    [Parameter(Mandatory = $true)]
    [string]$InstallerUri,

    [Parameter(Mandatory = $true)]
    [string]$ExpectedSha256
)

. (Join-Path $PSScriptRoot 'verify-toolchain.ps1')

Assert-ManagedInstallRoot -InstallRoot $InstallRoot -ExpectedRoot 'D:\DevTools\python' -ToolName 'Python'
$null = Set-ToolchainProcessCacheDefaults

$pythonPath = Join-Path $InstallRoot 'python.exe'
$report = Get-ToolHealthReport -Name 'python' -Path $pythonPath -VersionPattern '^Python\s+3\.13\.\d+$' -RequiredRoot $InstallRoot
if ($report.healthy) {
    Write-Output $report
    return
}

Assert-InstallDirectoryAvailable -InstallRoot $InstallRoot -ToolName 'Python'

if ($PSCmdlet.ShouldProcess($InstallRoot, '安装 Python 3.13')) {
    $installer = Get-VerifiedInstaller `
        -InstallerUri $InstallerUri `
        -ExpectedSha256 $ExpectedSha256 `
        -CacheDirectory (Join-Path $script:CacheRoot 'installers') `
        -ToolName 'Python'

    $arguments = @(
        '/quiet',
        'InstallAllUsers=0',
        'PrependPath=0',
        "TargetDir=$InstallRoot",
        'Include_launcher=0',
        'Include_pip=1',
        'Include_test=0'
    )
    $process = Start-Process -FilePath $installer -ArgumentList $arguments -Wait -PassThru
    if ($process.ExitCode -ne 0) {
        throw "Python 安装器以退出码 $($process.ExitCode) 结束。"
    }

    $report = Get-ToolHealthReport -Name 'python' -Path $pythonPath -VersionPattern '^Python\s+3\.13\.\d+$' -RequiredRoot $InstallRoot
    if (-not $report.healthy) {
        throw "Python 安装后健康检查失败：$($report.detail)"
    }

    Write-Output $report
}
