bl_info = {
    'name':     'BakeMyScan',
    'category': 'Import-Export',
    'version': (1, 0, 0),
    'blender': (2, 79, 0),
    "description": "Multipurpose add-on to texture, remesh and bake objects",
    "author": "Loïc NORGEOT"
}

import sys
import os
import importlib

#All python files in the src/ directory
modulesFiles = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith(".py")]
modulesNames = ["src." + f for f in modulesFiles]

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
