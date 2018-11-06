import bpy
import os
from bpy_extras.io_utils import ImportHelper
import addon_utils
import time

class remesh_iterative(bpy.types.Operator):
    bl_idname = "bakemyscan.remesh_iterative"
    bl_label  = "Remesh with an iterative method"
    bl_options = {"REGISTER", "UNDO"}

    limit    = bpy.props.IntProperty(name="limit",    description="Target faces", default=1500, min=50, max=500000)
    manifold = bpy.props.BoolProperty(name="manifold", description="Make manifold", default=False)
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
        self.layout.prop(self, "manifold", text="make manifold")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        print("Iterative method")
        t0 = time.time()

        #Go into object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        #Duplicate the original mesh and make it active
        hr = context.scene.objects.active
        bpy.ops.object.duplicate()
        lr = context.scene.objects.active

        #Apply the modifiers
        for m in lr.modifiers:
            bpy.ops.object.modifier_apply(modifier=m.name)

        #First coarse decimate to get a medium poly model
        if len(lr.data.polygons) > 50 * self.limit:
            print("-- First decimation because nTris > 50 x target")
            target = min(50 * self.limit, len(lr.data.polygons)/5)
            lr.modifiers.new("decimate", type='DECIMATE')
            lr.modifiers["decimate"].ratio = float(target/len(lr.data.polygons))
            lr.modifiers["decimate"].use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(modifier="decimate")

        #Iteration process to reach 1.5 x limit
        bpy.types.Scene.hr = hr
        iterate = True
        i = 0
        while(iterate):
            i+=1
            print("-- Iteration %d:" % i)
            lr = context.scene.objects.active
            bpy.ops.object.duplicate()
            bpy.ops.bakemyscan.remesh_one_iteration(manifold=self.manifold, vertex_group=self.vertex_group)
            tmp = context.scene.objects.active

            print("-- Iteration %d: %d tris -> %d tris" % (i, len(lr.data.polygons), len(tmp.data.polygons)) )

            if len(tmp.data.polygons) < self.limit:
                print("-- We went far enough, cancel the last iteration")
                iterate=False
                bpy.data.objects.remove(tmp)
                bpy.context.scene.objects.active = lr
                lr.select = True
            else:
                bpy.data.objects.remove(lr)
        del bpy.types.Scene.hr

        #Final decimation to stick to the limit
        print("-- Last decimate to be as exact as possible")
        lr.modifiers.new("decimate", type='DECIMATE')
        lr.modifiers["decimate"].ratio = float(self.limit/len(lr.data.polygons))
        lr.modifiers["decimate"].use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier="decimate")

        #Remove hypothetical material
        while len(context.active_object.material_slots):
            context.active_object.active_material_index = 0
            bpy.ops.object.material_slot_remove()

        # 6 - Remove non manifold and doubles
        print("-- Making manifold")
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.mesh.dissolve_degenerate(threshold=0.0001)
        bpy.ops.mesh.vert_connect_nonplanar()
        if self.manifold:
            addon_utils.enable("object_print3d_utils")
            bpy.ops.mesh.print3d_clean_non_manifold()
        bpy.ops.object.editmode_toggle()

        #Shade smooth and rename
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = False
        context.active_object.name = hr.name + ".iterative"

        self.report({'INFO'}, 'Remeshed to %s polys in %.2fs.' % (len(context.active_object.data.polygons), time.time() - t0))
        return{'FINISHED'}

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
        if context.mode!="OBJECT" and context.mode!="SCULPT":
            return 0
        return 1

    def execute(self, context):

        print("  -- Planar decimation")
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

        print("  -- Ensuring triangles only")
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.object.editmode_toggle()

        print("  -- Initial smoothing")
        bpy.ops.object.modifier_add(type='SMOOTH')
        bpy.context.object.modifiers["Smooth"].iterations = 1
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Smooth")

        print("  -- Initial decimation")
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].ratio = 0.8
        if len(bpy.context.object.vertex_groups)>0 and self.vertex_group:
            bpy.context.object.modifiers["Decimate"].vertex_group = bpy.context.object.vertex_groups[0].name
            bpy.context.object.modifiers["Decimate"].vertex_group_factor = 0.75
            bpy.context.object.modifiers["Decimate"].invert_vertex_group = True
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

        print("  -- Shrinkwrap")
        bpy.ops.object.modifier_add(type='SHRINKWRAP')
        bpy.context.object.modifiers["Shrinkwrap"].target = bpy.types.Scene.hr
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")

        return{'FINISHED'}


def register() :
    bpy.utils.register_class(do_one_iteration)
    bpy.utils.register_class(remesh_iterative)

def unregister() :
    bpy.utils.unregister_class(do_one_iteration)
    bpy.utils.unregister_class(remesh_iterative)
