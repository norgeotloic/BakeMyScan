import bpy
import os
from . import fn_soft
import tempfile

class remesh_quadriflow(bpy.types.Operator):
    bl_idname = "bakemyscan.remesh_quadriflow"
    bl_label  = "Remesh with Quadriflow"
    bl_options = {"REGISTER", "UNDO"}

    resolution = bpy.props.IntProperty( name="resolution", description="Resolution", default=1000, min=10, max=100000 )
    #smooth = bpy.props.BoolProperty(  name="smooth", description="Smooth surface", default=True)

    @classmethod
    def poll(self, context):
        if context.user_preferences.addons["BakeMyScan"].preferences.quadriflow == "":
            return 0
        if len(context.selected_objects)!=1 or context.active_object is None:
            return 0
        for o in context.selected_objects:
            if o.type != "MESH":
                return 0
        if context.mode!="OBJECT" and context.mode!="SCULPT":
            return 0
        return 1

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "resolution", text="Number of faces")
        col = self.layout.column(align=True)

    def execute(self, context):
        #Go into object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        obj    = context.active_object

        #Export
        tmpDir = tempfile.TemporaryDirectory()
        IN  = os.path.join(tmpDir.name, "tmp.obj")
        OUT = os.path.join(tmpDir.name, "tmp.o.obj")
        bpy.ops.export_scene.obj(filepath=IN, use_selection=True)

        #Remesh
        output, error, code = fn_soft.quadriflow(
            executable  = context.user_preferences.addons["BakeMyScan"].preferences.quadriflow,
            input_mesh  = IN,
            output_mesh = OUT,
            face_count = self.resolution,
        )

        #Check the status
        if code != 0:
            self.report({"ERROR"}, "QUADRIFLOW error, look in the console...")
            print("QUADRIFLOW OUTPUT:\n%s\QUADRIFLOW ERROR:\n%s" % (output, error))
            return{"CANCELLED"}
        else:
            #Reimport
            bpy.ops.import_scene.obj(filepath=OUT)
            bpy.context.scene.objects.active = context.selected_objects[0]
            bpy.ops.object.shade_smooth()
            self.report({"INFO"}, "QUADRIFLOW success")
            return{'FINISHED'}

def register() :
    bpy.utils.register_class(remesh_quadriflow)

def unregister() :
    bpy.utils.unregister_class(remesh_quadriflow)
