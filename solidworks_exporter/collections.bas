Attribute VB_Name = "collections"
Function addkeyed(dict As Collection, variable As Collection)
    dict.Add variable, variable.item("id")
End Function

Function ExtendCollection(c1 As Collection, c2 As Collection)
    Dim item As Variant
    
    For Each item In c2
        c1.Add item
    Next item
    
End Function

Function ExtendCollectionFromArray(c1 As Collection, c2 As Variant)
    Dim item As Variant
    Dim ii As Integer
    
    For ii = LBound(c2) To UBound(c2)
        c1.Add c2(ii)
    Next
End Function


Function face_index(c As Collection, item As SldWorks.Face2) As Integer
Dim element As SldWorks.Face2
Dim ii As Integer

ii = 0
index = -1

For Each element In c
    If item.IsSame(element) Then
        index = ii
    End If
    ii = ii + 1
Next element

face_index = index
End Function

Function reverse_c(c As Collection)
    Dim c_in As Collection
    Dim c_out As New Collection
    Dim ii, jj, l As Integer
    
    Set c_in = c
    l = c_in.Count
    For ii = 1 To l
        jj = l - ii + 1
        c_out.Add c_in(jj)
    Next ii
    Set c = c_out

End Function

Function UniqueID() As String
    Static i As Integer
    Dim s As String
    
    s = CStr(i)
    i = i + 1
    UniqueID = s
    
End Function

Function replace(c As Collection, replacement, index)
    Dim cin As Collection
    Dim cout As New Collection
    
    Set cin = c
    l = cin.Count
    
    For ii = 1 To index - 1
        cout.Add cin(ii)
    Next ii
    cout.Add replacement
    For ii = index + 1 To l
        cout.Add cin(ii)
    Next ii
    Set c = cout


End Function
