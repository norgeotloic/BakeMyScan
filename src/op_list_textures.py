# coding: utf8
import imghdr
import os
import bpy
from bpy_extras.io_utils import ImportHelper

from . import fn_match

class AvailablePBRTextures(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.pbrtextures = {}
        # ... and so on adding properties to cls

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.pbrtextures

class list_textures(bpy.types.Operator, ImportHelper):
    bl_idname = "bakemyscan.list_textures"
    bl_label  = "List available materials"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = "."
    use_filter_folder = True

    def execute(self, context):

        materials = findMaterials(os.path.dirname(self.properties.filepath))

        bpy.types.Scene.pbrtextures = materials
        for m in materials:
            print(m, len(materials[m].keys()))
        self.report({'INFO'}, 'Found %d PBR materials (see the console)' % (len(materials.keys())))
        return{'FINISHED'}

def register() :
    bpy.utils.register_class(list_textures)
    bpy.utils.register_class(AvailablePBRTextures)

def unregister() :
    bpy.utils.unregister_class(list_textures)
    bpy.utils.unregister_class(AvailablePBRTextures)
