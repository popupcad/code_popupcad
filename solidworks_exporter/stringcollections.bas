Attribute VB_Name = "stringcollections"

Function PadStrings(lines As collection, s_before_firstline, s_before As String, s_after As String)
    Dim linesout As New collection
    Dim item As Variant
    
    item = lines(1)
    lines.Remove 1
    linesout.Add s_before_firstline & item & s_after
    
    For Each item In lines
        linesout.Add s_before & item & s_after
    Next item
    
    Set lines = linesout
End Function

Function WriteFile(s As collection, filename As String)
    Dim fs, a
    Dim line As Variant
    
    Set fs = CreateObject("Scripting.FileSystemObject")
    Set a = fs.CreateTextFile(filename, True)
    
    For Each line In s
        a.WriteLine (line)
    Next
    
    a.Close
End Function

