import bpy
import os

class remesh_decimate(bpy.types.Operator):
    bl_idname = "bakemyscan.remesh_decimate"
    bl_label  = "Remesh with the decimate modifier"
    bl_options = {"REGISTER", "UNDO"}

    limit    = bpy.props.IntProperty(name="limit",    description="Target faces", default=1500, min=50, max=500000)
    vertex_group = bpy.props.BoolProperty(name="vertex_group", description="Use vertex group", default=True)

    @classmethod
    def poll(self, context):
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

    def draw(self, context):
        self.layout.prop(self, "limit", text="target triangles")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        #Go into object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        #Duplicate the original mesh and make it active
        hr = context.scene.objects.active
        bpy.ops.object.duplicate()
        lr = context.scene.objects.active

        #Apply the modifiers
        for m in lr.modifiers:
            bpy.ops.object.modifier_apply(modifier=m.name)

        #First coarse decimate or mmgs or meshlabserver to get a medium poly?

        #Apply the modifier
        lr.modifiers.new("decimate", type='DECIMATE')
        lr.modifiers["decimate"].ratio = float(self.limit/len(lr.data.polygons))
        lr.modifiers["decimate"].use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier="decimate")

        #Shade smooth and rename
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = False
        context.active_object.name = hr.name + ".decimate"

        #Remove hypothetical material
        while len(context.active_object.material_slots):
            context.active_object.active_material_index = 0
            bpy.ops.object.material_slot_remove()

        self.report({'INFO'}, 'Remeshed to %s triangles' % len(context.active_object.data.polygons))

        return{'FINISHED'}

def register() :
    bpy.utils.register_class(remesh_decimate)

def unregister() :
    bpy.utils.unregister_class(remesh_decimate)
