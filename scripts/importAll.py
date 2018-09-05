"""
Usage:
blender --python importAll.py -- -i INPUT -r NROWS
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

#Remove the initial objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

#Import all the 3D models with their textures
models = [f for f in os.listdir(args.input) if f[-4:] == ".fbx"]
for m in models:
    #Import the model
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.import_scene.fbx(filepath=os.path.join(args.input, m))
    rootName = os.path.splitext(m)[0]
    obj = [o for o in bpy.data.objects if o.select][0]
    obj.name = rootName
    mat = obj.material_slots[0].material
    mat.name = rootName

    #Import the albedo and normals if they exist
    for f in os.listdir(args.input):
        if rootName + "_ALBEDO" in f:
            path         = os.path.join(args.input, f)
            img          = bpy.data.images.load(path, check_existing=False)
            tex          = bpy.data.textures.new( rootName + "_albedo",  "IMAGE" )
            tex.image    = img
            slot         = mat.texture_slots.add()
            slot.texture = tex
        if rootName + "_NORMAL" in f:
            path         = os.path.join(args.input, f)
            img          = bpy.data.images.load(path, check_existing=False)
            tex          = bpy.data.textures.new( rootName + "_normal",  "IMAGE" )
            tex.image    = img
            slot         = mat.texture_slots.add()
            slot.texture = tex
            tex.use_normal_map  = True
            slot.use_map_normal = True
            slot.use_map_color_diffuse = False

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
