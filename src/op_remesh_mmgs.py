import bpy
import os
import tempfile
from . import fn_soft

class remesh_mmgs(bpy.types.Operator):
    bl_idname = "bakemyscan.remesh_mmgs"
    bl_label  = "Remesh with mmgs"
    bl_options = {"REGISTER", "UNDO"}

    hausd  = bpy.props.FloatProperty( name="hausd", description="Haussdorf distance as a ratio", default=0.01, min=0.0001, max=1)
    smooth = bpy.props.BoolProperty(  name="smooth", description="Smooth surface", default=True)

    @classmethod
    def poll(self, context):
        #mmgs must be installed
        if context.user_preferences.addons["BakeMyScan"].preferences.mmgs == "":
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
        tmpDir = tempfile.TemporaryDirectory()
        IN  = os.path.join(tmpDir.name, "tmp.mesh")
        OUT = os.path.join(tmpDir.name, "tmp.o.mesh")
        bpy.ops.bakemyscan.export_mesh(filepath=IN)

        #Remesh
        exe = context.user_preferences.addons["BakeMyScan"].preferences.mmgs
        output, error, code = fn_soft.mmgs(
            executable  = exe,
            input_mesh  = IN,
            output_mesh = OUT,
            hausd       = self.hausd * maxDim,
            nr          = True if self.smooth else False
        )

        #Check the status
        if code != 0:
            self.report({"ERROR"}, "MMGS error, look in the console...")
            print("MMGS OUTPUT:\n%s\nMMGS ERROR:\n%s" % (output, error))
            return{"CANCELLED"}
        else:
            #Reimport
            bpy.ops.bakemyscan.import_mesh(filepath=OUT)
            self.report({"INFO"}, "MMGS success")
            return{'FINISHED'}

def register() :
    bpy.utils.register_class(remesh_mmgs)

def unregister() :
    bpy.utils.unregister_class(remesh_mmgs)
