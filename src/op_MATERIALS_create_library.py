# coding: utf8
import os
import bpy

from . import fn_match

class list_textures(bpy.types.Operator):
    bl_idname = "bakemyscan.list_textures"
    bl_label  = "List available materials"
    bl_options = {"REGISTER", "UNDO"}

    filepath = bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for importing the file",
        maxlen=1024,
        subtype='DIR_PATH')

    def execute(self, context):

        materials = fn_match.findMaterials(os.path.dirname(self.properties.filepath))

        bpy.types.Scene.pbrtextures = materials
        for m in materials:
            print(m, len(materials[m].keys()))
        self.report({'INFO'}, 'Found %d PBR materials (see the console)' % (len(materials.keys())))
        return{'FINISHED'}

def register() :
    bpy.utils.register_class(list_textures)
    bpy.types.Scene.pbrtextures = {}

def unregister() :
    bpy.utils.unregister_class(list_textures)
    del bpy.types.Scene.pbrtextures
