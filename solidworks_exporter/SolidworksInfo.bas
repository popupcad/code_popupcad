Attribute VB_Name = "SolidworksInfo"
Function getview(model As SldWorks.ModelDoc2, view As SldWorks.view)
    Dim swApp As SldWorks.SldWorks
    'Dim model As SldWorks.ModelDoc2
    Dim drawing As SldWorks.DrawingDoc
    'Dim view As SldWorks.view
    
    Set swApp = Application.SldWorks
    Set model = swApp.ActiveDoc
    
    If model.GetType <> swDocDRAWING Then
        MsgBox ("Please Open a Drawing")
        End
    End If
    
    Set drawing = model
    Set view = drawing.ActiveDrawingView
    
    If view Is Nothing Then
        MsgBox ("Please Select a View")
        End
    End If
    'Set getview = view
End Function

Function get_visible_faces(view As SldWorks.view, visible_faces As Collection)
    Dim comp As SldWorks.Component2
    Dim faces As Variant
    Dim face As SldWorks.Face2
    Dim body As Body2
    Set comp = Nothing
    
    Debug.Assert Not view Is Nothing
    'Debug.Print "Name of drawing view: "; view.Name
    
    faces = view.GetVisibleEntities(comp, swViewEntityType_Face)
    'Debug.Print "There are a total of " & UBound(faces) + 1 & " visible faces in this view."
    
    collections.ExtendCollectionFromArray visible_faces, faces
    
End Function

Function get_referenced_doc(view As SldWorks.view) As SldWorks.ModelDoc2

    Dim ref_doc As SldWorks.ModelDoc2
    Dim ref_conf As SldWorks.Configuration
    Dim swRootComp As SldWorks.component
    Dim comp As SldWorks.Component2
    Dim faceexport As New Collection
    Set ref_doc = view.ReferencedDocument
    
    
    Set get_referenced_doc = ref_doc
    
End Function

Sub build_component_info(ref_doc As SldWorks.ModelDoc2, component_info As Collection)
    Dim components As New Collection
    Dim vComponents As Variant
    Dim comp As Component2
    Dim vBodies As Variant
    Dim vBodyInfo As Variant
    Dim errors As Long, warnings As Long
    Dim i As Long, j As Long
    
    Dim ref_conf As SldWorks.Configuration
    Dim rootcomponent As SldWorks.component
    
    Dim mathTransform As SldWorks.mathTransform
    Dim arrayTransform As Variant
    
    Dim ci As Collection
    
    Set ref_conf = ref_doc.GetActiveConfiguration
    Set rootcomponent = ref_conf.GetRootComponent
    
    If ref_doc.GetType = swDocPART Then
        Set ci = part_comp_info(ref_doc)
        addkeyed component_info, ci
    End If
    
    If ref_doc.GetType = swDocASSEMBLY Then
        buildcomponentlist_rec components, rootcomponent
        
        For Each comp In components
            Set ci = assembly_comp_info(comp)
            addkeyed component_info, ci
        Next comp
    End If
    

End Sub

Sub buildcomponentlist_rec(componentlist As Collection, component As Component2)
    Dim children As Variant
    children = component.GetChildren
    
    For i = LBound(children) To UBound(children)
        Dim child As SldWorks.Component2
        Set child = children(i)
        componentlist.Add child
        buildcomponentlist_rec componentlist, child
    Next
End Sub

Function part_comp_info(comp As SldWorks.PartDoc) As Collection
    Dim info As New Collection

'   ---------
    info.Add comp, "component"
    info.Add "component", "type"
'   ---------
    info.Add UniqueID, "id"
'   ---------
    info.Add (comp.Visible = swComponentVisibilityState_e.swComponentVisible), "isVisible"
'   ---------
    
    Dim bodies As New Collection
    Dim vBodies As Variant
    Dim vBodyInfo As Variant
    Dim body As SldWorks.Body2
    Dim bi As Collection

    vBodies = comp.GetBodies2(SwConst.swBodyType_e.swSolidBody, False)
    For j = 0 To UBound(vBodies)
        Set body = vBodies(j)
        Set bi = BodyInfo(body, info)
        addkeyed bodies, bi
    Next
    info.Add bodies, "bodies"
'   ---------
    Dim mathTransform As SldWorks.mathTransform
    Dim arrayTransform As Variant

    arrayTransform = Matrices.Eye(4)
    
    info.Add arrayTransform, "transform"
'   ---------
        Dim transformstring As New Collection
        Set transformstring = Matrices.toString(arrayTransform)
        stringcollections.PadStrings transformstring, "- [", "- [", "]"
        info.Add transformstring, "transform_s"
'   ---------
    Set part_comp_info = info

End Function

Function assembly_comp_info(comp As SldWorks.Component2) As Collection
    Dim info As New Collection
'   ---------
    info.Add comp, "component"
    info.Add "component", "type"
'   ---------
    info.Add UniqueID, "id"
'   ---------
    info.Add (comp.Visible = swComponentVisibilityState_e.swComponentVisible), "isVisible"
'   ---------
    Dim bodies As New Collection
    Dim vBodies As Variant
    Dim vBodyInfo As Variant
    Dim body As SldWorks.Body2
    Dim bi As Collection

    vBodies = comp.GetBodies3(SwConst.swBodyType_e.swSolidBody, vBodyInfo)
    For j = 0 To UBound(vBodies)
        Set body = vBodies(j)
        Set bi = BodyInfo(body, info)
        addkeyed bodies, bi
    Next
    info.Add bodies, "bodies"
'   ---------
    Dim mathTransform As SldWorks.mathTransform
    Dim arrayTransform As Variant

    Set mathTransform = comp.Transform2
    If Not mathTransform Is Nothing Then
        arrayTransform = Matrices.buildFromMathTransform(mathTransform)
    Else
        arrayTransform = Matrices.Eye(4)
    End If
    
    info.Add arrayTransform, "transform"
'   ---------
        Dim transformstring As New Collection
        Set transformstring = Matrices.toString(arrayTransform)
        stringcollections.PadStrings transformstring, "- [", "- [", "]"
        info.Add transformstring, "transform_s"
'   ---------
    Set assembly_comp_info = info

End Function

Function BodyInfo(body As SldWorks.Body2, parent As Collection) As Collection
    Dim info As New Collection
    info.Add body, "body"
    info.Add "body", "type"
'   ---------
    info.Add UniqueID, "id"
'   ---------
    info.Add body.Visible, "isVisible"
'   ---------
    info.Add parent, "parent"
'   ---------
    Dim FaceArray As Variant
    Dim faces As New Collection
    Dim face As SldWorks.Face2
    Dim fi As Collection
    
    FaceArray = body.getfaces()

    Dim ii As Integer
    For ii = LBound(FaceArray) To UBound(FaceArray)
        Set face = FaceArray(ii)
        Set fi = FaceInfoDict(face, info)
        addkeyed faces, fi
    Next ii
    info.Add faces, "faces"
'   ---------
    Set BodyInfo = info
End Function

Function FaceInfoDict(face As SldWorks.Face2, parent As Collection) As Collection
    Dim info As New Collection
    info.Add face, "face"
    info.Add "face", "type"
'   ---------
    info.Add UniqueID, "id"
'   ---------
    info.Add parent, "parent"
'   ---------
    'Dim face_data As Variant
    'face_data =
    'Dim exterior, interiors(), loops() As Variant
    'FaceInfo.FaceInfo2 face, exterior, interiors
    'info.Add exterior, "exterior"
    'info.Add interiors, "interiors"
    'info.Add build_loop_string(info.item("exterior")), "exterior_s"
    'info.Add build_loops_string(info.item("interiors")), "interiors_s"
'   ---------
    loops = FaceInfo.FaceInfo(face)
    info.Add loops, "loops"
    info.Add build_loops_string(info.item("loops")), "output"
'   ---------
    info.Add False, "isVisible"
'   ---------
    Set FaceInfoDict = info
End Function

Function MarkVisibleFaces(component_info As Collection, visible_faces As Collection)
    Dim component, bodies, body_info, faces, face_info As Collection
    Dim ii As Integer
    ii = 0
    For Each component In component_info
        For Each body_info In component.item("bodies")
            For Each face_info In body_info.item("faces")
                Dim f As SldWorks.Face2
                Set f = face_info.item("face")
                ii = face_index(visible_faces, f)
                    If ii >= 0 Then
                        face_info.Remove "isVisible"
                        face_info.Add True, "isVisible"
                    End If
            Next face_info
        Next body_info
    Next component
End Function

Function GenFaceOutput(outputstring As Collection, component_info As Collection)
    Dim component, bodies, body_info, faces, face_info As Collection
    For Each component In component_info
        For Each body_info In component.item("bodies")
            For Each face_info In body_info.item("faces")
                If face_info.item("isVisible") Then
                    'Debug.Print face_info.item("id")
                    collections.ExtendCollection outputstring, face_info.item("output")
                End If
            Next face_info
        Next body_info
    Next component
End Function



