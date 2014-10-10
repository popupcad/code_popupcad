Attribute VB_Name = "Matrices"
Function Zeros(size As Integer) As Variant
    Dim a() As Variant
    ReDim a(size - 1, size - 1)
    Dim ii, jj As Integer
    For ii = 0 To size - 1
        For jj = 0 To size - 1
            a(ii, jj) = 0
        Next jj
    Next ii
    Zeros = a
End Function

Function Eye(size As Integer) As Variant
    Dim a As Variant
    Dim ii As Integer
    
    a = Zeros(size)
    For ii = 0 To size - 1
        a(ii, ii) = 1
    Next ii
    
    Eye = a
End Function

Function build_from_vectors(a As Variant) As Variant
    Dim innerelement As Variant
    Dim m, n, ii, jj As Long
    Dim A_out() As Variant
    
    innerelement = a(0)
    m = UBound(a, 1) - LBound(a, 1)
    n = UBound(innerelement, 1) - LBound(innerelement, 1)
    ReDim A_out(m, n)
    
    For ii = 0 To m
        For jj = 0 To n
            A_out(ii, jj) = a(ii)(jj)
        Next jj
    Next ii
    
    build_from_vectors = A_out
End Function

Function toString(a As Variant) As collection
    Dim strings As New collection
    Dim ii, jj As Long
    Dim s As String
    For ii = LBound(a, 1) To UBound(a, 1)
        s = ""
        For jj = LBound(a, 2) To UBound(a, 2)
            s = s & Format((a(ii, jj)), "0.00000000000000000")
            If jj <> UBound(a, 2) Then
                s = s & ","
            End If
        Next jj
        strings.Add s
    Next ii
    Set toString = strings
End Function

Function toYaml(a As Variant) As collection
    Dim strings As collection
    Set strings = toString(a)
    stringcollections.PadStrings strings, "- - [", "  - [", "]"
    Set toYaml = strings
End Function
Function toYaml2(a As Variant) As collection
    Dim strings As collection
    Set strings = toString(a)
    stringcollections.PadStrings strings, "- [", "- [", "]"
    Set toYaml2 = strings
End Function

Function buildFromMathTransform(tin As mathTransform) As Variant
    Dim T_out As Variant
    Dim transformin As Variant
    Dim ii, jj, kk As Long
    transformin = tin.ArrayData
    
    T_out = Matrices.Zeros(4)
    kk = 0
    For ii = 0 To 2
        For jj = 0 To 2
            T_out(ii, jj) = transformin(kk)
            kk = kk + 1
        Next jj
    Next ii
    
    For ii = 0 To 2
        T_out(ii, 3) = transformin(kk)
        kk = kk + 1
    Next ii
    T_out(3, 3) = transformin(kk)
            
    buildFromMathTransform = T_out
End Function

