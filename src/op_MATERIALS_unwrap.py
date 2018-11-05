# coding: utf8
import bpy

class unwrap(bpy.types.Operator):
    bl_idname = "bakemyscan.unwrap"
    bl_label  = "Unwrap the model"
    bl_options = {"REGISTER", "UNDO"}

    method = bpy.props.EnumProperty(
        items= (
            ('basic',   'Basic unwrapping',   'Basic unwrapping'),
            ("smart",   "Smart UV project",   "Smart UV project"),
            ("smarter", "Smarter UV project", "Smarter UV project")
        ) ,
        name="method",
        description="Unwrapping method",
        default="smarter"
    )

    @classmethod
    def poll(self, context):
        if bpy.context.active_object is None:
            return 0
        if len([o for o in bpy.context.selected_objects if o.type=="MESH"])!=1:
            return 0
        return 1

    def draw(self, context):
        self.layout.prop(self, "method", text="Unwrapping method")
        col = self.layout.column(align=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        obj = context.active_object

        if self.method == "basic":
            bpy.ops.object.editmode_toggle()
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
            bpy.ops.object.editmode_toggle()
        elif self.method == "smart":
            bpy.ops.uv.smart_project(island_margin=0.001)
        elif self.method == "smarter":
            bpy.ops.uv.smart_project(island_margin=0.001)
            bpy.ops.object.editmode_toggle()
            bpy.ops.uv.select_all(action='SELECT')
            for i in range(5):
                bpy.ops.uv.average_islands_scale()
                bpy.ops.uv.pack_islands(margin=0.001)
            bpy.ops.object.editmode_toggle()

        self.report({'INFO'}, 'Model unwrapped')
        return{'FINISHED'}

def register() :
    bpy.utils.register_class(unwrap)

def unregister() :
    bpy.utils.unregister_class(unwrap)
