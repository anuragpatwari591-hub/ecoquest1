param([switch]$Quiet)
# Stops the EcoQuest web server and the MySQL database cleanly.
$mysqlBin = "C:\Program Files\MySQL\MySQL Server 8.4\bin"
Add-Type -AssemblyName PresentationFramework

$conn = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }

if (Get-NetTCPConnection -LocalPort 3306 -State Listen -ErrorAction SilentlyContinue) {
    & "$mysqlBin\mysqladmin.exe" -uroot shutdown 2>$null
}
if (-not $Quiet) { [System.Windows.MessageBox]::Show("EcoQuest and its database have been stopped.", "EcoQuest", "OK", "Information") | Out-Null }
