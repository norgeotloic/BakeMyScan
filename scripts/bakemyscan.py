"""
Reprocess one model to a lowpoly version

Examples:
blender -b -P bakemyscan.py model.obj model.fbx
blender -b -P bakemyscan.py model.obj model.fbx -Z
blender -b -P bakemyscan.py model.obj model.fbx -M MMGS -X 0.005
blender -b -P bakemyscan.py model.obj model.fbx -M INSTANT -X 4000
blender -b -P bakemyscan.py model.obj model.fbx -M QUADRIFLOW -X 3000
blender -b -P bakemyscan.py model.obj model.fbx -M MESHLAB -X 500
blender -b -P bakemyscan.py model.obj model.fbx -M ITERATIVE -X 1000
blender -b -P bakemyscan.py model.obj model.fbx -M DECIMATE -X 1000
blender -b -P bakemyscan.py model.obj model.fbx -M NAIVEQUADS -X 0.01
blender -b -P bakemyscan.py model.obj model.fbx -R 2048 --color albedo.png --normal nm.jpg --metallic metal.tif --roughness rough.jpeg --ao ambientOcc.jpg --displacement heightmap.PNG --emission emit.jpg --opacity alpha.png
"""

import bpy
import sys
import os
import argparse
import imghdr

def get_args():
    """Processes the command line arguments"""
    argv = sys.argv[sys.argv.index("--") + 1:]

    def arg_from_name(_parser, _name, _help):
        parser.add_argument("-"+_name[0], "--" + _name, help=_help, type=str)

    msg1 = 'Remeshing method: "MMGS", "INSTANT", "QUADRIFLOW", "MESHLAB", "DEIMATE", "ITERATIVE", "DECIMATE" (defaults to "ITERATIVE")'
    msg2 = "Depends on chosen method: Number of faces or Relative Haussdorf (try 0.01 for MMGS) or Resolution (try 2500 for INSTANT and QUADRIFLOW) or Ratio (try 0.01 for NAIVEQUADS)"

    parser = argparse.ArgumentParser(description="Remesh a scan to a lowpoly model in blender")
    parser.prog = "blender -b -P /path/to/bakemyscan.py"

    parser.add_argument("input",  type=str, help="Input model (.fbx, .obj, .ply, .wrl, .x3d, .dae)")
    parser.add_argument("output", type=str, help="Output model (.fbx, .obj, .ply)")

    parser.add_argument("-Z", "--zip", action="store_true", help="Compress the files into a .zip archive", default=False)
    parser.add_argument("-M", "--method", type=str, help=msg1, default="ITERATIVE")
    parser.add_argument("-X", "--target", type=int, default=1500,   help=msg2)
    parser.add_argument("-R", "--resolution",   type=int, default=1024,   help="Output resolution")

    arg_from_name(parser, "color",        "Base Color")
    arg_from_name(parser, "metallic",     "Metallic")
    arg_from_name(parser, "roughness",    "Roughness")
    arg_from_name(parser, "glossiness",   "Glossiness")
    arg_from_name(parser, "ao",           "Ambient occlusion")
    arg_from_name(parser, "normal",       "Normal map")
    arg_from_name(parser, "displacement", "Displacement map")
    arg_from_name(parser, "emission",     "Emission")
    arg_from_name(parser, "opacity",      "Opacity")

    args = parser.parse_args(argv)

    def check_valid_file(_file, _exts=None, _image=False, _can_create=False):
        if _file is not None:
            if not _can_create:
                if not os.path.exists(_file):
                    parser.print_help()
                    print('ERROR: did not find "' + _file + '"')
                    sys.exit(1)
            if _exts is not None:
                if os.path.splitext(_file)[1].lower() not in _exts:
                    parser.print_help()
                    print('ERROR: invalid extension for "%s"' % _file)
                    sys.exit(2)
            _file = os.path.abspath(_file)
            if _image:
                if imghdr.what(_file) is None:
                    parser.print_help()
                    print('Error: "%s" is not an image')
                    sys.exit(3)
            if _can_create:
                _dir = os.path.dirname(_file)
                if not os.path.exists(_dir):
                    parser.print_help()
                    print('Error: "%s" is not a directory')
                    sys.exit(4)
        return _file

    args.input  = check_valid_file(args.input,  [".fbx", ".obj", ".ply", ".wrl", ".x3d", ".dae", ".stl"])
    args.output = check_valid_file(args.output, [".fbx", ".obj", ".ply"], _can_create=True)

    args.color        = check_valid_file(args.color, _image=True)
    args.metallic     = check_valid_file(args.metallic, _image=True)
    args.roughness    = check_valid_file(args.roughness, _image=True)
    args.glossiness   = check_valid_file(args.glossiness, _image=True)
    args.ao           = check_valid_file(args.ao, _image=True)
    args.normal       = check_valid_file(args.normal, _image=True)
    args.displacement = check_valid_file(args.displacement, _image=True)
    args.emission     = check_valid_file(args.emission, _image=True)
    args.opacity      = check_valid_file(args.opacity, _image=True)

    if args.method not in ["MMGS", "INSTANT", "QUADRIFLOW", "MESHLAB", "DEIMATE", "ITERATIVE", "DECIMATE"]:
        parser.print_help()
        print('ERROR: invalid method name')
        sys.exit(5)
    if args.method == "MMGS" and bpy.types.Scene.executables["mmgs"] == "":
        print("MMGS is not configured in the user preferences")
        sys.exit(6)
    if args.method == "INSTANT" and bpy.types.Scene.executables["instant"] == "":
        print("Instant Meshes is not configured in the user preferences")
        sys.exit(7)
    if args.method == "QUADRIFLOW" and bpy.types.Scene.executables["quadriflow"] == "":
        print("Quadriflow is not configured in the user preferences")
        sys.exit(8)
    if args.method == "MESHLAB" and bpy.types.Scene.executables["meshlabserver"] == "":
        print("Meshlabserver is not configured in the user preferences")
        sys.exit(9)

    return args

if __name__ == "__main__":

    #Parse the arguments
    args = get_args()

    #Setup
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.context.scene.render.engine = "CYCLES"

    #Import
    bpy.ops.bakemyscan.import_scan(filepath = args.input)
    bpy.ops.bakemyscan.clean_object()
    original = bpy.context.active_object

    #Add a material
    bpy.ops.bakemyscan.create_empty_material()

    #Assign the textures
    def assign(_slot_name, _texture):
        if _texture is not None:
            bpy.ops.bakemyscan.assign_texture(slot=_slot_name, filepath=_texture)
    assign("albedo", args.color)
    assign("metallic", args.metallic)
    assign("roughness", args.roughness)
    assign("glossiness", args.glossiness)
    assign("ao", args.ao)
    assign("normal", args.normal)
    assign("height", args.displacement)
    assign("emission", args.emission)
    assign("opacity", args.opacity)

    #Remesh
    if args.method == "MMGS":
        bpy.ops.bakemyscan.remesh_mmgs(hausd=args.target)
    elif args.method == "INSTANT":
        bpy.ops.bakemyscan.remesh_instant(facescount=args.target)
    elif args.method == "QUADRIFLOW":
        bpy.ops.bakemyscan.remesh_quadriflow(resolution=args.target)
    elif args.method == "MESHLAB":
        bpy.ops.bakemyscan.remesh_meshlab(facescount=args.target)
    elif args.method == "ITERATIVE":
        bpy.ops.bakemyscan.remesh_iterative(limit=args.target)
    elif args.method == "NAIVEQUADS":
        bpy.ops.bakemyscan.remesh_quads(ratio=args.target)
    elif args.method == "DECIMATE":
        bpy.ops.bakemyscan.remesh_decimate(limit=args.target)

    #Unwrap and smooth
    bpy.ops.bakemyscan.unwrap(method="smarter")
    bpy.ops.object.shade_smooth()

    #Bake
    original.select=True
    bpy.ops.bakemyscan.bake_textures(
        resolution    = args.resolution,
        bake_albedo   = args.color is not None,
        bake_metallic = args.metallic is not None,
        bake_roughness = args.roughness is not None or args.glossiness is not None,
        bake_ao        = args.ao is not None,
        bake_surface   = args.displacement is not None or args.normal is not None,
        bake_geometry = True,
        bake_emission = args.emission is not None,
        bake_opacity  = args.opacity is not None,
    )

    #Export
    original.select = False
    bpy.ops.bakemyscan.remove_all_but_selected()
    bpy.ops.bakemyscan.export(filepath=args.output, compress=args.zip)
