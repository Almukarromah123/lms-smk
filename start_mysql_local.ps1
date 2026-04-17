$mysqlBase = "C:\Program Files\MySQL\MySQL Server 9.6"
$dataDir = Join-Path $PSScriptRoot ".mysql-local\data"
$logDir = Join-Path $PSScriptRoot ".mysql-local"
$stdoutLog = Join-Path $logDir "mysqld.out.log"
$stderrLog = Join-Path $logDir "mysqld.err.log"
$pidFile = Join-Path $dataDir "Ciming.pid"

if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Force $dataDir | Out-Null
    & "$mysqlBase\bin\mysqld.exe" --no-defaults --initialize-insecure --basedir="$mysqlBase" --datadir="$dataDir"
}

if (Test-Path $pidFile) {
    $mysqlPid = (Get-Content $pidFile | Select-Object -First 1).Trim()
    if ($mysqlPid -and (Get-Process -Id $mysqlPid -ErrorAction SilentlyContinue)) {
        Write-Output "MySQL lokal sudah berjalan."
        exit 0
    }
}

$args = "--no-defaults --standalone --console --basedir=""$mysqlBase"" --datadir=""$dataDir"" --bind-address=127.0.0.1 --port=3306 --mysqlx=0"

Start-Process -FilePath "$mysqlBase\bin\mysqld.exe" `
    -ArgumentList $args `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -WindowStyle Hidden

Write-Output "MySQL lokal sedang dijalankan di 127.0.0.1:3306"
