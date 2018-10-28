# coding: utf8
import os
import bpy
from bpy_extras.io_utils import ImportHelper
import json

class load_json_library(bpy.types.Operator, ImportHelper):
    bl_idname = "bakemyscan.load_json_library"
    bl_label  = "Load the material library from a JSON file"
    bl_options = {"REGISTER", "UNDO"}

    bl_label  = "Material library from .json"
    filter_glob = bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
    )
    check_extension = True
    filename_ext=".json"

    @classmethod
    def poll(self, context):
        #Need to be in Cycles render mode
        if bpy.context.scene.render.engine != "CYCLES":
            return 0
        #Final return
        return 1

    def execute(self, context):

        with open(self.filepath, 'r') as fp:
            bpy.types.Scene.pbrtextures = json.load(fp)

        self.report({'INFO'}, 'Found %d materials in the JSON file' % len(bpy.types.Scene.pbrtextures.keys()))
        return{'FINISHED'}

def register() :
    bpy.utils.register_class(load_json_library)

def unregister() :
    bpy.utils.unregister_class(load_json_library)
