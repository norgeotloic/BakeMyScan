import bpy
import os

class remesh_decimate(bpy.types.Operator):
    bl_idname = "bakemyscan.remesh_decimate"
    bl_label  = "Remesh with the decimate modifier"
    bl_options = {"REGISTER", "UNDO"}

    limit    = bpy.props.IntProperty(name="limit",    description="Target faces", default=1500, min=50, max=500000)
    vertex_group = bpy.props.BoolProperty(name="vertex_group", description="Use vertex group", default=True)

    def draw(self, context):
        self.layout.prop(self, "limit", text="target triangles")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        #Duplicate the original mesh and make it active
        hr = context.scene.objects.active
        bpy.ops.object.duplicate()
        lr = context.scene.objects.active

        #First coarse decimate or mmgs or meshlabserver to get a medium poly
        lr.modifiers.new("decimate", type='DECIMATE')
        lr.modifiers["decimate"].ratio = float(self.limit/len(lr.data.polygons))
        lr.modifiers["decimate"].use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier="decimate")

        return{'FINISHED'}

def register() :
    bpy.utils.register_class(remesh_decimate)

def unregister() :
    bpy.utils.unregister_class(remesh_decimate)
