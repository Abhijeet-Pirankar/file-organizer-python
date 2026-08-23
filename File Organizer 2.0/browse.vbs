Set objShell = CreateObject("Shell.Application")
Set objFolder = objShell.BrowseForFolder(0, "Select Folder to Organize", 0, 0)
If objFolder Is Nothing Then
    Wscript.Echo ""
Else
    Wscript.Echo objFolder.Self.Path
End If
