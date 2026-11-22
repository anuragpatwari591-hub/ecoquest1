# Starts MySQL (if needed) and EcoQuest, then opens the app in your browser.
# Double-click "EcoQuest.vbs" (or the desktop shortcut) instead of running this directly.
$root     = Split-Path -Parent $MyInvocation.MyCommand.Path
$mysqlBin = "C:\Program Files\MySQL\MySQL Server 8.4\bin"
$dataDir  = Join-Path $env:USERPROFILE "ecoquest-mysql-data"
$url      = "http://127.0.0.1:5000"
Add-Type -AssemblyName PresentationFramework

function Test-Port([int]$port) {
    return [bool](Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
}
function Wait-Port([int]$port, [int]$seconds) {
    for ($i = 0; $i -lt $seconds; $i++) { if (Test-Port $port) { return $true }; Start-Sleep -Seconds 1 }
    return $false
}
function Show-Error([string]$msg) {
    [System.Windows.MessageBox]::Show($msg, "EcoQuest", "OK", "Error") | Out-Null
}

# 1. MySQL database
if (-not (Test-Port 3306)) {
    if (-not (Test-Path "$mysqlBin\mysqld.exe")) { Show-Error "MySQL was not found at:`n$mysqlBin"; exit 1 }
    Start-Process -FilePath "$mysqlBin\mysqld.exe" -ArgumentList "--datadir=`"$dataDir`"", "--bind-address=127.0.0.1", "--port=3306" -WindowStyle Hidden
    if (-not (Wait-Port 3306 60)) { Show-Error "The MySQL database did not start."; exit 1 }
}

# 2. EcoQuest web server
if (-not (Test-Port 5000)) {
    $py = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source
    if (-not $py) { $py = (Get-Command python.exe).Source }
    Start-Process -FilePath $py -ArgumentList "run_server.py" -WorkingDirectory $root -WindowStyle Hidden
    if (-not (Wait-Port 5000 40)) { Show-Error "EcoQuest did not start.`nSee: $root\logs\server.log"; exit 1 }
}

# 3. Open the app
Start-Process $url
