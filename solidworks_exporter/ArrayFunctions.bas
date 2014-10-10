Attribute VB_Name = "ArrayFunctions"
Function AddItem(lines As Variant, line As Variant, l As Long) As Long
    ReDim Preserve lines(l + 1)
    l = UBound(lines) - LBound(lines)
    lines(l) = line
    AddItem = l
End Function

Function reverse(list As Variant)
    Dim ii, l As Long
    Dim list2() As Variant
    
    l = UBound(list) - LBound(list)
    ReDim list2(l)
    
    For ii = 0 To l
        list2(ii) = list(l - ii)
    Next ii
    
    list = list2
End Function

Function IsVarArrayEmpty(anArray As Variant)

Dim i As Integer

On Error Resume Next
    i = UBound(anArray, 1)
If Err.Number = 0 Then
    IsVarArrayEmpty = False
Else
    IsVarArrayEmpty = True
End If

End Function
