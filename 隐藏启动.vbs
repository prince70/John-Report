' Hidden launcher for John-Report service (no window)
' Usage: double-click (default port 8092)
'        or with a custom port:  wscript hidden_start.vbs 8091
' Put a shortcut of this file into shell:startup for auto-start at logon
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh  = CreateObject("WScript.Shell")
Dim bat, args
bat = fso.GetParentFolderName(WScript.ScriptFullName) & "\start_prod.bat"
args = ""
If WScript.Arguments.Count > 0 Then args = " " & WScript.Arguments(0)
sh.Run """" & bat & """" & args, 0, False
