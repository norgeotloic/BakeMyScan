"""
Usage:
blender --python importAll.py -- -i INDIR [-r NUMROWS]
"""

import bpy
import sys
import os
import argparse

#Create an arguments parser
parser = argparse.ArgumentParser(description="Import .fbx files on a nice grid layout")
parser.add_argument("-i", "--input", dest="input", type=str, metavar='FILE', required=True, help="Input models directory")
parser.add_argument("-r", "--rows",  dest="rows",  type=int, default=5, help="Number of rows to import the models on")

#Parse the arguments
argv = sys.argv[sys.argv.index("--") + 1:]
args = parser.parse_args(argv)

#Check their validity
if not os.path.exists(args.input):
    print("ERROR: " + args.input + " is not a valid file")
    sys.exit(1)
if not os.path.isdir(args.input):
    print("ERROR: " + args.input + " is not a directory")
    sys.exit(1)
args.input = os.path.abspath(args.input)

bpy.context.scene.render.engine = "CYCLES"

#Remove the initial objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

#Import all the 3D models with their textures
models = [f for f in os.listdir(args.input) if f[-4:] == ".fbx"]
for m in models:

    #Get the object name from its path
    name = os.path.splitext(m)[0]

    #Import the model and make it active
    bpy.ops.bakemyscan.import_scan(filepath = os.path.join(args.input, m))
    obj = [o for o in bpy.data.objects if o.select][0]
    bpy.context.scene.objects.active = obj
    obj.name = name

    #Try to create a material from a texture
    for f in os.listdir(args.input):
        if name in f:
            bpy.ops.bakemyscan.material_from_texture(filepath=os.path.join(args.input, f))
            #Maybe convert it to a blender internal material?

#Get the number of columns
columns = int(len(models)/args.rows) + 1

#rearrange objects on a grid
for i,o in enumerate([ o for o in bpy.data.objects if o.type=="MESH" ]):
    r = int(i/columns)
    c = i%columns
    o.location = [c - (columns-1)/2, (args.rows-1)/2 - r , 0]

#add a lamp and go to material rendering
bpy.ops.object.lamp_add(type='SUN', radius=1, view_align=False, location=(0, 0, 0), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
for area in bpy.data.screens["Default"].areas:
    if area.type == "VIEW_3D":
        area.spaces[0].viewport_shade = "MATERIAL"
