"""
Remesh one scan to a lowpoly version

Usage:
blender --background --python bakeOne.py -- -i inputFile -o outputFile -t targetNumberOfFaces -r resolution -a albedoImage -n normalImage

For instance, to remesh scan.obj to 500 triangles and save the resulting mesh to scan01.blend associated with 2048px images:
blender --background --python bakeOne.py -- -i scan.obj -o scan01.blend -t 500 -r 2048 -a model_albedo.jpg -n model_normals.jpg
"""

import bpy
import sys
import os
import argparse
import imghdr

#Create an arguments parser
parser = argparse.ArgumentParser(description="Remesh a scan to a lowpoly model in blender")
parser.add_argument("-i", "--input",  dest="input",  type=str, metavar='FILE', required=True, help="Input model")
parser.add_argument("-o", "--output", dest="output", type=str, metavar='FILE', required=True, help="Output model")
parser.add_argument("-a", "--albedo", dest="albedo", type=str, metavar='FILE', help="Albedo image file")
parser.add_argument("-n", "--normal", dest="normal", type=str, metavar='FILE', help="Normal image file")
parser.add_argument("-t", "--target", dest="target", type=int, default=1500,   help="Target number of faces")
parser.add_argument("-r", "--resolution", dest="resolution", type=int, default=1024, help="Baked textures resolution")

#Parse the arguments
argv = sys.argv[sys.argv.index("--") + 1:]
args = parser.parse_args(argv)

#Check their validity
if not os.path.exists(args.input):
    print("ERROR: " + args.input + " is not a valid file")
    sys.exit(1)
args.input = os.path.abspath(args.input)
if args.output.split(".")[-1]!="fbx" and args.output.split(".")[-1]!="blend":
    print("ERROR: " + args.output + " must be either a .fbx or .blend file")
    sys.exit(1)
args.output = os.path.abspath(args.output)
if args.albedo is not None:
    if not os.path.exists(args.albedo):
        print("ERROR: " + args.albedo + " does not exist")
        sys.exit(1)
    if imghdr.what(args.albedo) is None:
        print("ERROR: " + args.albedo + " is not a valid image")
        sys.exit(1)
    args.albedo = os.path.abspath(args.albedo)
if args.normal is not None:
    if not os.path.exists(args.normal):
        print("ERROR: " + args.normal + " does not exist")
        sys.exit(1)
    if imghdr.what(args.normal) is None:
        print("ERROR: " + args.normal + " is not a valid image")
        sys.exit(1)
    args.normal = os.path.abspath(args.normal)

#Remove the delete file objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

#Import the base scan model
bpy.ops.lowpolymyscan.import_scan(filepath = args.input)

#Get the interesting stuff
hr = bpy.context.active_object
mat = hr.material_slots[0].material

#Add the textures to the material
if args.albedo is not None:
    img = bpy.data.images.load(args.albedo)
    mat.texture_slots[0].texture.image = img
if args.normal is not None:
    img = bpy.data.images.load(args.normal)
    mat.texture_slots[1].texture.image = img

bpy.ops.lowpolymyscan.remesh(limit=args.target)

#Select the two models to bake
hr.select=True

#Bake
bpy.ops.lowpolymyscan.bake(resolution=args.resolution, bake_albedo=(args.albedo is not None), bake_normals=(args.normal is not None))

#Export
hr.select = False
if args.output.split(".")[-1] == "blend":
    bpy.ops.lowpolymyscan.export_blend(filepath=args.output)
if args.output.split(".")[-1] == "fbx":
    bpy.ops.lowpolymyscan.export_fbx(filepath=args.output)
