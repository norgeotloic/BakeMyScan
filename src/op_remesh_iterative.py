import bpy
import os
from bpy_extras.io_utils import ImportHelper

class remesh_iterative(bpy.types.Operator):
    bl_idname = "bakemyscan.remesh_iterative"
    bl_label  = "Remesh to a target number of faces"
    bl_options = {"REGISTER", "UNDO"}

    limit = bpy.props.IntProperty(name="limit", description="Target faces", default=1500, min=50, max=500000)

    def draw(self, context):
        self.layout.prop(self, "limit", text="target triangles")

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
        while( len(lr.data.polygons) > 1.5*self.limit ):

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
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

            # 5 - shrinkwrap to the original
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers["Shrinkwrap"].target = hr
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")

            # 6 - Remove non manifold and doubles
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.remove_doubles(threshold=0.0001)
            bpy.ops.mesh.dissolve_degenerate(threshold=0.0001)
            bpy.ops.mesh.vert_connect_nonplanar()
            bpy.ops.mesh.print3d_clean_non_manifold()
            bpy.ops.object.editmode_toggle()

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
    bpy.utils.register_class(remesh_iterative)

def unregister() :
    bpy.utils.unregister_class(remesh_iterative)
