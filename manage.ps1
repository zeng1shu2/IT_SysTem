<#
 .SYNOPSIS
    前后端服务一键管理脚本（启动 / 停止 / 重启 / 状态查看）

 .DESCRIPTION
    通过监听端口精确识别前后端进程并启停，避免误杀其它进程。
    日志写入 .runtime/ 目录。

 .EXAMPLE
    .\manage.ps1 start     # 启动前后端
    .\manage.ps1 stop      # 停止前后端
    .\manage.ps1 restart   # 重启前后端
    .\manage.ps1 status    # 查看运行状态
#>
param(
    [Parameter(Position = 0)]
    [ValidateSet('start', 'stop', 'restart', 'status', 'help')]
    [string]$Action = 'help'
)

$ErrorActionPreference = 'SilentlyContinue'

# 脚本所在目录即项目根目录
$Root = $PSScriptRoot
if (-not $Root) { $Root = (Get-Location).Path }

$FrontendDir = Join-Path $Root 'frontend'
$BackendDir  = Join-Path $Root 'backend'
$RuntimeDir  = Join-Path $Root '.runtime'
$FE_PORT = 5173
$BE_PORT = 8000

# 优先使用项目配套的运行环境，缺失时回退到 PATH
$NodeExe = 'C:\Users\Administrator\.workbuddy\binaries\node\versions\22.22.2\node.exe'
if (-not (Test-Path $NodeExe)) { $NodeExe = 'node' }
$PyExe   = Join-Path $BackendDir 'venv\Scripts\python.exe'
if (-not (Test-Path $PyExe)) { $PyExe = 'python' }
$ViteJs  = Join-Path $FrontendDir 'node_modules\vite\bin\vite.js'

$FE_OUT = Join-Path $RuntimeDir 'frontend.out.log'
$FE_ERR = Join-Path $RuntimeDir 'frontend.err.log'
$BE_OUT = Join-Path $RuntimeDir 'backend.out.log'
$BE_ERR = Join-Path $RuntimeDir 'backend.err.log'

function Get-PidByPort($port) {
    $result = @()
    netstat -ano | Select-String ":$port\s" | Where-Object { $_ -match 'LISTENING' } | ForEach-Object {
        $parts = ($_ -split '\s+') | Where-Object { $_ -ne '' }
        $last = $parts[-1]
        if ($last -match '^\d+$') { $result += [int]$last }
    }
    return ($result | Sort-Object -Unique)
}

function Test-Port($port) {
    return ((Get-PidByPort $port).Count -gt 0)
}

function Stop-ByPort($port, $name) {
    if (-not (Test-Port $port)) {
        Write-Host ("[{0}] 未运行" -f $name) -ForegroundColor Gray
        return
    }
    Write-Host ("[{0}] 停止中 (端口 {1})..." -f $name, $port) -ForegroundColor Yellow
    $tries = 0
    while ((Test-Port $port) -and $tries -lt 6) {
        $tries++
        foreach ($p in (Get-PidByPort $port)) {
            $proc = Get-Process -Id $p -ErrorAction SilentlyContinue
            if ($proc) {
                try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { }
            }
        }
        if (Test-Port $port) { Start-Sleep -Seconds 1 }
    }
    if (Test-Port $port) {
        Write-Host ("[{0}] 停止失败，端口仍被占用，请手动检查: netstat -ano | findstr :{1}" -f $name, $port) -ForegroundColor Red
    } else {
        Write-Host ("[{0}] 已停止" -f $name) -ForegroundColor Green
    }
}

function Start-All {
    # 前端
    if (Test-Port $FE_PORT) {
        Write-Host ("[前端] 已在运行 (端口 {0})" -f $FE_PORT) -ForegroundColor Green
    } else {
        if (-not (Test-Path $ViteJs)) {
            Write-Host "[前端] 缺少 vite.js，请先在 frontend/ 下执行 npm install" -ForegroundColor Red
        } else {
            Write-Host ("[前端] 启动中 (端口 {0})..." -f $FE_PORT) -ForegroundColor Cyan
            $ps = Start-Process -FilePath $NodeExe `
                -ArgumentList @($ViteJs, '--host', '--port', $FE_PORT, '--strictPort') `
                -WorkingDirectory $FrontendDir `
                -RedirectStandardOutput $FE_OUT -RedirectStandardError $FE_ERR `
                -WindowStyle Hidden -PassThru
            if ($ps.HasExited) {
                Write-Host ("[前端] 启动即退出，退出码 {0}，请查看日志: {1}" -f $ps.ExitCode, $FE_ERR) -ForegroundColor Red
            }
        }
    }

    # 后端
    if (Test-Port $BE_PORT) {
        Write-Host ("[后端] 已在运行 (端口 {0})" -f $BE_PORT) -ForegroundColor Green
    } else {
        if (-not (Test-Path $PyExe)) {
            Write-Host "[后端] 缺少 venv/python，请确认 backend/venv 已创建" -ForegroundColor Red
        } else {
            Write-Host ("[后端] 启动中 (端口 {0})..." -f $BE_PORT) -ForegroundColor Cyan
            $ps = Start-Process -FilePath $PyExe `
                -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', $BE_PORT) `
                -WorkingDirectory $BackendDir `
                -RedirectStandardOutput $BE_OUT -RedirectStandardError $BE_ERR `
                -WindowStyle Hidden -PassThru
            if ($ps.HasExited) {
                Write-Host ("[后端] 启动即退出，退出码 {0}，请查看日志: {1}" -f $ps.ExitCode, $BE_ERR) -ForegroundColor Red
            }
        }
    }

    Start-Sleep -Seconds 5
    Write-Host "---- 启动完成 ----" -ForegroundColor Cyan
    Show-Status
}

function Show-Status {
    $fe = Test-Port $FE_PORT
    $be = Test-Port $BE_PORT
    Write-Host ""
    Write-Host ("前端 (:{0}) : {1}" -f $FE_PORT, $(if ($fe) { '运行中' } else { '已停止' })) `
        -ForegroundColor $(if ($fe) { 'Green' } else { 'Red' })
    Write-Host ("后端 (:{0}) : {1}" -f $BE_PORT, $(if ($be) { '运行中' } else { '已停止' })) `
        -ForegroundColor $(if ($be) { 'Green' } else { 'Red' })
    Write-Host ""
    Write-Host ("前端访问: http://localhost:{0}" -f $FE_PORT) -ForegroundColor White
    Write-Host ("后端文档: http://localhost:{0}/docs" -f $BE_PORT) -ForegroundColor White
    if ($fe -and -not $be) { Write-Host "提示: 后端未运行，前端接口会请求失败" -ForegroundColor Yellow }
    if (-not $fe -and $be) { Write-Host "提示: 前端未运行，请在浏览器打开上面的地址" -ForegroundColor Yellow }
    if (-not $fe -and -not $be) {
        Write-Host "提示: 前后端均未运行，执行 .\manage.ps1 start 启动" -ForegroundColor Yellow
    }
    if (($fe -or $be) -and -not ($fe -and $be)) {
        Write-Host ("启动排错日志在 .runtime\ 目录 (frontend/backend 的 .out.log 与 .err.log)" -f $FE_PORT) -ForegroundColor Gray
    }
}

switch ($Action) {
    'start' {
        if (-not (Test-Path $RuntimeDir)) { New-Item -ItemType Directory -Path $RuntimeDir | Out-Null }
        Start-All
    }
    'stop' {
        Stop-ByPort $FE_PORT '前端'
        Stop-ByPort $BE_PORT '后端'
    }
    'restart' {
        Stop-ByPort $FE_PORT '前端'
        Stop-ByPort $BE_PORT '后端'
        Start-Sleep -Seconds 1
        Start-All
    }
    'status' { Show-Status }
    default {
        Write-Host "用法: .\manage.ps1 <start|stop|restart|status>" -ForegroundColor Cyan
        Write-Host "  start   - 启动前后端" -ForegroundColor White
        Write-Host "  stop    - 停止前后端" -ForegroundColor White
        Write-Host "  restart - 先停止再启动前后端" -ForegroundColor White
        Write-Host "  status  - 查看前后端运行状态" -ForegroundColor White
        Write-Host ""
        Write-Host "也可直接双击 manage.bat 使用。" -ForegroundColor Gray
    }
}
