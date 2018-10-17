import bpy
import os
import tempfile
from . import fn_soft

class remesh_instant(bpy.types.Operator):
    bl_idname = "bakemyscan.remesh_instant"
    bl_label  = "Remesh with Instant Meshes"
    bl_options = {"REGISTER", "UNDO"}

    facescount  = bpy.props.IntProperty(  name="facescount",  description="Number of faces", default=5000, min=10, max=1000000 )
    interactive = bpy.props.BoolProperty( name="interactive", description="Interactive", default=False)

    @classmethod
    def poll(self, context):
        #Instant meshes must be installed
        if context.user_preferences.addons["BakeMyScan"].preferences.instant == "":
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
        self.layout.prop(self, "facescount",  text="Number of faces")
        self.layout.prop(self, "interactive", text="Interactive")
        col = self.layout.column(align=True)

    def execute(self, context):
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        obj    = context.active_object
        #maxDim = max( max( obj.dimensions[0], obj.dimensions[1]) , obj.dimensions[2] )

        #Export
        #Export
        tmpDir = tempfile.TemporaryDirectory()
        IN  = os.path.join(tmpDir.name, "tmp.obj")
        OUT = os.path.join(tmpDir.name, "tmp.o.obj")
        bpy.ops.export_scene.obj(filepath=IN, use_selection=True)

        #Remesh
        if self.interactive:
            output, error, code = fn_soft.instant_meshes_gui(
                executable  = context.user_preferences.addons["BakeMyScan"].preferences.instant,
                input_mesh  = IN,
            )
        else:
            output, error, code = fn_soft.instant_meshes_cmd(
                executable  = context.user_preferences.addons["BakeMyScan"].preferences.instant,
                input_mesh  = IN,
                output_mesh = OUT,
                face_count = self.facescount,
            )

        #Get the mesh the user saved
        if self.interactive:
            for l in output.split("\n"):
                if "Writing" in l:
                    OUT = l.split('"')[1]

        #Check the status
        if code != 0 and "tmp.o.obj" in OUT:
            self.report({"ERROR"}, "INSTANTMESHES error, look in the console...")
            print("INSTANTMESHES OUTPUT:\n%s\INSTANTMESHES ERROR:\n%s" % (output, error))
            return{"CANCELLED"}
        else:
            #Reimport
            bpy.ops.import_scene.obj(filepath=OUT)
            self.report({"INFO"}, "INSTANTMESHES success")
            return{'FINISHED'}

def register() :
    bpy.utils.register_class(remesh_instant)

def unregister() :
    bpy.utils.unregister_class(remesh_instant)
