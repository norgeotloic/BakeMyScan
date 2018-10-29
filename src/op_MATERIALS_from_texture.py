# coding: utf8
import os
import bpy
from   bpy_extras.io_utils import ImportHelper

from . import fn_match
from . import fn_nodes

class material_from_texture(bpy.types.Operator, ImportHelper):
    bl_idname = "bakemyscan.material_from_texture"
    bl_label  = "List available materials"
    bl_options = {"REGISTER", "UNDO"}

    filter_glob = bpy.props.StringProperty(
        default="*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff;*.exr",
        options={'HIDDEN'},
    )

    @classmethod
    def poll(self, context):
        #Need to be in Cycles render mode
        if bpy.context.scene.render.engine != "CYCLES":
            return 0
        if bpy.context.active_object is None:
            return 0
        if len([o for o in bpy.context.selected_objects if o.type=="MESH"])!=1:
            return 0
        return 1

    def execute(self, context):
        name, settings = fn_match.findMaterialFromTexture(self.filepath)
        if settings is not None:
            #Create a new material
            bpy.ops.bakemyscan.create_empty_material()
            mat = context.active_object.active_material
            mat.name = name
            for s in settings:
                bpy.ops.bakemyscan.assign_texture(slot=s, filepath=settings[s])
            return{'FINISHED'}
        else:
            print("Did not manage to find a matching material")
            return{'CANCELLED'}

def register() :
    bpy.utils.register_class(material_from_texture)

def unregister() :
    bpy.utils.unregister_class(material_from_texture)
