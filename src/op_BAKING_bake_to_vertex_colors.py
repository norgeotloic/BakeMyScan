import bpy
import os
from bpy_extras.io_utils import ExportHelper

from . import fn_bake

class bake_to_vertex_colors(bpy.types.Operator):
    """Assume a PBR material is present, will bake from cycles"""
    bl_idname = "bakemyscan.bake_to_vertex_colors"
    bl_label  = "Textures to vertex colors"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        #Render engine must be cycles
        if bpy.context.scene.render.engine!="CYCLES":
            return 0
        #If more than two objects are selected
        if len(context.selected_objects)!=1:
            return 0
        #If no object is active
        if context.active_object is None:
            return 0
        #If something other than a MESH is selected
        if context.active_object.type != "MESH":
            return 0
        #Each material must be not None and have nodes
        if context.active_object.active_material is None:
            return 0
        if context.active_object.active_material.use_nodes:
            return 0
        if context.mode!="OBJECT":
            return 0
        return 1

    def execute(self, context):
        obj = context.active_object
        mat = obj.active_material

        #Get the image from the PBR material
        image_nodes = fn_bake.get_all_nodes_in_material(mat, node_type="TEX_IMAGE")
        albedo      = [a["node"] for a in image_nodes if a["node"].name == "albedo"]
        if len(albedo)!=1:
            print("Material is not correct!")
            return{'CANCELLED'}

        image = albedo[0].image

        #Switch to blender render and adapt the materials
        bpy.context.scene.render.engine = 'BLENDER_RENDER'

        #Set some baking parameters
        bpy.context.scene.render.use_bake_selected_to_active = False
        bpy.context.scene.render.use_bake_to_vertex_color    = True
        bpy.context.scene.render.bake_type = "TEXTURE"

        #Add a vertex color group to the object
        obj.data.vertex_colors.new()
        bpy.ops.object.vertex_group_add()

        #Prepare the material
        mat.use_nodes              = False
        mat.use_vertex_color_paint = True

        #Assign the image to a texture slot
        if not bpy.data.textures.get("tmp_vertexcolors"):
            bpy.data.textures.new( "tmp_vertexcolors", type = 'IMAGE')
        tex = bpy.data.textures.get("tmp_vertexcolors")
        tex.image = image
        slots = mat.texture_slots
        slots.clear(0)
        mtex = slots.add()
        mtex.texture = tex
        mtex.texture_coords = 'UV'

        #Assign the vertex paint
        bpy.ops.paint.vertex_paint_toggle()
        bpy.ops.paint.vertex_paint_toggle()

        #And add the image in edit mode to the image editor
        bpy.ops.object.editmode_toggle()
        bpy.data.screens['UV Editing'].areas[1].spaces[0].image = image
        #bpy.context.object.active_material.use_textures[0] = False
        bpy.ops.object.bake_image()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.bake_image()

        #Reset to Cycles
        bpy.context.scene.render.engine = 'CYCLES'
        mat.use_nodes = True

        return{'FINISHED'}

def register() :
    bpy.utils.register_class(bake_to_vertex_colors)

def unregister() :
    bpy.utils.unregister_class(bake_to_vertex_colors)
