"""
Usage:
blender --python import_scans_with_albedo.py -- -i INFILE
"""

import bpy
import sys
import os
import argparse
import imghdr

#Create an arguments parser
parser = argparse.ArgumentParser(description="Remesh a scan to a lowpoly model in blender")
parser.add_argument("-i", "--input",  dest="input",  type=str, metavar='FILE', required=True, help="Input model")
argv = sys.argv[sys.argv.index("--") + 1:]
args = parser.parse_args(argv)
args.input = os.path.abspath(args.input)

#Remove the delete file objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

#Import the base scan model
directories = [d for d in os.listdir(args.input) if os.path.isdir(os.path.join(os.path.abspath(args.input), d))][:]
directories.sort()
for directory in directories:
    #Prepare the variables for the directory
    image_path, model_path = None, None
    directory = os.path.abspath(os.path.join(args.input, directory))
    files     = [os.path.join(directory, f) for f in os.listdir(directory)]
    #Find the model and the image
    if len(files) != 2:
        print("%s does not contain two files!")
        pass
    else:
        try:
            image_path = [f for f in files if imghdr.what(f)][0]
            model_path = [f for f in files if f!=image_path][0]
        except:
            print("Did not find a model and an image in %s" % directory)
            pass

    #Get the name of the model and its extension
    filename = os.path.basename(model_path)
    name, ext = os.path.splitext(filename)
    name, ext = name.lower(), ext.lower()

    #Get a list of the current objects in the scene, to remove the unused ones later
    oldObjects = [o for o in bpy.data.objects]

    #Import the object with the appropriate function
    if ext==".obj":
        bpy.ops.import_scene.obj(filepath=model_path)
    elif ext==".ply":
        bpy.ops.import_mesh.ply(filepath=model_path)
    elif ext==".stl":
        bpy.ops.import_mesh.stl(filepath=model_path)
    elif ext==".fbx":
        bpy.ops.import_scene.fbx(filepath=model_path)
    elif ext==".dae":
        bpy.ops.wm.collada_import(filepath=model_path)
    elif ext==".wrl" or ext==".x3d":
        bpy.ops.import_scene.x3d(filepath=model_path)


    #Remove the new objects which are not a mesh
    newObjects = [o for o in bpy.data.objects if o not in oldObjects]
    for o in newObjects:
        if o.type != "MESH":
            bpy.data.objects.remove(o)
    newObjects = [o for o in bpy.data.objects if o not in oldObjects]

    #Don't treat the case in which there are multiple meshes
    """
    if len(newObjects) > 1:
        return {'CANCELLED'}
    """
    obj = newObjects[0]

    #Select the new mesh, and make it the active object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = 1
    bpy.context.scene.objects.active = obj

    #Remove the material if one was assigned
    if len(obj.material_slots)>0:
        for slot in obj.material_slots:
            if slot.material is not None:
                slot.material = None

    #Clear the custom split normals, sharp edges, doubles and loose
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.mark_sharp(clear=True)
    bpy.ops.mesh.customdata_custom_splitnormals_clear()
    bpy.ops.mesh.remove_doubles()
    bpy.ops.mesh.delete_loose()
    bpy.ops.object.editmode_toggle()

    #Center and scale it to one
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
    s = 1.0/(max(max(obj.dimensions[0], obj.dimensions[1]), obj.dimensions[2]))
    obj.scale = [s,s,s]
    bpy.ops.object.transform_apply(location=False, rotation=True)

    #Give it the name of the file
    obj.name = name

    #Add a new material
    mat = bpy.data.materials.new(name)
    obj.active_material = mat

    #Assign a texture to it
    image = bpy.data.images.load(image_path)
    tex = bpy.data.textures.new( name, type = 'IMAGE')
    tex.image = image
    mat.use_nodes = False
    mtex = mat.texture_slots.add()
    mtex.texture = tex
    mtex.texture_coords = 'UV'

    #print success
    print("Successfully imported %s and %s" % (model_path, image_path))


"""
#Get the interesting stuff
hr = bpy.context.active_object
mat = hr.active_material

bpy.ops.bakemyscan.remesh_iterative(limit=args.target)

#Select the two models to bake
hr.select=True

#Bake
bpy.ops.bakemyscan.bake_textures(
    resolution    = args.resolution,
    bake_albedo   = (args.albedo!=""),
    bake_geometry = True,
    bake_surface  = (args.normal!="")
)

#Export
hr.select = False
bpy.ops.bakemyscan.export_fbx(filepath=args.output)
"""
