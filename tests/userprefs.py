#travis
#blender/blender --addons BakeMyScan --background --python BakeMyScan/scripts/tests/userprefs.py -- --mmgs bin/mmgs_O3 --instant "Instant Meshes/Instant Meshes" --meshlabserver "LC_ALL=C meshlabserver"
#windows
#blender --addons BakeMyScan --background --python BakeMyScan\scripts\tests\userprefs.py -- --mmgs "C:\Users\lnorgeot\Downloads\bin\mmgs_O3.exe" --instant "C:\Users\lnorgeot\Downloads\bin\Instant Meshes.exe" --meshlabserver "C:\Program Files\VCG\Meshlab\meshlabserver.exe"

import argparse
import os
import bpy
import sys

if __name__ == "__main__":

    #Create the parser
    parser = argparse.ArgumentParser(description="Tests the BakeMyScan add-on")

    #Create the arguments
    parser.add_argument("--mmgs",          type=str, required=True, help="Path to mmgs executable")
    parser.add_argument("--instant",       type=str, required=True, help="Path to Instant Meshes executable")
    parser.add_argument("--meshlabserver", type=str, required=True, help="Path to meshlabserver executable")

    #Parse
    argv = sys.argv[sys.argv.index("--") + 1:]
    args = parser.parse_args(argv)

    #Make the executable paths absolute
    try:
        if os.path.exists(args.mmgs):
            args.mmgs = os.path.abspath(args.mmgs)
        if os.path.exists(args.instant):
            args.instant = os.path.abspath(args.instant)
        if os.path.exists(args.meshlabserver):
            args.meshlabserver = os.path.abspath(args.meshlabserver)
    except:
        print("Did not managed to make the paths absolute")
        sys.exit(1)

    #print everything
    print(args.mmgs)
    print(args.instant)
    print(args.meshlabserver)

    #Activate the addon
    try:
        bpy.ops.wm.addon_enable(module="BakeMyScan")
    except:
        print("Error enabling the addon")
        sys.exit(2)

    #Set the executables in the addon user preferences
    try:
        bpy.context.user_preferences.addons["BakeMyScan"].preferences.mmgs          = args.mmgs
        bpy.context.user_preferences.addons["BakeMyScan"].preferences.instant       = args.instant
        bpy.context.user_preferences.addons["BakeMyScan"].preferences.meshlabserver = args.meshlabserver
    except:
        print("Error setting the paths in preferences")
        sys.exit(3)

    #Save the user preferences
    try:
        bpy.ops.wm.save_userpref()
    except:
        print("Error saving the user preferences")
        sys.exit(4)

    sys.exit(0)
