$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Describe 'stop-hard ownership' {
    It 'keeps run state when the verified process cannot be terminated' {
        $fixture = Join-Path $repoRoot ('.pester-identity-' + [guid]::NewGuid().ToString('N'))
        $directory = Join-Path $fixture '.tool-cache\hard-start'
        New-Item -ItemType Directory -Force -Path $directory | Out-Null
        $moment=[datetime]'2026-01-01T00:00:00Z'
        $ticks=$moment.ToUniversalTime().Ticks.ToString()
        @{project_root=$fixture;api_pid=987001;web_pid=987002;api_port=29991;web_port=29992;api_started_ticks=$ticks;web_started_ticks=$ticks;api_executable='D:\owned.exe';web_executable='D:\owned.exe'} | ConvertTo-Json | Set-Content (Join-Path $directory 'run.json')
        Mock Get-Process { [pscustomobject]@{Id=987001;StartTime=([datetime]'2026-01-01T00:00:00Z');Path='D:\owned.exe'} }
        Mock taskkill.exe { $global:LASTEXITCODE=5 }
        try {
            $message=''
            try { & (Join-Path $repoRoot 'scripts\stop-hard.ps1') -ProjectRoot $fixture } catch { $message=$_.Exception.Message }
            $message | Should Match 'taskkill.*5'
            Test-Path (Join-Path $directory 'run.json') | Should Be $true
        } finally {
            $resolved = [IO.Path]::GetFullPath($fixture)
            if (-not $resolved.StartsWith($repoRoot + '\.pester-identity-')) { throw 'Unsafe fixture path' }
            Remove-Item -LiteralPath $resolved -Recurse -Force
        }
    }
    It 'rejects unowned records before making HTTP or kill calls' -TestCases @(@{Reason='project'},@{Reason='pid'}) {
        param($Reason)
        $fixture = Join-Path $repoRoot ('.pester-identity-' + [guid]::NewGuid().ToString('N'))
        $directory = Join-Path $fixture '.tool-cache\hard-start'
        New-Item -ItemType Directory -Force -Path $directory | Out-Null
        @{project_root=$(if($Reason -eq 'project'){'D:\different'}else{$fixture});api_pid=987001;web_pid=987002;api_port=29991;web_port=29992;api_started_ticks='1';web_started_ticks='1';api_executable='D:\old.exe';web_executable='D:\old.exe'} | ConvertTo-Json | Set-Content (Join-Path $directory 'run.json')
        Mock Invoke-RestMethod {}
        Mock Get-Process { [pscustomobject]@{Id=987001;StartTime=(Get-Date);Path='D:\unrelated.exe'} }
        Mock taskkill.exe {}
        Mock Get-NetTCPConnection {}
        try {
            $rejected = $false
            try { & (Join-Path $repoRoot 'scripts\stop-hard.ps1') -ProjectRoot $fixture } catch { $rejected = $true }
            $rejected | Should Be $true
            Assert-MockCalled taskkill.exe -Times 0 -Exactly -Scope It
            Assert-MockCalled Invoke-RestMethod -Times 0 -Exactly -Scope It
        } finally {
            $resolved = [IO.Path]::GetFullPath($fixture)
            if (-not $resolved.StartsWith($repoRoot + '\.pester-identity-')) { throw 'Unsafe fixture path' }
            Remove-Item -LiteralPath $resolved -Recurse -Force
        }
    }
}
