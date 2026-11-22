' Double-click to start EcoQuest (no console window).
Set sh = CreateObject("WScript.Shell")
folder = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
sh.Run "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & folder & "\start_ecoquest.ps1""", 0, False
