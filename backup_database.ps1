param([switch]$Quiet)
# Saves a full backup of the EcoQuest database to the backups folder (SQL file).
$root     = Split-Path -Parent $MyInvocation.MyCommand.Path
$mysqlBin = "C:\Program Files\MySQL\MySQL Server 8.4\bin"
Add-Type -AssemblyName PresentationFramework

# read DB settings from .env
$cfg = @{}
Get-Content (Join-Path $root ".env") | ForEach-Object { if ($_ -match '^\s*([A-Z_]+)=(.*)$') { $cfg[$Matches[1]] = $Matches[2].Trim() } }
$stamp = Get-Date -Format "yyyyMMdd_HHmm"
$file  = Join-Path $root "backups\ecoquest_$stamp.sql"
New-Item -ItemType Directory -Force (Join-Path $root "backups") | Out-Null

$env:MYSQL_PWD = $cfg["DB_PASSWORD"]
& "$mysqlBin\mysqldump.exe" -h $cfg["DB_HOST"] -P $cfg["DB_PORT"] -u $cfg["DB_USER"] --routines --single-transaction --no-tablespaces --result-file="$file" $cfg["DB_NAME"]
$ok = ($LASTEXITCODE -eq 0) -and (Test-Path $file)
Remove-Item Env:\MYSQL_PWD
if ($ok) { Write-Output "Backup saved: $file"; if (-not $Quiet) { [System.Windows.MessageBox]::Show("Backup saved:`n$file", "EcoQuest backup", "OK", "Information") | Out-Null } }
else     { [System.Windows.MessageBox]::Show("Backup failed. Is EcoQuest (MySQL) running?", "EcoQuest backup", "OK", "Error") | Out-Null }
