import bpy
import os
from bpy_extras.io_utils import ImportHelper
import addon_utils

class do_one_iteration(bpy.types.Operator):
    bl_idname = "bakemyscan.remesh_one_iteration"
    bl_label  = "Do one iteration for remshing"
    bl_options = {"REGISTER", "UNDO"}

    manifold     = bpy.props.BoolProperty(name="manifold", description="Make manifold", default=False)
    vertex_group = bpy.props.BoolProperty(name="vertex_group", description="Use vertex group", default=False)

    @classmethod
    def poll(self, context):
        #If more than two objects are selected
        if len(context.selected_objects)!=1 or context.active_object is None:
            return 0
        #If something other than a MESH is selected
        for o in context.selected_objects:
            if o.type != "MESH":
                return 0
        return 1

    def execute(self, context):
        # 1 - planar decimation
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

        # 2 - triangulate the mesh
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.object.editmode_toggle()

        # 3 - smooth the vertices
        bpy.ops.object.modifier_add(type='SMOOTH')
        bpy.context.object.modifiers["Smooth"].iterations = 1
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Smooth")

        # 4 - decimate it
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].ratio = 0.8
        if len(bpy.context.object.vertex_groups)>0 and self.vertex_group:
            bpy.context.object.modifiers["Decimate"].vertex_group = bpy.context.object.vertex_groups[0].name
            bpy.context.object.modifiers["Decimate"].vertex_group_factor = 0.75
            bpy.context.object.modifiers["Decimate"].invert_vertex_group = True
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")


        # 5 - shrinkwrap to the original
        bpy.ops.object.modifier_add(type='SHRINKWRAP')
        bpy.context.object.modifiers["Shrinkwrap"].target = bpy.types.Scene.hr
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")

        # 6 - Remove non manifold and doubles
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.mesh.dissolve_degenerate(threshold=0.0001)
        bpy.ops.mesh.vert_connect_nonplanar()
        if self.manifold:
            addon_utils.enable("object_print3d_utils")
            bpy.ops.mesh.print3d_clean_non_manifold()
        bpy.ops.object.editmode_toggle()

        return{'FINISHED'}


class remesh_iterative(bpy.types.Operator):
    bl_idname = "bakemyscan.remesh_iterative"
    bl_label  = "Remesh to a target number of faces"
    bl_options = {"REGISTER", "UNDO"}

    limit    = bpy.props.IntProperty(name="limit",    description="Target faces", default=1500, min=50, max=500000)
    manifold = bpy.props.BoolProperty(name="manifold", description="Make manifold", default=False)
    vertex_group = bpy.props.BoolProperty(name="vertex_group", description="Use vertex group", default=True)

    def draw(self, context):
        self.layout.prop(self, "limit", text="target triangles")
        self.layout.prop(self, "manifold", text="make manifold")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        #Duplicate the original mesh and make it active
        hr = context.scene.objects.active
        bpy.ops.object.duplicate_move()
        lr = context.scene.objects.active

        #First coarse decimate or mmgs or meshlabserver to get a medium poly
        if len(lr.data.polygons) > 50 * self.limit:
            target = min(50 * self.limit, len(lr.data.polygons)/5)
            lr.modifiers.new("decimate", type='DECIMATE')
            lr.modifiers["decimate"].ratio = float(target/len(lr.data.polygons))
            lr.modifiers["decimate"].use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(modifier="decimate")

        #Iteration process to reach 1.5 x limit
        bpy.types.Scene.hr = hr
        iterate = True
        while(iterate):
            lr = context.scene.objects.active
            bpy.ops.object.duplicate_move()
            bpy.ops.bakemyscan.remesh_one_iteration(manifold=self.manifold, vertex_group=self.vertex_group)
            tmp = context.scene.objects.active
            print(self.limit, len(tmp.data.polygons), len(lr.data.polygons))
            if len(tmp.data.polygons) < self.limit:
                iterate=False
                bpy.data.objects.remove(tmp)
                bpy.context.scene.objects.active = lr
                lr.select = True
            else:
                bpy.data.objects.remove(lr)
        del bpy.types.Scene.hr

        #Final decimation to stick to the limit
        lr.modifiers.new("decimate", type='DECIMATE')
        lr.modifiers["decimate"].ratio = float(self.limit/len(lr.data.polygons))
        lr.modifiers["decimate"].use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier="decimate")

        #Remove the materials
        for i,slot in enumerate(lr.material_slots):
            if slot.material is not None:
                slot.material = None
                if i>0:
                    bpy.ops.object.material_slot_remove()

        #Smart unwrapping
        bpy.ops.uv.smart_project()
        #UV "optimization"
        bpy.ops.object.editmode_toggle()
        bpy.ops.uv.select_all(action='SELECT')
        for i in range(5):
            bpy.ops.uv.average_islands_scale()
            bpy.ops.uv.pack_islands(margin=0.005)
        bpy.ops.object.editmode_toggle()

        return{'FINISHED'}

def register() :
    bpy.utils.register_class(do_one_iteration)
    bpy.utils.register_class(remesh_iterative)

def unregister() :
    bpy.utils.unregister_class(do_one_iteration)
    bpy.utils.unregister_class(remesh_iterative)
