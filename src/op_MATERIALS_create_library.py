# coding: utf8
import os
import bpy

from . import fn_match

class create_library(bpy.types.Operator):
    bl_idname = "bakemyscan.create_library"
    bl_label  = "List available materials"
    bl_options = {"REGISTER", "UNDO"}

    filepath = bpy.props.StringProperty(
        name="filepath",
        description="Filepath used for importing the file",
        maxlen=1024,
        subtype='DIR_PATH')

    @classmethod
    def poll(self, context):
        #Need to be in Cycles render mode
        if bpy.context.scene.render.engine != "CYCLES":
            return 0
        return 1

    def execute(self, context):

        materials = fn_match.findMaterials(os.path.dirname(self.properties.filepath))

        bpy.types.Scene.pbrtextures = materials
        for m in materials:
            print(m, len(materials[m].keys()))
        self.report({'INFO'}, 'Found %d PBR materials (see the console)' % (len(materials.keys())))
        return{'FINISHED'}

def register() :
    bpy.utils.register_class(create_library)
    bpy.types.Scene.pbrtextures = {}

def unregister() :
    bpy.utils.unregister_class(create_library)
    try:
        del bpy.types.Scene.pbrtextures
    except:
        pass
