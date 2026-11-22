# Installs EcoQuest as a normal Windows program for the current user:
#   %LOCALAPPDATA%\Programs\EcoQuest\EcoQuest.exe + Desktop and Start Menu shortcuts.
# Run build_exe.ps1 first (it creates dist\EcoQuest).
$root   = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $root "dist\EcoQuest"
$target = Join-Path $env:LOCALAPPDATA "Programs\EcoQuest"
if (-not (Test-Path "$source\EcoQuest.exe")) { throw "dist\EcoQuest\EcoQuest.exe not found - run build_exe.ps1 first." }

Get-Process EcoQuest -ErrorAction SilentlyContinue | ForEach-Object { $_.CloseMainWindow() | Out-Null }
Start-Sleep -Seconds 4
Get-Process EcoQuest -ErrorAction SilentlyContinue | Stop-Process -Force

New-Item -ItemType Directory -Force $target | Out-Null
robocopy $source $target /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
New-Item -ItemType Directory -Force (Join-Path $target "logs") | Out-Null

$ws = New-Object -ComObject WScript.Shell
$places = @([Environment]::GetFolderPath("Desktop"), (Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"))
foreach ($dir in $places) {
    $l = $ws.CreateShortcut((Join-Path $dir "EcoQuest.lnk"))
    $l.TargetPath = Join-Path $target "EcoQuest.exe"
    $l.WorkingDirectory = $target
    $l.IconLocation = Join-Path $target "EcoQuest.exe"
    $l.Description = "EcoQuest - Gamified Environmental Education Platform"
    $l.Save()
}
# the old launcher-style stop shortcut is no longer needed (closing the window stops everything)
Remove-Item (Join-Path ([Environment]::GetFolderPath("Desktop")) "EcoQuest - Stop.lnk") -ErrorAction SilentlyContinue
Write-Output "Installed to $target"
