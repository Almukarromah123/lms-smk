$dataDir = Join-Path $PSScriptRoot ".mysql-local\data"
$pidFile = Join-Path $dataDir "Ciming.pid"

if (-not (Test-Path $pidFile)) {
    Write-Output "MySQL lokal tidak sedang berjalan."
    exit 0
}

$mysqlPid = (Get-Content $pidFile | Select-Object -First 1).Trim()

if (-not $mysqlPid) {
    Write-Output "MySQL lokal tidak sedang berjalan."
    exit 0
}

if (Get-Process -Id $mysqlPid -ErrorAction SilentlyContinue) {
    Stop-Process -Id $mysqlPid -Force
}

Write-Output "MySQL lokal dihentikan."
