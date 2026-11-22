# Removes the installed EcoQuest program and its shortcuts.
# Your database (C:\Users\<you>\ecoquest-mysql-data) and project folder are NOT touched.
$target = Join-Path $env:LOCALAPPDATA "Programs\EcoQuest"
Get-Process EcoQuest -ErrorAction SilentlyContinue | ForEach-Object { $_.CloseMainWindow() | Out-Null }
Start-Sleep -Seconds 4
Get-Process EcoQuest -ErrorAction SilentlyContinue | Stop-Process -Force
Remove-Item $target -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path ([Environment]::GetFolderPath("Desktop")) "EcoQuest.lnk") -ErrorAction SilentlyContinue
Remove-Item (Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\EcoQuest.lnk") -ErrorAction SilentlyContinue
Write-Output "EcoQuest uninstalled (your data was kept)."
