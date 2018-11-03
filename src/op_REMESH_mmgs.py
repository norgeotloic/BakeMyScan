import bpy
import os
import tempfile
from . import fn_soft

class remesh_mmgs(bpy.types.Operator):
    bl_idname = "bakemyscan.remesh_mmgs"
    bl_label  = "Remesh with mmgs"
    bl_options = {"REGISTER", "UNDO"}

    #Basic options
    smooth = bpy.props.BoolProperty(  name="smooth", description="Ignore angle detection (smooth)", default=True)
    hausd  = bpy.props.FloatProperty( name="hausd", description="Haussdorf distance (ratio)", default=0.01, min=0.0001, max=1)
    #Advanced options
    angle  = bpy.props.FloatProperty( name="hausd",  description="Angle detection (°)", default=30, min=0.01, max=180.)
    hmin   = bpy.props.FloatProperty( name="hmin",   description="Minimal edge size (ratio)", default=0.01, min=0.0001, max=1)
    hmax   = bpy.props.FloatProperty( name="hmax",   description="Maximal edge size (ratio)", default=1, min=0.0001, max=5)
    hgrad  = bpy.props.FloatProperty( name="hgrad",  description="Gradation parameter", default=1.3, min=1., max=5.)
    aniso  = bpy.props.BoolProperty(  name="aniso",  description="Enable anisotropy", default=False)
    nreg   = bpy.props.BoolProperty(  name="nreg",   description="Normal regulation", default=False)

    advanced = bpy.props.BoolProperty(  name="advanced", description="advanced properties", default=False)
    weight   = bpy.props.BoolProperty(  name="weight", description="weight as edge length", default=False)

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
        if context.mode!="OBJECT" and context.mode!="SCULPT":
            return 0
        return 1

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def check(self, context):
        return True

    def draw(self, context):
        box = self.layout.box()
        box.label('Basic options')
        box.prop(self, "hausd",  text="Haussdorf distance (ratio)")
        box.prop(self, "smooth", text="Ignore angle detection (smooth)")

        box = self.layout.box()
        box.prop(self, "weight", text="Use weight paint")
        if self.weight:
            box.label('Warning!')
            box.label('Low weights (blue) <-> max size')
            box.label('High weights (red) <-> min size')
            box.label('Min size too low -> very long!')
            box.label('Try defaults first!')
            box.prop(self, "hmin",   text="Minimal edge size (ratio)")
            box.prop(self, "hmax",   text="Maximal edge size (ratio)")

        box = self.layout.box()
        box.prop(self, "advanced", text="Advanced options")
        if self.advanced:
            box.prop(self, "angle",  text="Angle detection (°)")
            if not self.weight:
                box.prop(self, "hmin",   text="Minimal edge size (ratio)")
                box.prop(self, "hmax",   text="Maximal edge size (ratio)")
            box.prop(self, "hgrad",  text="Gradation parameter")
            box.prop(self, "aniso",  text="Enable anisotropy")
            box.prop(self, "nreg",   text="Normal regulation")

        col = self.layout.column(align=True)

    def execute(self, context):
        #Go into object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        obj    = context.active_object
        maxDim = max( max( obj.dimensions[0], obj.dimensions[1]) , obj.dimensions[2] )

        #Export
        tmpDir = tempfile.TemporaryDirectory()
        IN  = os.path.join(tmpDir.name, "tmp.mesh")
        OUT = os.path.join(tmpDir.name, "tmp.o.mesh")
        bpy.ops.bakemyscan.export_mesh(filepath=IN, writeSol=self.weight, miniSol=self.hmin * maxDim, maxiSol=self.hmax * maxDim)

        #Remesh
        exe = context.user_preferences.addons["BakeMyScan"].preferences.mmgs
        output, error, code = fn_soft.mmgs(
            executable  = exe,
            input_mesh  = IN,
            output_mesh = OUT,
            hausd       = self.hausd * maxDim,
            hgrad       = self.hgrad,
            hmin        = self.hmin * maxDim,
            hmax        = self.hmax * maxDim,
            ar          = self.angle,
            nr          = self.smooth,
            aniso       = self.aniso,
            nreg        = self.nreg,
        )

        #Reimport
        try:
            bpy.ops.bakemyscan.import_mesh(filepath=OUT)
            self.report({"INFO"}, "MMGS success")
            print("MMGS OUTPUT:\n%s\nMMGS ERROR:\n%s" % (output, error))
            return{'FINISHED'}
        except:
            self.report({"ERROR"}, "MMGS error, look in the console...")
            print("MMGS OUTPUT:\n%s\nMMGS ERROR:\n%s" % (output, error))
            return{"CANCELLED"}

def register() :
    bpy.utils.register_class(remesh_mmgs)

def unregister() :
    bpy.utils.unregister_class(remesh_mmgs)
