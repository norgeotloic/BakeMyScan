import bpy
import os
from . import fn_soft
import tempfile

class remesh_meshlab(bpy.types.Operator):
    bl_idname = "bakemyscan.remesh_meshlab"
    bl_label  = "Remesh with meshlab"
    bl_options = {"REGISTER", "UNDO"}

    facescount = bpy.props.IntProperty( name="facescount", description="Number of faces", default=5000, min=10, max=1000000 )

    @classmethod
    def poll(self, context):
        #meshlabserver must be installed
        if context.user_preferences.addons["BakeMyScan"].preferences.meshlabserver == "":
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
        #self.layout.prop(self, "method", text="Meshlab method")
        self.layout.prop(self, "facescount", text="Number of faces")
        col = self.layout.column(align=True)

    def execute(self, context):
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        obj    = context.active_object
        #maxDim = max( max( obj.dimensions[0], obj.dimensions[1]) , obj.dimensions[2] )

        #Temporary directory
        tmpDir = tempfile.TemporaryDirectory()

        #Create a temporary meshlab script with custom variables
        original_script = os.path.join(os.path.dirname(__file__), os.path.pardir, "scripts_meshlab", "quadricedgecollapse.mlx")
        new_script      = os.path.join(tmpDir.name, "tmp.mlx")
        with open(original_script, 'r') as infile :
            filedata = infile.read()
            newdata  = filedata.replace("FACESCOUNT", str(self.facescount))
            if os.name == "nt":
                newdata = newdata.replace("FILTERNAME", "Simplification: Quadric Edge Collapse Decimation")
            else:
                newdata = newdata.replace("FILTERNAME", "Quadric Edge Collapse Decimation")
            with open(new_script, 'w') as outfile:
                outfile.write(newdata)

        IN  = os.path.join(tmpDir.name, "tmp.obj")
        OUT = os.path.join(tmpDir.name, "tmp.o.obj")
        bpy.ops.export_scene.obj(filepath=IN, use_selection=True)

        #Remesh
        output, error, code = fn_soft.meshlabserver(
            executable  = context.user_preferences.addons["BakeMyScan"].preferences.meshlabserver,
            input_mesh  = IN,
            output_mesh = OUT,
            script_file = new_script,
        )

        #Check the status
        if code != 0:
            self.report({"ERROR"}, "MESHLABSERVER error, look in the console...")
            print("MESHLABSERVER OUTPUT:\n%s\MESHLABSERVER ERROR:\n%s" % (output, error))
            return{"CANCELLED"}
        else:
            #Get the old objects
            old = [o for o in bpy.data.objects]
            #Reimport
            bpy.ops.import_scene.obj(filepath=OUT)
            #Make active
            obj = [o for o in bpy.data.objects if o not in old][0]
            bpy.ops.object.select_all(action='DESELECT')
            obj.select=True
            bpy.context.scene.objects.active = obj
            self.report({"INFO"}, "MESHLABSERVER success")
            return{'FINISHED'}

def register() :
    bpy.utils.register_class(remesh_meshlab)

def unregister() :
    bpy.utils.unregister_class(remesh_meshlab)
