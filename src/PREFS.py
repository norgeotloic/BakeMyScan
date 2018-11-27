import bpy
import os
import json

import shutil

def is_exe(exe):
    return shutil.which(exe) is not None

def absolute_paths(self, context):
    #Make the paths absolute
    bpy.types.Scene.executables["mmgs"] = os.path.abspath(bpy.path.abspath(self.mmgs)) if self.mmgs!="" else ""
    bpy.types.Scene.executables["instant"] = os.path.abspath(bpy.path.abspath(self.instant)) if self.instant!="" else ""
    bpy.types.Scene.executables["quadriflow"] = os.path.abspath(bpy.path.abspath(self.quadriflow)) if self.quadriflow!="" else ""
    bpy.types.Scene.executables["meshlabserver"] = os.path.abspath(bpy.path.abspath(self.meshlabserver)) if self.meshlabserver!="" else ""
    bpy.types.Scene.executables["colmap"] = os.path.abspath(bpy.path.abspath(self.colmap)) if self.colmap!="" else ""
    bpy.types.Scene.executables["interfacevisualsfm"] = os.path.abspath(bpy.path.abspath(self.interfacevisualsfm)) if self.interfacevisualsfm!="" else ""
    bpy.types.Scene.executables["densifypointcloud"] = os.path.abspath(bpy.path.abspath(self.densifypointcloud)) if self.densifypointcloud!="" else ""
    bpy.types.Scene.executables["reconstructmesh"] = os.path.abspath(bpy.path.abspath(self.reconstructmesh)) if self.reconstructmesh!="" else ""
    bpy.types.Scene.executables["texturemesh"] = os.path.abspath(bpy.path.abspath(self.texturemesh)) if self.texturemesh!="" else ""
    bpy.types.Scene.executables["openmvsdir"] = os.path.abspath(bpy.path.abspath(self.openmvsdir)) if self.openmvsdir!="" else ""

    #Check that everything is an executable
    oneWrong = False
    for x in bpy.types.Scene.executables:
        if x!="openmvsdir":
            exe = bpy.types.Scene.executables[x]
            if not is_exe(exe):
                print("ERROR: %s is not a valid executable!" % exe)
                bpy.types.Scene.executables[x] = ""
                oneWrong = True
    if not oneWrong:
        print("All provided paths seem valid, we're good to go!")

    #Write to a .json file to keep even after updating the addon
    path = os.path.join(bpy.utils.resource_path('USER'), "bakemyscan.config")
    try:
        with open(path, 'w') as fp:
            json.dump(bpy.types.Scene.executables, fp, sort_keys=True, indent=4)
    except:
        print("Can't write into %s" % bpy.utils.resource_path('USER'), "bakemyscan.config")
    return None

def find_openmvs_executables(self, context):
    bpy.types.Scene.executables["openmvsdir"] = os.path.abspath(bpy.path.abspath(self.openmvsdir)) if self.openmvsdir!="" else ""
    D = bpy.types.Scene.executables["openmvsdir"]
    if os.path.isdir(D):
        for f in os.listdir(D):
            if "InterfaceVisualSFM" in f:
                self.interfacevisualsfm = os.path.join(D, f)
            if "DensifyPointCloud" in f:
                self.densifypointcloud = os.path.join(D, f)
            if "ReconstructMesh" in f:
                self.reconstructmesh = os.path.join(D, f)
            if "TextureMesh" in f:
                self.texturemesh = os.path.join(D, f)
    return None

def updatepath(self, context):
    print("Reading in materials from %s" % self.texturepath)
    bpy.ops.bakemyscan.create_library(filepath=self.texturepath)
    path = os.path.join(bpy.utils.resource_path('USER'), "materials.json")
    try:
        with open(path, 'w') as fp:
            json.dump(bpy.types.Scene.pbrtextures, fp, sort_keys=True, indent=4)
        print("Successfully saved %d texture sets to %s" % (len(bpy.types.Scene.pbrtextures), path))
    except:
        pass
    return None

class BakeMyScanPrefs(bpy.types.AddonPreferences):
    bl_idname     = 'BakeMyScan'

    executables = {}
    #Remeshers
    mmgs          = bpy.props.StringProperty(name="MMGS Executable", subtype='FILE_PATH', update=absolute_paths)
    instant       = bpy.props.StringProperty(name="Instant Meshes Executable", subtype='FILE_PATH', update=absolute_paths)
    quadriflow    = bpy.props.StringProperty(name="Quadriflow Executable", subtype='FILE_PATH', update=absolute_paths)
    meshlabserver = bpy.props.StringProperty(name="Meshlabserver Executable", subtype='FILE_PATH', update=absolute_paths)
    #Scanning executables
    colmap        = bpy.props.StringProperty(name="Colmap Executable", subtype='FILE_PATH', update=absolute_paths)
    openmvsdir    = bpy.props.StringProperty(name="OpenMVS directory", subtype='DIR_PATH', update=find_openmvs_executables)
    #OpenMVS executables
    interfacevisualsfm = bpy.props.StringProperty(name="InterfaceVisualSFM", subtype='FILE_PATH', update=absolute_paths)
    densifypointcloud  = bpy.props.StringProperty(name="DensifyPointCloud", subtype='FILE_PATH', update=absolute_paths)
    reconstructmesh    = bpy.props.StringProperty(name="ReconstructMesh", subtype='FILE_PATH', update=absolute_paths)
    texturemesh        = bpy.props.StringProperty(name="TextureMesh", subtype='FILE_PATH', update=absolute_paths)

    #Texture library
    texturepath =  bpy.props.StringProperty(description="PBR textures library", subtype='DIR_PATH', update=updatepath)



    def check(self, context):
        return True
    def draw(self, context):
        layout = self.layout
        layout.label(text="PBR textures path")
        layout.prop(self, "texturepath")
        layout.label(text="Remeshing tools")
        layout.prop(self, "instant")
        layout.prop(self, "mmgs")
        layout.prop(self, "quadriflow")
        layout.prop(self, "meshlabserver")
        layout.label(text="Photogrammetry")
        layout.prop(self, "colmap")
        layout.prop(self, "openmvsdir")
        #Display the OpenMVS executables
        if self.openmvsdir != "":
            layout.prop(self, "interfacevisualsfm")
            layout.prop(self, "densifypointcloud")
            layout.prop(self, "reconstructmesh")
            layout.prop(self, "texturemesh")

def register():
    bpy.types.Scene.executables = {}
    bpy.utils.register_class(BakeMyScanPrefs)

    PREFS = bpy.context.user_preferences.addons["BakeMyScan"].preferences

    #Try to read in the preferences from the saved file
    path = os.path.join(bpy.utils.resource_path('USER'), "bakemyscan.config")
    if os.path.exists(path):
        with open(path, 'r') as fp:
            bpy.types.Scene.executables = json.load(fp)
            #Assign them to the variables
            for x in bpy.types.Scene.executables.keys():
                if x in PREFS:
                    if PREFS[x] == "":
                        PREFS[x] = bpy.types.Scene.executables[x]
                else:
                    PREFS[x] = bpy.types.Scene.executables[x]
    else:
        for x in PREFS:
            if PREFS[x] is not None and PREFS[x]!="":
                bpy.types.Scene.executables[x] = PREFS[x]

    #Try to read in the textures from the .json file
    path = os.path.join(bpy.utils.resource_path('USER'), "materials.json")
    if os.path.exists(path):
        with open(path, 'r') as fp:
            bpy.types.Scene.pbrtextures = json.load(fp)
            print("Successfully loaded %d texture sets from %s" % (len(bpy.types.Scene.pbrtextures), path))

def unregister():
    bpy.utils.unregister_class(BakeMyScanPrefs)
    del bpy.types.Scene.executables
