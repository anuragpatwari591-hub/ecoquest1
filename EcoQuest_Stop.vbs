' Double-click to stop EcoQuest and its database.
Set sh = CreateObject("WScript.Shell")
folder = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
sh.Run "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & folder & "\stop_ecoquest.ps1""", 0, False
