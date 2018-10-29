#On windows
#blender --addons BakeMyScan --background --python BakeMyScan\scripts\tests\tests.py
#On linux
#blender --addons BakeMyScan --background --python BakeMyScan/scripts/tests/tests.py

#Need to have run the userprefs before:
#blender --addons BakeMyScan --background --python BakeMyScan\scripts\tests\userprefs.py -- --mmgs bin/mmgs_O3 --instant 'Instant Meshes/Instant Meshes' --convert convert --meshlabserver 'LC_ALL=C meshlabserver'

import collections
import bpy
import os
import time
import sys
import json

################################################################################
# 1 - A class to manage the execution of the different test cases
################################################################################

class TestSequence:

    def __init__(self):
        self.operators = collections.OrderedDict()

    def reset(self):
        #Remove all the objects
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        #Switch to Cycles render engine
        bpy.context.scene.render.engine = "CYCLES"
        #Empty pbrtextures
        bpy.types.Scene.pbrtextures = {}
        #Relmove the temporary .json file
        jsonfile = os.path.join(os.path.dirname(__file__), "test.json")
        if os.path.exists(jsonfile):
            os.remove(jsonfile)

    def add_operator(self, name, operator, args={}, reset=True, before=None, after=None):
        op = {
            "name": operator,
            "args": args,
            "reset": reset,
            "before": before,
            "after": after,
            "status":None,
            "time":0
        }
        self.operators[name] = op

    def run(self):
        #For each operator in the stack
        for name in self.operators:

            #Get parameters
            OP                = self.operators[name]
            operator_function = getattr(bpy.ops.bakemyscan, OP["name"])
            args              = OP["args"]
            t = time.time()

            #Run the operator and wrapper functions
            try:
                #Reset the file
                if OP["reset"]:
                    self.reset()
                #Preprocessing
                if OP["before"] is not None:
                    OP["before"]()
                #Run the operator
                if operator_function.poll():
                    operator_function(**args)
                    #Post-processing
                    if OP["after"] is not None:
                        OP["after"]()
                    #Set the status to success
                    OP["status"] = "SUCCESS"
                else:
                    #The poll function did not return, context is incorrect
                    OP["status"] = "CONTEXT"
            #If an error occured
            except:
                print("Error using %s" % OP["name"])
                OP["status"] = "FAILURE"

            OP["time"] = time.time() - t

    def report(self):
        nTests  = len(self.operators.keys())
        nPassed = 0
        #Count the number of passed tests
        for operator in self.operators:
            if self.operators[operator]["status"] == "SUCCESS":
                nPassed+=1
            else:
                pass
        #Return and print according to the number of successful tests
        if nPassed == nTests:
            print("Successfully ran the %d tests" % nTests)
            for operator in self.operators:
                OP = self.operators[operator]
                print("%s: %s in %f s" % (operator.ljust(30), OP["status"], OP["time"]) )
            return 0
        else:
            print("Failed %d tests out of %d" % (nTests - nPassed, nTests))
            for operator in self.operators:
                OP = self.operators[operator]
                print("%s: %s in %f s" % (operator.ljust(30), OP["status"], OP["time"]) )
            return 1

################################################################################
# 2 - Test the different operators with as much use cases as possible
################################################################################

if __name__ == "__main__":
    TESTS = TestSequence()
    TESTS.reset()

    ############################################################################
    # 2.0 - Functions used before operators and to check the results
    ############################################################################

    def create_suzanne():
        bpy.ops.mesh.primitive_monkey_add()
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels = 2
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")
        bpy.context.active_object.select=True
    def empty_material_library():
        bpy.types.Scene.pbrtextures = {}
    def prepare_for_baking():
        source = bpy.data.objects["Suzanne"]
        bpy.ops.mesh.primitive_monkey_add(calc_uvs=True)
        target = bpy.context.active_object
        source.select = True

    def assert_model_imported():
        assert(len(bpy.data.objects) == 1)
    def assert_suzanne_remeshed():
        assert(len(bpy.data.objects) == 2)
        assert(bpy.context.active_object is not None)
        assert(bpy.context.active_object.name != "Suzanne")
        assert(len(bpy.context.active_object.data.polygons)!=len(bpy.data.objects["Suzanne"].data.polygons))
    def assert_pbr_library_non_empty():
        assert(len(bpy.types.Scene.pbrtextures.keys())>0)
    def assert_json_non_empty():
        with open(os.path.join(os.path.dirname(__file__),"test.json"), 'r') as fp:
            bpy.types.Scene.pbrtextures = json.load(fp)
    def assert_suzanne_has_material():
        obj = bpy.context.active_object
        assert(len(obj.material_slots)>0)
        assert(obj.material_slots[0].material is not None)
        assert(obj.material_slots[0].material.use_nodes == True)
        assert(len([x for x in obj.material_slots[0].material.node_tree.nodes if x.type=="GROUP"])>0)
    def assert_suzanne_is_unwrapped():
        obj = bpy.data.objects["Suzanne"]
        assert(len(obj.data.uv_layers)>0)
    def assert_orthoview_created():
        assert(os.path.exists(os.path.join(os.path.dirname(__file__),"orthoview.png")))
        os.remove(os.path.join(os.path.dirname(__file__),"orthoview.png"))
    def assert_baked_textures():
        alb = os.path.join(os.path.dirname(__file__), "baked_basecolor.png")
        nor = os.path.join(os.path.dirname(__file__), "baked_normals.png")
        rou = os.path.join(os.path.dirname(__file__), "baked_roughness.png")
        met = os.path.join(os.path.dirname(__file__), "baked_metallic.png")
        assert(os.path.exists(alb))
        assert(os.path.exists(nor))
        assert(os.path.exists(rou))
        assert(os.path.exists(met))
        os.remove(alb)
        os.remove(nor)
        os.remove(rou)
        os.remove(met)
    def assert_mesh_file_created():
        assert(os.path.exists(os.path.join(os.path.dirname(__file__),"suzanne.mesh")))
        os.remove(os.path.join(os.path.dirname(__file__),"suzanne.mesh"))
    def assert_cube_read():
        assert( len(bpy.data.objects) == 1 )
        assert( len(bpy.context.active_object.data.polygons) == 12 )

    ############################################################################
    # 2.1 - Testing the import operators on cubes in different formats
    ############################################################################

    #Import a .obj
    TESTS.add_operator(
        name="import_obj",
        operator="import_scan",
        args = {"filepath": os.path.join(os.path.dirname(__file__), "cube.obj")},
        after = assert_model_imported
    )

    #Import a .ply
    TESTS.add_operator(
        name="import_ply",
        operator="import_scan",
        args = {"filepath": os.path.join(os.path.dirname(__file__), "cube.ply")},
        after = assert_model_imported
    )

    #Import a .stl
    TESTS.add_operator(
        name="import_stl",
        operator="import_scan",
        args = {"filepath": os.path.join(os.path.dirname(__file__), "cube.stl")},
        after = assert_model_imported
    )

    #Import a .fbx
    TESTS.add_operator(
        name="import_fbx",
        operator="import_scan",
        args = {"filepath": os.path.join(os.path.dirname(__file__), "cube.fbx")},
        after = assert_model_imported
    )

    #Import a .dae
    TESTS.add_operator(
        name="import_dae",
        operator="import_scan",
        args = {"filepath": os.path.join(os.path.dirname(__file__), "cube.dae")},
        after = assert_model_imported
    )

    #Import a .x3d
    TESTS.add_operator(
        name="import_x3d",
        operator="import_scan",
        args = {"filepath": os.path.join(os.path.dirname(__file__), "cube.x3d")},
        after = assert_model_imported
    )

    ############################################################################
    # 2.2 - Preprocessing filter on the last imported cube
    ############################################################################

    #Preprocess a cube
    TESTS.add_operator(
        name="preprocessing",
        operator="clean_object",
        reset=False
    )

    ############################################################################
    # 2.3 - Internal remeshing methods
    ############################################################################

    #Remesh suzanne with the simple decimate modifier
    TESTS.add_operator(
        name="remesh_decimate",
        operator="remesh_decimate",
        before=create_suzanne,
        after=assert_suzanne_remeshed,
        reset=True,
        args={"limit":300}
    )

    #Remesh suzanne with the naive quads method
    TESTS.add_operator(
        name="remesh_quads",
        operator="remesh_quads",
        before=create_suzanne,
        after=assert_suzanne_remeshed,
        reset=True,
        args={"ratio":0.01, "smooth":2}
    )

    #Remesh suzanne with an iterative method
    TESTS.add_operator(
        name="remesh_iterative",
        operator="remesh_iterative",
        before=create_suzanne,
        after=assert_suzanne_remeshed,
        reset=True,
        args={"limit":500}
    )

    ############################################################################
    # 2.4 - External remeshing methods
    ############################################################################

    #Remesh suzanne with mmgs
    TESTS.add_operator(
        name="remesh_mmgs",
        operator="remesh_mmgs",
        before=create_suzanne,
        after=assert_suzanne_remeshed,
        reset=True,
        args={"smooth":True, "hausd":0.01}
    )

    #Remesh suzanne with Instant Meshes
    TESTS.add_operator(
        name="remesh_instant",
        operator="remesh_instant",
        before=create_suzanne,
        after=assert_suzanne_remeshed,
        reset=True,
        args={"interactive":False, "method":"faces", "facescount":1000}
    )

    #Do not run meshlabserver on Travis, as it needs a X server to run
    if not "travis" in os.path.abspath(os.getcwd()):
        #Remesh suzanne with meshlabserver
        TESTS.add_operator(
            name="remesh_meshlab",
            operator="remesh_meshlab",
            before=create_suzanne,
            after=assert_suzanne_remeshed,
            reset=True,
            args={"facescount":1500}
        )

    ############################################################################
    # 2.5 - PBR textures library operators
    ############################################################################

    #Read textures from a directory
    TESTS.add_operator(
        name="create_library",
        operator="create_library",
        args={"filepath":os.path.dirname(__file__)},
        after=assert_pbr_library_non_empty,
        reset=True
    )

    #Import a material which was read previously
    TESTS.add_operator(
        name="material_from_library",
        operator="material_from_library",
        args={"enum":"stick"},
        before=create_suzanne,
        after=assert_suzanne_has_material,
        reset=False,
    )

    #Save the current library as a .json file for future use
    TESTS.add_operator(
        name="save_json",
        operator="save_json_library",
        args={"filepath":os.path.join(os.path.dirname(__file__),"test.json")},
        after=assert_json_non_empty,
        reset=False
    )

    #Load a library from a .json file
    TESTS.add_operator(
        name="load_json",
        operator="load_json_library",
        args={"filepath":os.path.join(os.path.dirname(__file__),"test.json")},
        before=empty_material_library,
        after=assert_pbr_library_non_empty,
        reset=False
    )

    #Import a material from a library, loaded from a .json file
    TESTS.add_operator(
        name="material_from_json",
        operator="material_from_library",
        args={"enum":"stick"},
        before=create_suzanne,
        after=assert_suzanne_has_material,
        reset=False,
    )

    ############################################################################
    # 2.6 - Other material operators
    ############################################################################

    #Unwrap a model with the basic method
    TESTS.add_operator(
        name="unwrap",
        operator="unwrap",
        args={"method":"basic"},
        before=create_suzanne,
        after=assert_suzanne_is_unwrapped,
    )

    #Unwrap a model with the smart uv project
    TESTS.add_operator(
        name="unwrap",
        operator="unwrap",
        args={"method":"smart"},
        before=create_suzanne,
        after=assert_suzanne_is_unwrapped,
    )

    #Unwrap a model with the "smarter" UV project
    TESTS.add_operator(
        name="unwrap",
        operator="unwrap",
        args={"method":"smarter"},
        before=create_suzanne,
        after=assert_suzanne_is_unwrapped,
    )

    #Add an empty PBR material to suzanne
    TESTS.add_operator(
        name="empty_material",
        operator="create_empty_material",
        before=create_suzanne,
        after=assert_suzanne_has_material,
    )

    #Assign an albedo texture
    TESTS.add_operator(
        name="assign_albedo",
        operator="assign_texture",
        args={"slot":"albedo", "filepath":os.path.join(os.path.dirname(__file__),"stick_albedo.jpg")},
        reset=False,
    )

    #Assign a normal map
    TESTS.add_operator(
        name="assign_normals",
        operator="assign_texture",
        args={"slot":"normal", "filepath":os.path.join(os.path.dirname(__file__),"stick_normals.jpg")},
        reset=False,
    )

    ############################################################################
    # 2.7 - Texture baking (mixing everything)
    ############################################################################

    #Remesh suzanne
    TESTS.add_operator(
        name="bake_textures",
        operator="bake_textures",
        args={
            "filepath":os.path.dirname(__file__),
            "resolution": 64,
            "imgFormat": "PNG",
            "bake_albedo": True,
            "bake_geometry": True,
            "bake_surface": True,
            "bake_roughness": True,
            "bake_metallic": True
        },
        before=prepare_for_baking,
        after=assert_baked_textures,
        reset=False,
    )

    ############################################################################
    # 2.8 - Export operators
    ############################################################################

    #Export an orthoview
    #Not available as blender window needs to be open to have an opengl context
    """
    TESTS.add_operator(
        name="export_orthoview",
        operator="export_orthoview",
        args={"filepath":os.path.join(os.path.dirname(__file__),"orthoview.png")},
        before=create_suzanne,
        after=assert_orthoview_created,
    )
    """

    ############################################################################
    # 2.9 - Other operators (.mesh file format and future operators)
    ############################################################################

    #Exports suzanne as a .mesh
    TESTS.add_operator(
        name="export_mesh",
        operator="export_mesh",
        args={"filepath":os.path.join(os.path.dirname(__file__),"suzanne.mesh")},
        before=create_suzanne,
        after=assert_mesh_file_created,
    )

    #Imports suzanne .mesh file
    TESTS.add_operator(
        name="import_mesh",
        operator="import_mesh",
        args={"filepath":os.path.join(os.path.dirname(__file__),"cube.mesh")},
        after=assert_cube_read
    )

    ############################################################################
    # 3 - Run the tests and exit
    ############################################################################
    TESTS.run()
    err = TESTS.report()
    sys.exit(err)
