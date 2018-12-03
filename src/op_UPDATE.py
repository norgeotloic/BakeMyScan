import asyncio
import requests
import functools
import json

import bpy
import os
import addon_utils

import tempfile
import urllib.request
import zipfile
import shutil

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
                print("A new update is available")
                print("%s -> %s" % (bpy.types.Scene.currentVersion, bpy.types.Scene.newVersion))
                for a in object[0]["assets"]:
                    if a["name"] == "BakeMyScan.zip":
                        bpy.types.Scene.update_url = a["browser_download_url"]
                        print(bpy.types.Scene.update_url)

class CheckUpdates(bpy.types.Operator):
    bl_idname = "bakemyscan.check_updates"
    bl_label  = "Check for updates"
    @classmethod
    def poll(self, context):
        return 1
    def execute(self, context):
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(do_request())
            return {"FINISHED"}
        except:
            self.report({"ERROR"}, "Version check inoperative. Is internet off?")

class Update(bpy.types.Operator):
    bl_idname = "bakemyscan.update"
    bl_label  = "Update BakeMyScan"

    tmp = tempfile.TemporaryDirectory()

    @classmethod
    def poll(self, context):
        if bpy.types.Scene.newVersion is None or bpy.types.Scene.currentVersion is None:
            return 0
        if bpy.types.Scene.newVersion == bpy.types.Scene.currentVersion:
            return 0
        if bpy.types.Scene.update_url is None:
            return 0
        return 1
    def execute(self, context):
        #Download
        download_path = os.path.join(self.tmp.name, "BakeMyScan.zip")
        urllib.request.urlretrieve(bpy.types.Scene.update_url, filename=download_path)
        #Extract
        extract_path = os.path.join(self.tmp.name, "tmp_extract")
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        #Move the BakeMyScan folder to the root temporary directory
        os.rename(os.path.join(self.tmp.name, "tmp_extract", "BakeMyScan"), os.path.join(self.tmp.name, "BakeMyScan"))
        shutil.rmtree(os.path.join(self.tmp.name, "tmp_extract"))
        #Replace
        final_path = os.path.join(bpy.utils.resource_path('USER'), "scripts", "addons", "BakeMyScan")
        print(final_path)
        go = True
        if go:
            if os.path.exists(final_path):
                if os.path.isdir(final_path):
                    shutil.rmtree(final_path)
                    os.rename(os.path.join(self.tmp.name, "BakeMyScan"), final_path)
        #Prepare the restart to update the scripts
        bpy.types.Scene.restartRequired = True
        return {"FINISHED"}

def register():
    bpy.utils.register_class(CheckUpdates)
    bpy.utils.register_class(Update)
    bpy.types.Scene.newVersion      = None
    bpy.types.Scene.currentVersion  = None
    bpy.types.Scene.update_url      = None
    bpy.types.Scene.restartRequired = False

def unregister():
    bpy.utils.unregister_class(CheckUpdates)
    bpy.utils.unregister_class(Update)
    del bpy.types.Scene.newVersion
    del bpy.types.Scene.currentVersion
    del bpy.types.Scene.update_url
    del bpy.types.Scene.restartRequired
