import bpy
import os

class remove_all_but_selected(bpy.types.Operator):
    bl_idname = "bakemyscan.remove_all_but_selected"
    bl_label  = "Removes unused and unselected"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        #Need to have at least one mesh selected
        if len([ o for o in context.selected_objects if o.type == "MESH"]) == 0:
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

        #Get the materials being used
        mats = []
        for o in [x for x in objs if x.type=="MESH"]:
            for slot in o.material_slots:
                if slot.material is not None:
                    mats.append(slot.material)

        #Remove the materials with 0 users
        for mat in bpy.data.materials:
            if mat.users==0:
                bpy.data.materials.remove(mat)

        #Remove the materials which are not used by objects in the scene
        for mat in bpy.data.materials:
            if mat not in mats:
                bpy.data.materials.remove(mat)

        #Remove the node groups with 0 users
        for grp in bpy.data.node_groups:
            if grp.users==0:
                bpy.data.node_groups.remove(grp)

        #Remove the textures with 0 users
        for tex in bpy.data.textures:
            if tex.users==0:
                bpy.data.textures.remove(tex)

        #Remove the images with 0 users
        for img in bpy.data.images:
            if img.users==0:
                bpy.data.images.remove(img)

        #Update the scene
        bpy.context.scene.update()
        bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
        for window in bpy.context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    bpy.context.area.tag_redraw()

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):

        self.layout.label('Click OK to proceed')
        col = self.layout.column(align=True)

def register() :
    bpy.utils.register_class(remove_all_but_selected)

def unregister() :
    bpy.utils.unregister_class(remove_all_but_selected)
