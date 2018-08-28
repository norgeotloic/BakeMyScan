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

modulesNames =  ["src." + f.replace(".py", "") for f in os.listdir("src/") if "op_" in f]
modulesNames += "GUI"

modulesFullNames = {}
for currentModuleName in modulesNames:
    modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))

for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
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
