import asyncio
import requests
import functools
import json

import bpy
import os
import addon_utils

async def do_request():
    loop     = asyncio.get_event_loop()
    future   = loop.run_in_executor(None, requests.get, 'https://api.github.com/repos/norgeotloic/BakeMyScan/releases')
    response = await future
    object = json.loads(response.text)
    bpy.types.Scene.newVersion = object[0]["tag_name"]
    for mod in addon_utils.modules():
        if mod.bl_info.get("name") == "BakeMyScan":
            bpy.types.Scene.currentVersion = ".".join([str(x) for x in mod.bl_info.get("version")])
            if bpy.types.Scene.currentVersion == bpy.types.Scene.newVersion:
                print("No new updates")
            else:
                print("Oh yeah, a new update!")

class currentVersion(bpy.types.Operator):
    bl_idname = "bakemyscan.current_version"
    bl_label  = "Current version"
    @classmethod
    def poll(self, context):
        return 0

class checkUpdates(bpy.types.Operator):
    bl_idname = "bakemyscan.check_updates"
    bl_label  = "Check for updates"
    @classmethod
    def poll(self, context):
        return 1
    def execute(self, context):
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(do_request())
        if response is not None:

            return {"FINISHED"}
        else:
            return {"CANCELLED"}

def register():
    bpy.utils.register_class(currentVersion)
    bpy.utils.register_class(checkUpdates)
    bpy.types.Scene.newVersion = None
    bpy.types.Scene.currentVersion = None

def unregister():
    bpy.utils.unregister_class(currentVersion)
    bpy.utils.unregister_class(checkUpdates)
    del bpy.types.Scene.newVersion
    del bpy.types.Scene.currentVersion
