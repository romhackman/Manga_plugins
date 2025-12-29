Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
batchFile = scriptDir & "\main_HH_Json.bat"

' 0 = fenêtre invisible, True = attendre la fin
WshShell.Run "cmd /c """ & batchFile & """", 0, True
