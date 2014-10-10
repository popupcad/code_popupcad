Attribute VB_Name = "vectors"
Function ComparePoints(p1, p2 As Variant) As Boolean
    Dim tol As Double
    tol = 0.00001
    Dim p3() As Variant
    p3 = minus(p1, p2)
    ComparePoints = dot(p3, p3) < tol * tol
End Function
Function dot(p1, p2 As Variant) As Double
    Dim l As Double
    Dim ii As Long
    l = 0
    For ii = LBound(p1) To UBound(p1)
        l = l + p1(ii) * p2(ii)
    Next ii
    dot = l
End Function
Function minus(p1, p2 As Variant) As Variant
    Dim pout()  As Variant
    Dim l As Long
    Dim ii As Long
    l = -1
    For ii = LBound(p1) To UBound(p1)
        l = ArrayFunctions.AddItem(pout, p1(ii) - p2(ii), l)
    Next ii
    minus = pout
End Function
Function plus(p1, p2 As Variant) As Variant
    Dim pout()  As Variant
    Dim l As Long
    Dim ii As Long
    l = -1
    For ii = LBound(p1) To UBound(p1)
        l = ArrayFunctions.AddItem(pout, p1(ii) + p2(ii), l)
    Next ii
    plus = pout
End Function

