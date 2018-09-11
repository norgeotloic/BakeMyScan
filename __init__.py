bl_info = {
    'name':     'BakeMyScan',
    'category': 'Import-Export',
    'version': (0, 1, 0),
    'blender': (2, 79, 0),
    "description": "Multipurpose add-on to texture and bake scans",
    "author": "Loïc NORGEOT"
}

import sys
import os
import importlib

modulesFiles = [
    "fn_match", "fn_nodes", "fn_msh", "fn_ortho", "fn_soft",            # Functions
    "op_import_scan", "op_export_orthoview",                            # Initial operators
    "op_remesh_iterative", "op_remesh_mmgs",                            # Remeshing operators
    "op_list_textures", "op_import_material",                           # Material operators
    "op_bake_textures", "op_remove_all_but_selected", "op_export_fbx",  # Baking operators
    "op_import_mesh", "op_export_mesh"                                  # .mesh format operators
]
modulesNames = ["src." + f for f in modulesFiles]
modulesNames += ["GUI"]

modulesFullNames = {}
for currentModuleName in modulesNames:
    modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))

for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        print(currentModuleFullName)
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)

def register():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()

def unregister():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()

if __name__ == "__main__":
    register()
