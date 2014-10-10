Attribute VB_Name = "FaceInfo"
Function FaceInfo(face As SldWorks.Face2) As Variant
    Dim faceloops() As Variant
    Dim loops As Variant
    Dim jj As Long
    Dim loop1 As SldWorks.Loop2
    Dim l As Long
    
    loops = face.GetLoops
    
    l = -1
    For jj = LBound(loops) To UBound(loops)
        Set loop1 = loops(jj)
        l = ArrayFunctions.AddItem(faceloops, ProcessLoop(loop1), l)
    Next jj
    ArrayFunctions.reverse faceloops
    
    FaceInfo = faceloops

End Function
'Function FaceInfo2(face As SldWorks.Face2, exterior As Variant, interiors As Variant)
'    'Dim faceloops() As Variant
'    Dim loops As Variant
'    Dim jj As Long
'    Dim loop1 As SldWorks.Loop2
'    Dim l As Long
'
'    loops = face.GetLoops
'
'    Set loop1 = loops(UBound(loops))
'    exterior = ProcessLoop(loop1)
'
'    l = -1
'    For jj = (UBound(loops) - 1) To LBound(loops) Step -1
'        Set loop1 = loops(jj)
'        l = ArrayFunctions.AddItem(interiors, ProcessLoop(loop1), l)
'    Next jj
'    'interiors = faceloops
'
'End Function
Function ProcessLoop(loop_in As SldWorks.Loop2) As Variant
        loopedges = ApproxEdges(loop_in)
        loopedges2 = CorrectlyOrderedEdges(loopedges)
        ProcessLoop = CollapseEdges(loopedges2)
End Function




Function CollapseEdges(edgelist As Variant) As Variant
    Dim out() As Variant
    Dim testcases() As Variant
    Dim edge As Variant
    Dim point As Variant
    
    Dim ii As Long
    
    Dim l As Long
    l = -1
    For Each edge In edgelist
        For ii = LBound(edge) To UBound(edge) - 1
            point = edge(ii)
            l = ArrayFunctions.AddItem(out, point, l)
        Next ii
    Next
    
    CollapseEdges = out
End Function

Function CorrectlyOrderedEdges(edgelist As Variant) As Variant
    Dim out() As Variant
    Dim testcases() As Variant
    Dim edge1, edge2 As Variant
    Dim a, b, c, d As Variant
    Dim ii As Long
    Dim l As Long
    Dim m As Long
    
    l = -1
    m = UBound(edgelist) - LBound(edgelist)
    If m > 0 Then
        For ii = LBound(edgelist) To UBound(edgelist) - 1
            edge1 = edgelist(ii)
            edge2 = edgelist(ii + 1)
            a = edge1(LBound(edge1))
            b = edge1(UBound(edge1))
            c = edge2(LBound(edge2))
            d = edge2(UBound(edge2))
            If vectors.ComparePoints(a, c) Then
                reverse edge1
            ElseIf vectors.ComparePoints(a, d) Then
                reverse edge1
                reverse edge2
            ElseIf vectors.ComparePoints(b, c) Then
            ElseIf vectors.ComparePoints(b, d) Then
                reverse edge2
            Else
                Debug.Assert 0
            End If
            l = ArrayFunctions.AddItem(out, edge1, l)
        Next ii
        l = ArrayFunctions.AddItem(out, edge2, l)
        
        CorrectlyOrderedEdges = out
    Else
        CorrectlyOrderedEdges = edgelist
    End If
End Function

Function ApproxEdges(loop1 As SldWorks.Loop2) As Variant
    Dim edges As Variant
    Dim edge As SldWorks.edge
    Dim aedge As Variant
    Dim aedges() As Variant
    Dim ii, kk As Long
    Dim l As Long
    
    edges = loop1.GetEdges
    
    l = -1
    For kk = LBound(edges) To UBound(edges)
        Set edge = edges(kk)
        aedge = ApproximateEdge(edge)
        l = ArrayFunctions.AddItem(aedges, aedge, l)
    Next kk
    
    ApproxEdges = aedges
End Function

Function ApproximateEdge(edge As SldWorks.edge) As Variant
    Dim tesspoints As Variant
    Dim outpoints() As Variant
    Dim curve As SldWorks.curve
    Dim params As Variant
    Dim vStartPt(2) As Double
    Dim vEndPt(2) As Double
    Dim kk As Long
    Dim ii, jj As Long
    Dim l As Long
    Dim p(2) As Double
    
    Set curve = edge.GetCurve
    params = edge.GetCurveParams2
    
    For kk = LBound(vStartPt) To UBound(vStartPt)
        vStartPt(kk) = params(kk)
        vEndPt(kk) = params(kk + 3)
    Next kk
    
    tesspoints = curve.GetTessPts(0#, 0.0001, vStartPt, vEndPt)
    
    l = -1
    For ii = LBound(tesspoints) To UBound(tesspoints) Step 3
        For jj = LBound(p) To UBound(p)
            p(jj) = tesspoints(ii + jj)
        Next jj
        l = ArrayFunctions.AddItem(outpoints, p, l)
    Next ii
    
    ApproximateEdge = outpoints
End Function

Function VertexInfo(loop1 As SldWorks.Loop2) As Variant
    Dim vertices As Variant
    Dim vertex As SldWorks.vertex
    Dim point As Variant
    Dim coord As Variant
    Dim s As String
    Dim scoords() As String
    Dim x, y, z As Double
    Dim l As Long
    Dim kk As Long
    
    vertices = loop1.GetVertices
    
    l = -1
    For kk = LBound(vertices) To UBound(vertices)
        Set vertex = vertices(kk)
        point = vertex.GetPoint
        x = point(0)
        y = point(1)
        z = point(2)
        
        s = "[" & Str(x) & "," & Str(y) & "," & Str(z) & "]"
        'Debug.Print s
        ReDim Preserve scoords(l + 1)
        l = UBound(scoords, 1) - LBound(scoords, 1)
        scoords(l) = s
    Next kk
    
    VertexInfo = scoords
End Function

Function build_loops_string(loops As Variant) As collection
    Dim face_string As New collection
    Dim loopstring As collection
    
    If Not ArrayFunctions.IsVarArrayEmpty(loops) Then
        For Each loop1 In loops
            edgematrix = Matrices.build_from_vectors(loop1)
            Set loopstring = Matrices.toYaml2(edgematrix)
            
            
            stringcollections.PadStrings loopstring, "- ", "  ", ""
            collections.ExtendCollection face_string, loopstring
        Next
        
    End If
    
    
    Set build_loops_string = face_string
End Function

Function build_loop_string(loop1 As Variant) As collection
    edgematrix = Matrices.build_from_vectors(loop1)
    Set build_loop_string = Matrices.toYaml2(edgematrix)
End Function
