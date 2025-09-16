#NoEnv
SendMode Input
SetWorkingDir %A_ScriptDir%

; ================= VS CODE =================

; Win + N → Create new file and open in VS Code
#n::
    folderPath := ""
    shell := ComObjCreate("Shell.Application")
    for window in shell.Windows
    {
        if (window.hwnd = WinActive("A"))
        {
            folderPath := window.Document.Folder.Self.Path
            break
        }
    }
    if (folderPath = "")
    {
        MsgBox, Could not detect current folder!
        return
    }

    InputBox, fileName, New File, Enter filename (with extension):, , 300, 130
    if ErrorLevel
        return

    newFile := folderPath "\" fileName
    FileAppend,, %newFile%

    Run, "C:\Users\meet\AppData\Local\Programs\Microsoft VS Code\Code.exe" "%newFile%"
return

; Win + O → Open selected file in VS Code
#o::
    ClipSaved := ClipboardAll
    Clipboard := ""
    Send, ^c
    ClipWait, 0.5

    If (Clipboard = "")
    {
        MsgBox, No file selected or clipboard operation failed.
        Return
    }

    Run, "C:\Users\meet\AppData\Local\Programs\Microsoft VS Code\Code.exe" "%Clipboard%"
    Clipboard := ClipSaved
Return


; ================= WINDSURF =================

; Win + Shift + N → Create new file and open in Windsurf
#+n::
    folderPath := ""
    shell := ComObjCreate("Shell.Application")
    for window in shell.Windows
    {
        if (window.hwnd = WinActive("A"))
        {
            folderPath := window.Document.Folder.Self.Path
            break
        }
    }
    if (folderPath = "")
    {
        MsgBox, Could not detect current folder!
        return
    }

    InputBox, fileName, New File, Enter filename (with extension):, , 300, 130
    if ErrorLevel
        return

    newFile := folderPath "\" fileName
    FileAppend,, %newFile%

    Run, "C:\Users\meet\AppData\Local\Programs\Windsurf\Windsurf.exe" "%newFile%"
return

; Win + Shift + O → Open selected file in Windsurf
#+o::
    ClipSaved := ClipboardAll
    Clipboard := ""
    Send, ^c
    ClipWait, 0.5

    If (Clipboard = "")
    {
        MsgBox, No file selected or clipboard operation failed.
        Return
    }

    Run, "C:\Users\meet\AppData\Local\Programs\Windsurf\Windsurf.exe" "%Clipboard%"
    Clipboard := ClipSaved
Return
