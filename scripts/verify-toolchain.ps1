[CmdletBinding()]
param(
    [string]$Output,
    [string]$PythonPath = 'D:\DevTools\python\python.exe',
    [string]$DotnetPath = 'D:\DevTools\dotnet\dotnet.exe',
    [string]$Msys2Path = 'D:\DevTools\msys64\ucrt64\bin\g++.exe',
    [string]$JavaPath
)

Set-StrictMode -Version Latest

$script:DevToolsRoot = 'D:\DevTools'
$script:CacheRoot = 'D:\DevTools\cache'

function ConvertTo-NormalizedPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    if ($fullPath.Length -gt 3) {
        return $fullPath.TrimEnd([char[]]@('\', '/'))
    }

    return $fullPath
}

function Test-PathWithinRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Root
    )

    $normalizedPath = ConvertTo-NormalizedPath -Path $Path
    $normalizedRoot = ConvertTo-NormalizedPath -Path $Root
    $comparison = [System.StringComparison]::OrdinalIgnoreCase

    return $normalizedPath.Equals($normalizedRoot, $comparison) -or
        $normalizedPath.StartsWith($normalizedRoot + '\', $comparison)
}

function Get-ReparsePointAncestor {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $candidate = ConvertTo-NormalizedPath -Path $Path
    while (-not [string]::IsNullOrWhiteSpace($candidate)) {
        if (Test-Path -LiteralPath $candidate) {
            $item = Get-Item -LiteralPath $candidate -Force -ErrorAction Stop
            if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                return $item.FullName
            }
        }

        $parent = Split-Path -Parent $candidate
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent.Equals($candidate, [System.StringComparison]::OrdinalIgnoreCase)) {
            break
        }

        $candidate = $parent
    }

    return $null
}

function New-ToolHealthReport {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$Path,

        [AllowNull()]
        [object]$Version,

        [Parameter(Mandatory = $true)]
        [bool]$Healthy,

        [Parameter(Mandatory = $true)]
        [string]$Detail
    )

    return [pscustomobject][ordered]@{
        name = $Name
        path = $Path
        version = $Version
        healthy = $Healthy
        detail = $Detail
    }
}

function Get-ToolHealthReport {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$VersionPattern,

        [string]$RequiredRoot
    )

    if ($Name -eq 'python' -and $Path -match '(?i)(^|[\\/])(?:\.codex|codex|workbuddy)([\\/]|$)') {
        return New-ToolHealthReport -Name $Name -Path $Path -Version $null -Healthy $false -Detail '拒绝使用 Codex 或 Workbuddy 内部 Python 路径。'
    }

    if (-not [string]::IsNullOrWhiteSpace($RequiredRoot) -and -not (Test-PathWithinRoot -Path $Path -Root $RequiredRoot)) {
        return New-ToolHealthReport -Name $Name -Path $Path -Version $null -Healthy $false -Detail ("可执行文件必须位于 {0}。" -f $RequiredRoot)
    }

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return New-ToolHealthReport -Name $Name -Path $Path -Version $null -Healthy $false -Detail '未找到可执行文件。'
    }

    try {
        $versionOutput = @(& $Path '--version' 2>&1)
        $versionExitCode = $LASTEXITCODE
        $rawOutput = @($versionOutput | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine
    }
    catch {
        return New-ToolHealthReport -Name $Name -Path $Path -Version $null -Healthy $false -Detail ("无法读取版本：{0}" -f $_.Exception.Message)
    }

    $versionMatch = [regex]::Match($rawOutput, '(?<!\d)(\d+(?:\.\d+){1,3})(?!\d)')
    $version = if ($versionMatch.Success) { $versionMatch.Groups[1].Value } else { $null }

    if ($null -ne $versionExitCode -and $versionExitCode -ne 0) {
        $actual = if ([string]::IsNullOrWhiteSpace($rawOutput)) { '无输出' } else { $rawOutput.Trim() }
        return New-ToolHealthReport -Name $Name -Path $Path -Version $version -Healthy $false -Detail ("版本命令以退出码 {0} 结束：{1}" -f $versionExitCode, $actual)
    }

    if (-not [regex]::IsMatch($rawOutput, $VersionPattern, [System.Text.RegularExpressions.RegexOptions]::Multiline)) {
        $actual = if ([string]::IsNullOrWhiteSpace($rawOutput)) { '无输出' } else { $rawOutput.Trim() }
        return New-ToolHealthReport -Name $Name -Path $Path -Version $version -Healthy $false -Detail ("版本不符合要求：{0}" -f $actual)
    }

    return New-ToolHealthReport -Name $Name -Path $Path -Version $version -Healthy $true -Detail '健康。'
}

function Assert-ManagedInstallRoot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$InstallRoot,

        [Parameter(Mandatory = $true)]
        [string]$ExpectedRoot,

        [Parameter(Mandatory = $true)]
        [string]$ToolName
    )

    $normalizedRoot = ConvertTo-NormalizedPath -Path $InstallRoot
    $expected = ConvertTo-NormalizedPath -Path $ExpectedRoot

    if ($normalizedRoot -match '^(?i)c:\\') {
        throw "$ToolName 安装目标不得位于 C: 盘。"
    }

    if ($normalizedRoot -match '(?i)(^|[\\/])(?:\.codex|codex|workbuddy)([\\/]|$)') {
        throw "$ToolName 安装目标不得使用 Codex 或 Workbuddy 路径。"
    }

    if (-not $normalizedRoot.Equals($expected, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw ("{0} 安装目标必须固定为 {1}。" -f $ToolName, $ExpectedRoot)
    }

    $reparsePoint = Get-ReparsePointAncestor -Path $normalizedRoot
    if ($null -ne $reparsePoint) {
        throw ("{0} 安装目标不得经过重解析点：{1}。" -f $ToolName, $reparsePoint)
    }
}

function Assert-InstallDirectoryAvailable {
    param(
        [Parameter(Mandatory = $true)]
        [string]$InstallRoot,

        [Parameter(Mandatory = $true)]
        [string]$ToolName
    )

    if (-not (Test-Path -LiteralPath $InstallRoot)) {
        return
    }

    $existingItems = @(Get-ChildItem -LiteralPath $InstallRoot -Force -ErrorAction Stop)
    if ($existingItems.Count -gt 0) {
        throw "$ToolName 目标目录已存在内容，脚本拒绝覆盖现有安装。"
    }
}

function Set-ToolchainProcessCacheDefaults {
    $env:NPM_CONFIG_CACHE = Join-Path $script:CacheRoot 'npm'
    $env:npm_config_store_dir = Join-Path $script:CacheRoot 'pnpm-store'
    $env:PIP_CACHE_DIR = Join-Path $script:CacheRoot 'pip'
    $env:NUGET_PACKAGES = Join-Path $script:CacheRoot 'nuget-packages'
    $env:NUGET_HTTP_CACHE_PATH = Join-Path $script:CacheRoot 'nuget-http'
    $env:DOTNET_CLI_HOME = Join-Path $script:CacheRoot 'dotnet-cli'
    $env:MSYS2_CACHE_DIR = Join-Path $script:CacheRoot 'msys2'

    return [pscustomobject][ordered]@{
        npm = $env:NPM_CONFIG_CACHE
        pnpm = $env:npm_config_store_dir
        pip = $env:PIP_CACHE_DIR
        nuget = $env:NUGET_PACKAGES
        msys2 = $env:MSYS2_CACHE_DIR
    }
}

function Get-VerifiedInstaller {
    param(
        [Parameter(Mandatory = $true)]
        [string]$InstallerUri,

        [Parameter(Mandatory = $true)]
        [string]$ExpectedSha256,

        [Parameter(Mandatory = $true)]
        [string]$CacheDirectory,

        [Parameter(Mandatory = $true)]
        [string]$ToolName
    )

    if ($InstallerUri -notmatch '^https://') {
        throw '安装器 URL 必须使用 HTTPS。'
    }

    if ($ExpectedSha256 -notmatch '^[0-9a-fA-F]{64}$') {
        throw '安装器 SHA-256 必须是 64 位十六进制值。'
    }

    $uri = [System.Uri]$InstallerUri
    $fileName = [System.IO.Path]::GetFileName($uri.AbsolutePath)
    if ([string]::IsNullOrWhiteSpace($fileName)) {
        $fileName = "$ToolName-installer.bin"
    }

    New-Item -ItemType Directory -Force -Path $CacheDirectory | Out-Null
    $destination = Join-Path $CacheDirectory $fileName

    if (Test-Path -LiteralPath $destination -PathType Leaf) {
        $cachedHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
        if ($cachedHash.Equals($ExpectedSha256, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $destination
        }

        throw "缓存中的 $ToolName 安装器校验和不匹配；为避免覆盖，请先人工处理 $destination。"
    }

    Invoke-WebRequest -Uri $InstallerUri -OutFile $destination -UseBasicParsing
    $downloadedHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
    if (-not $downloadedHash.Equals($ExpectedSha256, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "$ToolName 安装器校验和不匹配。"
    }

    return $destination
}

if ($MyInvocation.InvocationName -ne '.') {
    if ([string]::IsNullOrWhiteSpace($JavaPath)) {
        $javac = Get-Command javac -ErrorAction SilentlyContinue
        $JavaPath = if ($null -ne $javac) { $javac.Source } else { 'javac-not-found' }
    }

    $reports = @(
        Get-ToolHealthReport -Name 'python' -Path $PythonPath -VersionPattern '^Python\s+3\.13\.\d+$' -RequiredRoot 'D:\DevTools\python'
        Get-ToolHealthReport -Name 'java' -Path $JavaPath -VersionPattern '^javac\s+17(?:\.\d+){1,2}\b'
        Get-ToolHealthReport -Name 'dotnet' -Path $DotnetPath -VersionPattern '^\s*10\.\d+\.\d+\s*$' -RequiredRoot 'D:\DevTools\dotnet'
        Get-ToolHealthReport -Name 'msys2-gcc' -Path $Msys2Path -VersionPattern '\b\d+\.\d+\.\d+\b' -RequiredRoot 'D:\DevTools\msys64'
    )

    $healthJson = ConvertTo-Json -InputObject $reports -Depth 3
    if ([string]::IsNullOrWhiteSpace($Output)) {
        Write-Output $healthJson
    }
    else {
        $outputPath = ConvertTo-NormalizedPath -Path $Output
        if ($outputPath -notmatch '^(?i)d:\\') {
            throw '健康报告必须写入 D: 盘。'
        }

        $outputDirectory = Split-Path -Parent $outputPath
        New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
        [System.IO.File]::WriteAllText($outputPath, $healthJson + [Environment]::NewLine, [System.Text.Encoding]::UTF8)
    }

    if (@($reports | Where-Object { -not $_.healthy }).Count -gt 0) {
        exit 1
    }
}
