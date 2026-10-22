$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$startScript = Join-Path $repoRoot 'scripts\start-hard.ps1'
$stopScript = Join-Path $repoRoot 'scripts\stop-hard.ps1'

function New-RunFixture {
    # 建立隔离项目夹具：.venv\Scripts 与 apps\web\node_modules 指向桩命令目录。
    # 桩解析 --port 参数并在该端口充当 HTTP/TCP 应答器，模拟 uvicorn/vite 监听。
    param()

    $fixtureRoot = Join-Path $repoRoot ('.pester-start-' + [guid]::NewGuid().ToString('N'))
    $scriptsDirectory = Join-Path $fixtureRoot 'scripts'
    $venvScripts = Join-Path $fixtureRoot '.venv\Scripts'
    $stubDirectory = Join-Path $fixtureRoot 'stub-bin'
    New-Item -ItemType Directory -Force -Path $scriptsDirectory, $venvScripts, $stubDirectory, (Join-Path $fixtureRoot 'apps\web'), (Join-Path $fixtureRoot 'content'), (Join-Path $fixtureRoot 'docs\setup') | Out-Null

    Copy-Item -LiteralPath $startScript -Destination (Join-Path $scriptsDirectory 'start-hard.ps1')
    Copy-Item -LiteralPath $stopScript -Destination (Join-Path $scriptsDirectory 'stop-hard.ps1')
    Copy-Item -LiteralPath (Join-Path $repoRoot 'scripts\prepare-hard.py') -Destination (Join-Path $scriptsDirectory 'prepare-hard.py')

    $stubServer = Join-Path $stubDirectory 'stub-server.ps1'
    Set-Content -LiteralPath $stubServer -Value @(
        'param([int]$Port)',
        '$listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, $Port)',
        '$listener.Start()',
        'try {',
        '    for ($index = 0; $index -lt 600; $index++) {',
        '        if (-not $listener.Pending()) { Start-Sleep -Milliseconds 100; continue }',
        '        try {',
        '        $client = $listener.AcceptTcpClient()',
        '        $stream = $client.GetStream()',
        '        $body = [System.Text.Encoding]::UTF8.GetBytes(''{"status":"ok"}'')',
        '        $header = [System.Text.Encoding]::ASCII.GetBytes("HTTP/1.1 200 OK`r`nContent-Type: application/json`r`nContent-Length: $($body.Length)`r`nConnection: close`r`n`r`n")',
        '        $buffer = New-Object byte[] 1024',
        '        $null = $stream.Read($buffer, 0, $buffer.Length)',
        '        $stream.Write($header, 0, $header.Length)',
        '        $stream.Write($body, 0, $body.Length)',
        '        $stream.Close()',
        '        $client.Close()',
        '        } catch { }',
        '    }',
        '} finally {',
        '    $listener.Stop()',
        '}'
    ) -Encoding Ascii

    # 桩解析 --port 后同步运行应答器（cmd 保持存活，可被 taskkill /T 整树回收）。
    Set-Content -LiteralPath (Join-Path $stubDirectory 'python.cmd') -Value @(
        '@echo off',
        'if "%~nx1"=="prepare-hard.py" if "%HARD_STUB_MIGRATION_FAIL%"=="1" exit /b 7',
        'if "%~nx1"=="prepare-hard.py" exit /b 0',
        'set STUB_PORT=',
        ':loop',
        'if "%~1"=="" goto run',
        'if "%~1"=="--port" (',
        '  set STUB_PORT=%~2',
        '  goto run',
        ')',
        'shift',
        'goto loop',
        ':run',
        'powershell -NoProfile -ExecutionPolicy Bypass -File "%HARD_STUB_SERVER%" -Port %STUB_PORT%'
    ) -Encoding Ascii
    Set-Content -LiteralPath (Join-Path $stubDirectory 'node.cmd') -Value @(
        '@echo off',
        'set STUB_PORT=',
        ':loop',
        'if "%~1"=="" goto run',
        'if "%~1"=="--port" (',
        '  set STUB_PORT=%~2',
        '  goto run',
        ')',
        'shift',
        'goto loop',
        ':run',
        'powershell -NoProfile -ExecutionPolicy Bypass -File "%HARD_STUB_SERVER%" -Port %STUB_PORT%'
    ) -Encoding Ascii

    New-Item -ItemType Junction -Path $venvScripts -Target $stubDirectory | Out-Null
    # vite 桩是真实 node 程序：解析 --port 后充当 HTTP 应答器并保持监听（模拟 vite --strictPort）。
    $viteStub = Join-Path $stubDirectory 'vite\bin\vite.js'
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $viteStub) | Out-Null
    Set-Content -LiteralPath $viteStub -Value @(
        'const net = require("net");',
        'const argv = process.argv.slice(2);',
        'const portIndex = argv.indexOf("--port");',
        'const port = portIndex >= 0 ? Number(argv[portIndex + 1]) : 4173;',
        'const server = net.createServer(function (socket) {',
        '    socket.on("error", function () { });',
        '    socket.resume();',
        '    socket.end("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n{\"status\":\"ok\"}");',
        '});',
        'server.on("error", function () { });',
        'server.listen(port, "127.0.0.1");'
    ) -Encoding Ascii
    Set-Content -LiteralPath (Join-Path $fixtureRoot 'docs\setup\toolchain-lock.json') -Value '{}' -Encoding Ascii
    New-Item -ItemType Junction -Path (Join-Path $fixtureRoot 'apps\web\node_modules') -Target $stubDirectory | Out-Null

    $portReservations = @(
        [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0),
        [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
    )
    foreach ($reservation in $portReservations) { $reservation.Start() }
    $ports = @($portReservations | ForEach-Object { $_.LocalEndpoint.Port })
    foreach ($reservation in $portReservations) { $reservation.Stop() }
    return @{
        Root = $fixtureRoot
        ApiPort = $ports[0]
        WebPort = $ports[1]
        StubServer = $stubServer
        # 匹配用调用路径：start-hard 经 junction 调用 node，命令行保留 node_modules 路径。
        ViteStub = (Join-Path $fixtureRoot 'apps\web\node_modules\vite\bin\vite.js')
    }
}

function Remove-RunFixture {
    param([hashtable]$Fixture)
    Get-StubServiceProcesses -Fixture $Fixture | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
    # 句柄释放略滞后于进程终止，短暂等待后再删目录。
    Start-Sleep -Milliseconds 500
    if (Test-Path $Fixture.Root) {
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

function Get-StubServiceProcesses {
    # 只统计引用本夹具桩文件路径的服务进程（API=powershell 桩、Web=node 桩）。
    # 夹具路径含唯一 GUID，避免机器上其他运行（并行/遗留）的进程干扰计数断言。
    param([hashtable]$Fixture)
    $apiPattern = [regex]::Escape($Fixture.StubServer)
    $webPattern = [regex]::Escape($Fixture.ViteStub)
    Get-CimInstance Win32_Process -Filter "Name = 'powershell.exe' OR Name = 'node.exe'" |
        Where-Object { ($_.CommandLine -match $apiPattern) -or ($_.CommandLine -match $webPattern) }
}

Describe 'start-hard.ps1' {
    It 'does not start services when database preparation fails' {
        $fixture = New-RunFixture
        $previous = $env:HARD_STUB_MIGRATION_FAIL
        try {
            $env:HARD_STUB_MIGRATION_FAIL = '1'
            $output = powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $fixture.Root 'scripts\start-hard.ps1') -ProjectRoot $fixture.Root -ApiPort $fixture.ApiPort -WebPort $fixture.WebPort 2>&1
            $LASTEXITCODE | Should Not Be 0
            ($output | Out-String) | Should Match '数据库准备失败.*7'
            Get-StubServiceProcesses -Fixture $fixture | Should BeNullOrEmpty
            Test-Path (Join-Path $fixture.Root '.tool-cache\hard-start\run.json') | Should Be $false
        } finally {
            $env:HARD_STUB_MIGRATION_FAIL = $previous
            Remove-RunFixture $fixture
        }
    }

    It 'rejects duplicate start when a previous run state is present' {
        $fixture = New-RunFixture
        try {
            $stateDirectory = Join-Path $fixture.Root '.tool-cache\hard-start'
            New-Item -ItemType Directory -Force -Path $stateDirectory | Out-Null
            Set-Content -LiteralPath (Join-Path $stateDirectory 'run.json') -Value '{"api_pid":0}' -Encoding Ascii
            $output = powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $fixture.Root 'scripts\start-hard.ps1') -ProjectRoot $fixture.Root -ApiPort $fixture.ApiPort -WebPort $fixture.WebPort 2>&1
            $LASTEXITCODE | Should Not Be 0
            ($output | Out-String) | Should Match '已在运行'
        } finally {
            Remove-RunFixture $fixture
        }
    }

    It 'reports a clear error when foreign programs occupy the ports' {
        $fixture = New-RunFixture
        try {
            $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, $fixture.ApiPort)
            $listener.Start()
            try {
                $output = powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $fixture.Root 'scripts\start-hard.ps1') -ProjectRoot $fixture.Root -ApiPort $fixture.ApiPort -WebPort $fixture.WebPort 2>&1
                $LASTEXITCODE | Should Not Be 0
                ($output | Out-String) | Should Match '占用'
            } finally {
                $listener.Stop()
            }
        } finally {
            Remove-RunFixture $fixture
        }
    }

    It 'recovers started processes and fails clearly when the health probe never succeeds' {
        $fixture = New-RunFixture
        try {
            $output = powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $fixture.Root 'scripts\start-hard.ps1') -ProjectRoot $fixture.Root -ApiPort $fixture.ApiPort -WebPort $fixture.WebPort -HealthTimeoutSeconds 3 2>&1
            $LASTEXITCODE | Should Not Be 0
            ($output | Out-String) | Should Match '启动失败|健康检查'
            Start-Sleep -Seconds 1
            Get-StubServiceProcesses -Fixture $fixture | Should BeNullOrEmpty
        } finally {
            Remove-RunFixture $fixture
        }
    }

    It 'starts api and web successfully and stop-hard reclaims the exact tree' {
        $fixture = New-RunFixture
        try {
            $env:HARD_STUB_SERVER = $fixture.StubServer
            $beforeCount = @(Get-StubServiceProcesses -Fixture $fixture).Count
            # 长驻桩进程使 Start-Process -Wait 永久阻塞（-Wait 等待全部后代），
            # -PassThru 的 ExitCode 在 PS 5.1 又不可靠；改由包装会话捕获结果写哨兵文件。
            $startOut = Join-Path $fixture.Root 'start-out.log'
            $startErr = Join-Path $fixture.Root 'start-err.log'
            $codeFile = Join-Path $fixture.Root 'start-code.txt'
            $scriptPath = Join-Path $fixture.Root 'scripts\start-hard.ps1'
            $inner = "try { & '$scriptPath' -ProjectRoot '$($fixture.Root)' -ApiPort $($fixture.ApiPort) -WebPort $($fixture.WebPort); `$code = 0 } catch { `$code = 1 }; Set-Content -LiteralPath '$codeFile' -Value `$code"
            $null = Start-Process powershell -WindowStyle Hidden -PassThru -RedirectStandardOutput $startOut -RedirectStandardError $startErr -ArgumentList @(
                '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', $inner
            )
            $deadline = (Get-Date).AddSeconds(60)
            while (-not (Test-Path -LiteralPath $codeFile) -and (Get-Date) -lt $deadline) {
                Start-Sleep -Milliseconds 300
            }
            (Test-Path -LiteralPath $codeFile) | Should Be $true
            (Get-Content -LiteralPath $codeFile -Raw).Trim() | Should Be '0'
            $text = (Get-Content -LiteralPath $startOut -Raw) + (Get-Content -LiteralPath $startErr -Raw)
            $text | Should Match "http://127\.0\.0\.1:$($fixture.ApiPort)"
            $text | Should Match "http://127\.0\.0\.1:$($fixture.WebPort)"
            $text | Should Match 'runner-work'
            $afterCount = @(Get-StubServiceProcesses -Fixture $fixture).Count
            $afterCount | Should Be ($beforeCount + 2)

            $stopOutput = powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $fixture.Root 'scripts\stop-hard.ps1') -ProjectRoot $fixture.Root 2>&1
            $LASTEXITCODE | Should Be 0
            ($stopOutput | Out-String) | Should Match '已停止'
            Start-Sleep -Seconds 1
            Get-StubServiceProcesses -Fixture $fixture | Should BeNullOrEmpty
        } finally {
            $env:HARD_STUB_SERVER = $null
            Remove-RunFixture $fixture
        }
    }
}

Describe 'stop-hard.ps1' {
    It 'is idempotent when nothing is running' {
        $fixture = New-RunFixture
        try {
            $output = powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $fixture.Root 'scripts\stop-hard.ps1') -ProjectRoot $fixture.Root 2>&1
            $LASTEXITCODE | Should Be 0
            ($output | Out-String) | Should Match '未发现'
        } finally {
            Remove-RunFixture $fixture
        }
    }
}
