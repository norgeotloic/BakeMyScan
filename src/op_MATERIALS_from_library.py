# coding: utf8
import bpy
from . import fn_nodes

def get_materials_list_callback(scene, context):
    mats = [m for m in bpy.types.Scene.pbrtextures.keys()]
    mats.sort()
    return [(m, m, "", i) for i,m in enumerate(mats)]

class material_from_library(bpy.types.Operator):
    bl_idname = "bakemyscan.material_from_library"
    bl_label  = "Import a PBR material from a library"
    bl_options = {"REGISTER", "UNDO"}
    bl_property = "enum"

    enum = bpy.props.EnumProperty(
        name="PBR textures",
        description="",
        items=get_materials_list_callback
        )

    @classmethod
    def poll(self, context):
        #Need to be in Cycles render mode
        if bpy.context.scene.render.engine != "CYCLES":
            return 0
        if len(bpy.types.Scene.pbrtextures.keys())==0:
            return 0
        if len(context.selected_objects)!=1:
            for o in bpy.data.objects:
                print(o, o.select)
            return 0
        if context.active_object is None:
            return 0
        return 1

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

    def execute(self, context):
        #Create an empty material
        bpy.ops.bakemyscan.create_empty_material(name = self.enum)
        #Fill the textures
        mat = bpy.types.Scene.pbrtextures[self.enum]
        for _type in mat:
            if mat[_type] is not None:
                bpy.ops.bakemyscan.assign_texture(slot=_type, filepath=mat[_type])
        return{'FINISHED'}

class node_from_library(bpy.types.Operator):
    bl_idname = "bakemyscan.node_from_library"
    bl_label  = "Import a PBR node from a library"
    bl_options = {"REGISTER", "UNDO"}
    bl_property = "enum"

    enum = bpy.props.EnumProperty(
        name="PBR textures",
        description="",
        items=get_materials_list_callback
        )

    @classmethod
    def poll(self, context):
        #Need to be in Cycles render mode
        if bpy.context.scene.render.engine != "CYCLES":
            return 0
        if len(bpy.types.Scene.pbrtextures.keys())==0:
            return 0
        if len(context.selected_objects)!=1:
            for o in bpy.data.objects:
                print(o, o.select)
            return 0
        if context.active_object is None:
            return 0
        return 1

    def invoke(self, context, event):
        context.space_data.cursor_location_from_region(event.mouse_region_x, event.mouse_region_y)
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

    def execute(self, context):
        #Create an empty node
        bpy.ops.bakemyscan.create_empty_node(name = self.enum)
        #Fill the textures
        mat = bpy.types.Scene.pbrtextures[self.enum]
        for _type in mat:
            if mat[_type] is not None:
                bpy.ops.bakemyscan.assign_texture(slot=_type, filepath=mat[_type])
        self.report({'INFO'}, '"' + self.enum + '" imported')
        return{'FINISHED'}

def register() :
    bpy.utils.register_class(material_from_library)
    bpy.utils.register_class(node_from_library)

def unregister() :
    bpy.utils.unregister_class(material_from_library)
    bpy.utils.unregister_class(node_from_library)
