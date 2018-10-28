import bpy
import os
from bpy_extras.io_utils import ExportHelper
from . import fn_nodes
from . import fn_soft

class bake_to_vertex_colors(bpy.types.Operator):
    bl_idname = "bakemyscan.bake_to_vertex_colors"
    bl_label  = "Bake textures"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        #Render engine must be cycles
        if bpy.context.scene.render.engine!="CYCLES":
            return 0
        #If more than two objects are selected
        if len(context.selected_objects)>2:
            return 0
        #If no object is active
        if context.active_object is None:
            return 0
        #If something other than a MESH is selected
        for o in context.selected_objects:
            if o.type != "MESH":
                return 0
        #The source object must have correct materials
        source = [o for o in context.selected_objects if o!=context.active_object][0] if len(context.selected_objects)==2 else context.active_object
        #it must have slots
        if len(source.material_slots)==0:
            return 0
        #Each material must be not None and have nodes
        for slot in source.material_slots:
            if slot.material is None:
                return 0
            if slot.material.use_nodes == False:
                return 0
        if context.mode!="OBJECT":
            return 0
        return 1

    def execute(self, context):

        objects = [o for o in bpy.context.selected_objects if o.type == "MESH"]

        #Get the source and the target
        source = [o for o in context.selected_objects if o!=context.active_object][0] if len(context.selected_objects)==2 else context.active_object
        target = context.active_object

        #Bake the albedo to an image
        bake_textures

        #Switch to blender render and adapt the materials
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        source.active_material.use_nodes = False

        #Set some baking parameters
        bpy.context.scene.render.use_bake_selected_to_active = True
        bpy.context.scene.render.bake_type = "TEXTURE"
        bpy.context.scene.render.use_bake_to_vertex_color = True

        #Add a vertex color group to the target
        target.data.vertex_colors.new()
        bpy.ops.object.vertex_group_add()

        #And a new material
        if not bpy.data.materials.get("vertexcolors"):
            bpy.data.materials.new("vertexcolors")
        mat = bpy.data.materials.get("vertexcolors")
        mat.use_vertex_color_paint = True
        target.material_slots[0].material = mat

        #Prepare the baking parameters in blender internal
        if not bpy.data.images.get("tmp_vertexcolors"):
            bpy.data.images.new("tmp_vertexcolors", 512, 512)
        image = bpy.data.images.get("tmp_vertexcolors")
        tex = None
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
        bpy.context.object.active_material.use_textures[0] = False
        bpy.ops.object.bake_image()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.bake_image()

        return{'FINISHED'}

def register() :
    bpy.utils.register_class(bake_to_vertex_colors)

def unregister() :
    bpy.utils.unregister_class(bake_to_vertex_colors)
