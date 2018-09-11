import bpy
import os
from bpy_extras.io_utils import ImportHelper

from . import fn_soft

class remesh_mmgs(bpy.types.Operator):
    bl_idname = "bakemyscan.remesh_mmgs"
    bl_label  = "Remesh with mmgs"
    bl_options = {"REGISTER", "UNDO"}

    hausd  = bpy.props.FloatProperty( name="hausd", description="Haussdorf distance as a ratio", default=0.01, min=0.0001, max=1)
    smooth = bpy.props.BoolProperty( name="smooth", description="Smooth surface", default=True)

    @classmethod
    def poll(self, context):
        #mmgs must be installed
        if fn_soft.mmgsExe is None:
            return 0
        #If more than two objects are selected
        if len(context.selected_objects)!=1 or context.active_object is None:
            return 0
        #If something other than a MESH is selected
        for o in context.selected_objects:
            if o.type != "MESH":
                return 0
        if context.mode!="OBJECT":
            return 0
        return 1

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "hausd",  text="Haussdorf ratio")
        self.layout.prop(self, "smooth", text="Smooth surface")
        col = self.layout.column(align=True)

    def execute(self, context):
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        obj    = context.active_object
        maxDim = max( max( obj.dimensions[0], obj.dimensions[1]) , obj.dimensions[2] )

        #Export
        bpy.ops.bakemyscan.export_mesh(filepath="tmp.mesh")

        #Remesh
        cmd = fn_soft.mmgsExe + "tmp.mesh -o tmp.o.mesh -hausd " + str( float(self.hausd * maxDim) )
        if self.smooth:
            cmd+=" -nr"
        err = fn_soft.execute(cmd)

        #Clean and import
        if not err:
            bpy.ops.bakemyscan.import_mesh(filepath="tmp.o.mesh")
        else:
            self.report({'INFO'}, "MMGS failure")
        for f in ["tmp.mesh", "tmp.o.mesh", "tmp.sol", "tmp.o.sol"]:
            if os.path.exists(f):
                os.remove(f)

        return{'FINISHED'}

def register() :
    bpy.utils.register_class(remesh_mmgs)

def unregister() :
    bpy.utils.unregister_class(remesh_mmgs)
