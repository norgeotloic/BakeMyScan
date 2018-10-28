# coding: utf8
import os
import bpy
from bpy_extras.io_utils import ExportHelper
import json

class save_json_library(bpy.types.Operator, ExportHelper):
    bl_idname = "bakemyscan.save_json_library"
    bl_label  = "Save the material library to a JSON file"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext=".json"

    @classmethod
    def poll(self, context):
        #Need to be in Cycles render mode
        if bpy.context.scene.render.engine != "CYCLES":
            return 0
        #Try to get the library
        if len(bpy.types.Scene.pbrtextures.keys())==0:
            return 0
        #Final return
        return 1


    def execute(self, context):

        with open(self.filepath, 'w') as fp:
            json.dump(bpy.types.Scene.pbrtextures, fp, sort_keys=True, indent=4)

        self.report({'INFO'}, 'Wrote the library to JSON file')
        return{'FINISHED'}

def register() :
    bpy.utils.register_class(save_json_library)

def unregister() :
    bpy.utils.unregister_class(save_json_library)
