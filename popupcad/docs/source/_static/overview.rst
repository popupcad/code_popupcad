===============
Software Layout
===============

------
Editor
------

.. image:: overview_images/editor_screenshot.*
   :scale: 50%
   :align: center
The editor is the center of interaction for a popupCAD design.  The editor provides several functions:

^^^^^^^^^^^^^^^^^^^^^^^^
View and Edit Operations
^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: overview_images/operation_list.*
   :scale: 100%
   :align: center
The editor provides access to the operations list, a listing of all operations applied in the design.  Selecting an item in the list shows the output geometry associated with the operation in the 2d and 3d view to the right.  Double clicking on an item in the list gives users the ability to edit that particular operation using its edit dialog.  The delete button removes the operation and its associated geometry from the design.

^^^^^^^^^^^^^^^^^^^^^^^^
View Layers
^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: overview_images/layer_list.*
   :scale: 100%
   :align: center
The editor's layer list gives users the ability to turn on or off layers in the 2d and 3d view.  This is useful for viewing the geometry of a single layer for error-proofing, or for understanding how the materials on multiple layers interact.  Clicking a layer shows or hides it in the 2d and 3d views.

^^^^^^^^^^^^^^^^^^^^^^^^
2D View
^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: overview_images/2d_view.*
   :scale: 50%
   :align: center
The 2d view of a design shows the currently-selected operation in the operation list, according to the selected layers in the layer list.  This is simply a view of the geometry, and interaction is generally restricted in the editor.  

^^^^^^^^^^^^^^^^^^^^^^^^
3D View
^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: overview_images/3d_view.*
   :scale: 50%
   :align: center
Like the 2d view, the 3d view allows users to view the geometric output of a particular operation.  The 3d view gives users the ability to pan and rotate the view to enable a closer inspection of each layer's geometry.  In addition, a slider bar to the right allows users to explode the layer view, allowing each layer to be seen on its own.

^^^^^^^^^^^^^^^^^^^^^^^^
File management
^^^^^^^^^^^^^^^^^^^^^^^^

Common file operations, such as "open", "save", and "save as" allow a user to load or save design files.   Design files, with the extension ".cad", are saved as human-readable YAML files.  The structure of a design file is discussed in a following section

^^^^^^^^^^^^^^^^^^^^^^^^
Project Management
^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: overview_images/project_management.*
   :scale: 100%
   :align: center

The editor also allows users to interact with project-level settings.  

.. image:: overview_images/edit_layer_order.*
   :scale: 100%
   :align: center
 
The "edit layer order" feature, for example, allows users to insert or remove layers from the listing of laminates in the design.  This affects which layers are available for geometric operations across all operations in the design, and should match the user's anticipated requirements for the number of layers in the physical device.  This setting should be changed at the beginning of the design process in order to allow individual operations to use the correct layers, in the right order.

.. image:: overview_images/edit_layer_properties.*
   :scale: 100%
   :align: center
 
The "edit laminate values" option allows users to edit the attributes of each layer, such as the color and thickness of the constituent layers.  Some materials, depending on the material type, may have attributes such as stiffness, poisson's ratio, etc, which can be displayed for that particular material type.  Currently, only color and thickness values are available.

^^^^^^^^^^^^^^^^^^^^^^^^
Ops Menu
^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: overview_images/ops_menu.*
   :scale: 100%
   :align: center
   
The Ops Menu, also visible as a toolbar, is the main mode of creating designs in the editor.  It lists a variety of operations which are available to the user.  These operations are typically geometric and allow the user to define or combine one or more geometries together across or between layers.  When selected, each operation typically spawns a dialog window specific to that class of operation, allowing the user to specify certain details of the operation.  Operations are described in detail in subsequent sections.  
There are several different types of operation available.  The elementary operations include "Dilate/Erode", "Laminate Op", "Layer Op", and "Shift/Flip".  These operations perform the basic geometric and layer operations required by more complicated operations, but are also useful to users by themselves.
PopupCAD is intended to be an object-oriented approach to creating laminate devices.  Therefore it is important to provide users with the ability to reuse geometry from design librarires in a variety of ways.  The second grouping of operations, "locate op" and "place op", allow users to specify the geometry important for the reuse of popupCAD designs in other designs.  Because geometry from one design can be embedded in another, the "locate op" allows users to create a location reference line to all the design's geometry.  When the user desires to reuse the design, the "place op" gives the user the ability to draw one or more lines, signifying the placement of the referenced design in the new design.  The relative length and scale of the locate and placement lines, along with the option to place, stretch, or scale the referenced geometry, gives users full control over the way in which referenced geometry gets transformed in the new design.

.. image:: overview_images/ops_toolbar.*
   :scale: 50%
   :align: center

^^^^^^^^^^^^^^^^^^^^^^^^
Other Menus
^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: overview_images/view_operations.*
   :scale: 100%
   :align: center

Other menus exist in popupCAD, but are sparsely populated.  The manufacturability window gives users access to a graphical view of the operation list, which allows users to view how various operations are related to each other

.. image:: overview_images/operation_network.*
   :scale: 50%
   :align: center
 
The Scripts menu populates itself with all scripts located in the popupcad/scripts/ subdirectory.  It functions as an easy way for users to create their own scripts and have it be accessible to them through the gui without delving too deep into the popupCAD codebase.  Only one example script is provided as a template for future plugin development .
Finally, the window menu allows users to show or hide various sub-windows in the editor.

--------
Sketcher
--------

.. image:: overview_images/sketcher_screenshot.*
   :scale: 50%
   :align: center
 
The sketcher is the second most important window in popupCAD, because it allows users to generate original geometry directly in the popupCAD environment.  The sketcher has many capabilities, mostly centered around creating and defining geometries.
The sketcher is usually accessed through operations which require the user to create geometry, such as the sketch operation, locate operation, and place operation.  It has a variety of sub-windows which allow the user easy access to underlying data, but the most important sub-window is the graphical sketching window, located in the center of the screen.  In this window, the user is able to create a variety of geometries, including circles, squares, polygons, lines, and polylines.
Creating new geometry begins by selecting the geometry type from the toolbar above.  Clicking in the drawing window then adds a vertex under the mouse pointer, defining the first point in the geometry.  Further clicks of the mouse define subsequent points, and double-clicking the mouse ends the definition process.  Some geometries only allow adding two points total, such as lines and circles.  Editing of geometries is allowed; by double-clicking on an object the vertices become visible, allowing them to be dragged to new positions.  Clicking inside the polygon while in edit mode with the ctrl key pressed adds a new vertex, and clicking on a vertex with the ctrl+shift  keys pressed deletes that vertex.

^^^^^^^^^^^
Constraints
^^^^^^^^^^^

A variety of constraints can be added to points or line segments, allowing them to be further defined.  Constraint mode is enabled by selecting "constraints on" which toggles all active vertices and line segments.  Clicking on one or more points or line segments with the ctrl key pressed allows the user to select multiple objects.  By clicking on the desired constraint, the constraint becomes added to the constraint list on the left.
Some constraints are value constraints, such as the "distance", point/line, "distance x" and "distance y" constraints.  If selected, a dialog box opens allowing the user to specify the desired constraint value.  Double clicking on the constraint in the constraint list also enables the user to edit the value later.
Constraints are not continually evaluated, and if the user drags or moves an object or vertex, they must refresh the constraints manually.  This is accomplished by the "refresh constraints" button, which reevaluates all constraints which have been added to the sketch.
Sketches can operate on previous geometry in a variety of ways.  They can be combined in the editor through a variety of laminate and layer operations, or they may operate directly on previous operations in the sketcher itself.  This is made possible by selecting a previous parent in the left dropbox, and by selecting the type of operation the sketcher is performing.  For example, in the example below, a user has chosen to merge the previous geometry (named Body(placement op), and colored reddish) with a new polygon they have drawn(in yellow).  By selecting "union" the two sets of polygons will merge as seen below.  The "union", "intersect", and "difference" operations are all available, each producing different output geometry.
The layer window seen in the sketcher does not serve to alter which layers are visible in the sketch.  In this case, it is used to designate how sketch geometry is copied to each layer in the laminate.  If all layers are selected, for example, they each get an instance of the resulting sketch operation in each layer.  If only one is selected, the resulting operation will only be applied to the one layer, giving the user a high level of control in combining geometric operations.

.. image:: overview_images/sketch_operation.*
   :scale: 50%
   :align: center
.. image:: overview_images/sketch_op_result.*
   :scale: 50%
   :align: center
   
^^^^^^^^^^^
Operations
^^^^^^^^^^^

For a more detailed discussion of the basic operations available in popupCAD, please see:

Aukes, D.M, Goldberg, B., Cutkosky, M.R., and Wood, R.J., "An Analytic Framework for Developing Inherently-Manufacturable Pop-up Laminate Devices".

* Dilate / Erode: grow or shrink laminate geometry by a certain radius.  Applied to all layers in the laminate
* Layer op: combines one or more layer geometries with a union/intersection/difference operation, and outputs the geometry to the specified layer
* Laminate Op: Combines one or more previous operations with a union/intersection/difference operation.
* Shift / Flip: Moves all layers up or down, and /or flips their order
------------
Dependencies
------------

.. image:: overview_images/dependencies.*
   :scale: 50%
   :align: center
