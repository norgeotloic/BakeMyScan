import bpy
import os

class remesh_quads(bpy.types.Operator):
    bl_idname = "bakemyscan.remesh_quads"
    bl_label  = "Remesh with decimate and a naive quadrilateral conversion"
    bl_options = {"REGISTER", "UNDO"}

    ratio  = bpy.props.FloatProperty(name="ratio",  description="Decimate ratio",  default=0.01, min=0.0001, max=1)
    smooth = bpy.props.IntProperty(  name="smooth", description="Smoothing steps", default=1, min=0, max=15)

    @classmethod
    def poll(self, context):
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

    def draw(self, context):
        self.layout.prop(self, "ratio",  text="Decimation ratio")
        self.layout.prop(self, "smooth", text="Smoothing iterations")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        #Duplicate the original mesh and make it active
        hr = context.scene.objects.active
        bpy.ops.object.duplicate()
        lr = context.scene.objects.active

        #Decimate it
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].ratio = self.ratio
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

        #Tris to quads
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.mesh.tris_convert_to_quads()
        for i in range(self.smooth):
            bpy.ops.mesh.vertices_smooth()
        bpy.ops.object.editmode_toggle()

        #Shrinkwrap to the original
        bpy.ops.object.modifier_add(type='SHRINKWRAP')
        bpy.context.object.modifiers["Shrinkwrap"].target = hr
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")

        #One last smoothing?
        """
        bpy.ops.object.modifier_add(type='SMOOTH')
        bpy.context.object.modifiers["Smooth"].factor = 0.
        bpy.context.object.modifiers["Smooth"].iterations = 1.
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Smooth")
        """

        #Subdivision
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels = 1
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")

        return{'FINISHED'}

def register() :
    bpy.utils.register_class(remesh_quads)

def unregister() :
    bpy.utils.unregister_class(remesh_quads)
