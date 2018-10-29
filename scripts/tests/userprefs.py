#travis
#blender/blender --addons BakeMyScan --background --python BakeMyScan/scripts/tests/userprefs.py -- --mmgs bin/mmgs_O3 --instant "Instant Meshes/Instant Meshes" --convert convert --meshlabserver "LC_ALL=C meshlabserver"
#windows
#blender --addons BakeMyScan --background --python BakeMyScan\scripts\tests\userprefs.py -- --mmgs "C:\Users\lnorgeot\Downloads\bin\mmgs_O3.exe" --instant "C:\Users\lnorgeot\Downloads\bin\Instant Meshes.exe" --convert "C:\Program Files\ImageMagick-7.0.8-Q16\magick.exe convert" --meshlabserver "C:\Program Files\VCG\Meshlab\meshlabserver.exe"

import argparse
import os
import bpy
import sys

if __name__ == "__main__":

    try:

        #Create the parser
        parser = argparse.ArgumentParser(description="Tests the BakeMyScan add-on")

        #Create the arguments
        parser.add_argument("--mmgs",          type=str, required=True, help="Path to mmgs executable")
        parser.add_argument("--instant",       type=str, required=True, help="Path to Instant Meshes executable")
        parser.add_argument("--meshlabserver", type=str, required=True, help="Path to meshlabserver executable")
        parser.add_argument("--convert",       type=str, required=True, help="Path to ImageMagick convert executable")

        #Parse
        argv = sys.argv[sys.argv.index("--") + 1:]
        args = parser.parse_args(argv)

        #Make the executable paths absolute
        if os.path.exists(args.mmgs):
            args.mmgs = os.path.abspath(args.mmgs)
        if os.path.exists(args.instant):
            args.instant = os.path.abspath(args.instant)
        if os.path.exists(args.meshlabserver):
            args.meshlabserver = os.path.abspath(args.meshlabserver)
        if os.path.exists(args.convert):
            args.convert = os.path.abspath(args.convert)

        #Activate the addon
        bpy.ops.wm.addon_enable(module="BakeMyScan")

        #Set the executables in the addon user preferences
        bpy.context.user_preferences.addons["BakeMyScan"].preferences.mmgs          = args.mmgs
        bpy.context.user_preferences.addons["BakeMyScan"].preferences.instant       = args.instant
        bpy.context.user_preferences.addons["BakeMyScan"].preferences.meshlabserver = args.meshlabserver
        bpy.context.user_preferences.addons["BakeMyScan"].preferences.convert       = args.convert

        #Save the user preferences
        bpy.ops.wm.save_userpref()

        sys.exit(0)

    except:

        sys.exit(1)
