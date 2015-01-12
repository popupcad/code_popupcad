Attribute VB_Name = "main"
Option Explicit

Sub main()
    Dim swApp As SldWorks.SldWorks
    Set swApp = Application.SldWorks
    
    Dim model As SldWorks.ModelDoc2
    Dim view As SldWorks.view
    Dim visible_faces As New Collection
    Dim ref_doc As SldWorks.ModelDoc2
    
    Dim component_info As New Collection
   
    Dim strings As Collection
    Dim transform As mathTransform
    
    SolidworksInfo.getview model, view
    Set ref_doc = SolidworksInfo.get_referenced_doc(view)

    SolidworksInfo.build_component_info ref_doc, component_info
    SolidworksInfo.get_visible_faces view, visible_faces
    SolidworksInfo.MarkVisibleFaces component_info, visible_faces
    
    Set transform = view.ModelToViewTransform
    Set strings = BuildExportData3(transform, component_info)
    'Dim filename As String
    'filename = "C:\Users\danb0b\Desktop\" & model.GetTitle & "_" & view.Name & ".yaml"
    Dim filename2 As String
    filename2 = swApp.GetCurrentWorkingDirectory() & model.GetTitle & "_" & view.Name & ".yaml"
    stringcollections.WriteFile strings, filename2
    Debug.Print "Done"
End Sub

Function BuildExportData(viewTransform As SldWorks.mathTransform, component_info As Collection) As Collection
    Dim lines As New Collection
    Dim transform As Variant
    Dim transformstring As New Collection
    
    lines.Add "!!python/object:popupcad.filetypes.solidworksimport.SolidworksImport"
    lines.Add "transform:"

    transform = Matrices.buildFromMathTransform(viewTransform)
    Set transformstring = Matrices.toString(transform)
    stringcollections.PadStrings transformstring, "- [", "- [", "]"
    collections.ExtendCollection lines, transformstring
    
    lines.Add "geoms:"
    Dim geomstring As New Collection
    SolidworksInfo.GenFaceOutput lines, component_info
    
    Set BuildExportData = lines
End Function


Function BuildExportData2(viewTransform As SldWorks.mathTransform, component_info As Collection) As Collection
    Dim lines As New Collection
    Dim transform As Variant
    Dim transformstring As New Collection
    
    lines.Add "!!python/object:popupcad.filetypes.solidworksimport.SolidworksImport"
    lines.Add "transform:"

    transform = Matrices.buildFromMathTransform(viewTransform)
    Set transformstring = Matrices.toString(transform)
    stringcollections.PadStrings transformstring, "- [", "- [", "]"
    collections.ExtendCollection lines, transformstring
    
    lines.Add "geoms:"
    Dim geomstring As New Collection
    
    Dim component, bodies, body_info, faces, face_info As Collection
    For Each component In component_info
        For Each body_info In component.item("bodies")
            For Each face_info In body_info.item("faces")
                If face_info.item("isVisible") Then
                    collections.ExtendCollection lines, face_info.item("output")
                End If
            Next face_info
        Next body_info
    Next component
    
    Set BuildExportData2 = lines
End Function

Function BuildExportData3(viewTransform As SldWorks.mathTransform, components As Collection) As Collection
    Dim lines As New Collection
    Dim transform As Variant
    Dim transformstring As New Collection
    Dim componentstring As New Collection
    Dim facestring As New Collection
    
    lines.Add "!!python/object:popupcad.filetypes.solidworksimport.Assembly"
    lines.Add "transform:"

    transform = Matrices.buildFromMathTransform(viewTransform)
    Set transformstring = Matrices.toString(transform)
    stringcollections.PadStrings transformstring, "- [", "- [", "]"
    collections.ExtendCollection lines, transformstring
    
    lines.Add "components:"
    Dim geomstring As New Collection
    
    Dim component_info, bodies, body_info, faces, face_info As Collection
    For Each component_info In components
        If component_info.item("isVisible") Then
'        If True Then
            Set componentstring = New Collection
            componentstring.Add "!!python/object:popupcad.filetypes.solidworksimport.Component"
            componentstring.Add "transform:"
            Set transformstring = component_info.item("transform_s")
            collections.ExtendCollection componentstring, transformstring
            
            componentstring.Add "faces:"
            For Each body_info In component_info.item("bodies")
                If body_info.item("isVisible") Then
'                If True Then
                    For Each face_info In body_info.item("faces")
                        If face_info.item("isVisible") Then
                            Set facestring = New Collection
                            facestring.Add "!!python/object:popupcad.filetypes.solidworksimport.Face"
                            'facestring.Add "exterior:"
                            'collections.ExtendCollection facestring, face_info.item("exterior_s")
                            'If Not ArrayFunctions.IsVarArrayEmpty(face_info.item("output")) Then
                            facestring.Add "loops:"
                            collections.ExtendCollection facestring, face_info.item("output")
                            'Else
                            '    facestring.Add "interiors: []"
                            'End If
                            stringcollections.PadStrings facestring, "- ", "  ", ""
                            collections.ExtendCollection componentstring, facestring
                        End If
                    Next face_info
                End If
            Next body_info
            
            stringcollections.PadStrings componentstring, "- ", "  ", ""
            collections.ExtendCollection lines, componentstring
        End If
    Next component_info
    
    Set BuildExportData3 = lines
End Function

