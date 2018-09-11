import bpy
import os

class remove_all_but_selected(bpy.types.Operator):
    bl_idname = "bakemyscan.remove_all_but_selected"
    bl_label  = "Removes unused objects, textures..."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        #Render engine must be cycles
        if bpy.context.scene.render.engine!="CYCLES":
            return 0
        #If more than two objects are selected
        if len(context.selected_objects)==0:
            return 0
        #If something other than a MESH is selected
        for o in context.selected_objects:
            if o.type != "MESH":
                return 0
        #Must be in object mode
        if context.mode!="OBJECT":
            return 0
        return 1

    def execute(self, context):
        objs = [o for o in context.selected_objects]
        #Remove all but the selected object
        for o in bpy.data.objects:
            if o not in objs:
                bpy.data.objects.remove(o)
        #Unused materials
        mats = []
        for o in objs:
            for slot in o.material_slots:
                if slot.material is not None:
                    mats.append(slot.material)
        for mat in bpy.data.materials:
            if mat.users==0:
                bpy.data.materials.remove(mat)
        for mat in bpy.data.materials:
            if mat not in mats:
                bpy.data.materials.remove(mat)
        #Unused textures
        for tex in bpy.data.textures:
            if tex.users==0:
                bpy.data.textures.remove(tex)
        #Unused images
        for img in bpy.data.images:
            if img.users==0:
                bpy.data.images.remove(img)

        return {'FINISHED'}

def register() :
    bpy.utils.register_class(remove_all_but_selected)

def unregister() :
    bpy.utils.unregister_class(remove_all_but_selected)
