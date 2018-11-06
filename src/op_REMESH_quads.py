"""
1 - Decimate
2 - Tris to quads
3 - Subdivision
4 - Shrinkwrap to the original
5 - Shade smooth and rename
"""

import bpy
import os
import time

class remesh_quads(bpy.types.Operator):
    bl_idname = "bakemyscan.remesh_quads"
    bl_label  = "Dirty quads with decimate and tristoquads and subdivide trick"
    bl_options = {"REGISTER", "UNDO"}

    nfaces = bpy.props.IntProperty(name="nfaces",   description="Decimate ratio",  default=1500, min=50, max=200000)
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
        if context.mode!="OBJECT" and context.mode!="SCULPT":
            return 0
        return 1

    def draw(self, context):
        self.layout.prop(self, "nfaces",  text="Number of quads (min)")
        self.layout.prop(self, "smooth", text="Relaxation steps")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
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

        #Guess the resulting number of faces
        ratio = 2 * self.nfaces / ( 4 * len(lr.data.polygons) )

        #Decimate it
        print("Decimating with ratio %.4f" % ratio)
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].ratio = ratio
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

        #Tris to quads
        print("Converting triangles to quadrilaterals")
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.tris_convert_to_quads(face_threshold=3.14159, shape_threshold=3.14159)
        bpy.ops.object.editmode_toggle()

        #Subdivision
        print("Subdividing")
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels = 1
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")

        #Relaxation steps
        print("Relaxation steps")
        for i in range(self.smooth):
            print("Smoothing: %d/%d" % (i+1, self.smooth))
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.vertices_smooth()
            bpy.ops.object.editmode_toggle()

            #Shrinkwrap to the original
            print("Shrinkwrapping: %d/%d" % (i+1, self.smooth))
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers["Shrinkwrap"].target = hr
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")

        #Smoothing
        print("Ultimate smoothing")
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.vertices_smooth()
        bpy.ops.object.editmode_toggle()

        #Shade smooth and rename
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.use_auto_smooth = False
        context.active_object.name = hr.name + ".quads"

        #Remove hypothetical material
        while len(context.active_object.material_slots):
            context.active_object.active_material_index = 0
            bpy.ops.object.material_slot_remove()


        self.report({'INFO'}, 'Remeshed to %s polys in %.2fs.' % (len(context.active_object.data.polygons), time.time() - t0))
        return{'FINISHED'}

def register() :
    bpy.utils.register_class(remesh_quads)

def unregister() :
    bpy.utils.unregister_class(remesh_quads)
