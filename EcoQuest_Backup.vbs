' Double-click to save a backup of the EcoQuest database.
Set sh = CreateObject("WScript.Shell")
folder = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
sh.Run "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & folder & "\backup_database.ps1""", 0, False
