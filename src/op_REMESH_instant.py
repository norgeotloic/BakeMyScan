import bpy
import os
import tempfile
from . import fn_soft

class remesh_instant(bpy.types.Operator):
    bl_idname = "bakemyscan.remesh_instant"
    bl_label  = "Remesh with Instant Meshes"
    bl_options = {"REGISTER", "UNDO"}

    interactive = bpy.props.BoolProperty(  name="interactive", description="Interactive", default=False)
    method      = bpy.props.EnumProperty(items= ( ('faces', 'Number of faces', 'Number of faces'), ("verts", "Number of verts", "Number of verts"), ("edges", "Edge length", "Edge length")) , name="Remesh according to", description="Remesh according to", default="faces")
    facescount  = bpy.props.IntProperty(   name="facescount",  description="Number of faces", default=5000, min=10, max=10000000 )
    vertscount  = bpy.props.IntProperty(   name="vertscount",  description="Number of verts", default=5000, min=10, max=10000000 )
    edgelength  = bpy.props.FloatProperty( name="edgelength",  description="Edge length (ratio)", default=0.05, min=0.001, max=1 )

    d = bpy.props.BoolProperty( name="d", description="Deterministic (slower)", default=False)
    D = bpy.props.BoolProperty( name="D", description="Tris/quads dominant instead of pure", default=False)
    i = bpy.props.BoolProperty( name="i", description="Intrinsic mode", default=False)
    b = bpy.props.BoolProperty( name="b", description="Align to boundaries", default=False)
    C = bpy.props.BoolProperty( name="C", description="Compatibility mode", default=False)

    c = bpy.props.FloatProperty( name="c",  description="Creases angle threshold", default=30, min=0, max=180 )
    S = bpy.props.IntProperty(   name="S",  description="Smoothing reprojection steps", default=2, min=0, max=100 )
    r = bpy.props.EnumProperty(items= ( ('r0', 'none', 'none'), ("2", "2", "2"), ("4", "4", "4"), ("6", "6", "6")) , name="r", description="Orientation symmetry type", default="r0")
    p = bpy.props.EnumProperty(items= ( ('p0', 'none', 'none'), ("4", "4", "4"), ("6", "6", "6")) , name="r", description="Position symmetry type", default="p0")

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
        if context.mode!="OBJECT" and context.mode!="SCULPT":
            return 0
        return 1

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        box = self.layout.box()
        box.label('Basic options')
        box.prop(self, "interactive", text="Open the GUI")
        box.prop(self, "method", text="Remesh according to")
        box.prop(self, "facescount",  text="Desired number of faces")
        box.prop(self, "facescount",  text="Desired number of vertices")
        box.prop(self, "edgelength",  text="Desired edge length (ratio)")

        box = self.layout.box()
        box.label('Advanced options')
        box.prop(self, "d", text="Deterministic (slower)")
        box.prop(self, "D", text="Tris/quads dominant instead of pure")
        box.prop(self, "i", text="Intrinsic mode")
        box.prop(self, "b", text="Align to boundaries")
        box.prop(self, "C", text="Compatibility mode")
        box.prop(self, "c", text="Creases angle threshold")
        box.prop(self, "S", text="Smoothing reprojection steps")
        box.prop(self, "r", text="Orientation symmetry type")
        box.prop(self, "p", text="Position symmetry type")
        col = self.layout.column(align=True)

    def execute(self, context):
        #Go into object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        obj    = context.active_object
        maxDim = max( max( obj.dimensions[0], obj.dimensions[1]) , obj.dimensions[2] )

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
                face_count   = self.facescount if self.method=="faces" else None,
                vertex_count = self.vertscount if self.method=="verts" else None,
                edge_length  = self.edgelength*maxdim if self.method=="edges" else None,
                d = self.d,
                D = self.D,
                i = self.i,
                b = self.b,
                C = self.C,
                c = self.c,
                S = self.S,
                p = self.p if self.p!="p0" else None,
                r = self.r if self.r!="r0" else None
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
            obj.select = False
            bpy.ops.import_scene.obj(filepath=OUT)
            for o in context.selected_objects:
                o.select=True
                bpy.context.scene.objects.active = o

            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.mark_sharp(clear=True)
            bpy.ops.object.editmode_toggle()

            self.report({"INFO"}, "INSTANTMESHES success")
            return{'FINISHED'}

def register() :
    bpy.utils.register_class(remesh_instant)

def unregister() :
    bpy.utils.unregister_class(remesh_instant)
