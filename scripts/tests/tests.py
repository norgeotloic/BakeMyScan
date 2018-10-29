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

    def create_suzanne():
        bpy.ops.mesh.primitive_monkey_add()
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels = 2
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")
        bpy.context.active_object.select=True
    def empty_material_library():
        bpy.types.Scene.pbrtextures = {}
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

    #Import multiple versions of the cube
    TESTS.add_operator(
        name="import_obj",
        operator="import_scan",
        args = {"filepath": os.path.join(os.path.dirname(__file__), "cube.obj")},
        after = assert_model_imported
    )
    TESTS.add_operator(
        name="import_ply",
        operator="import_scan",
        args = {"filepath": os.path.join(os.path.dirname(__file__), "cube.ply")},
        after = assert_model_imported
    )
    TESTS.add_operator(
        name="import_stl",
        operator="import_scan",
        args = {"filepath": os.path.join(os.path.dirname(__file__), "cube.stl")},
        after = assert_model_imported
    )
    TESTS.add_operator(
        name="import_fbx",
        operator="import_scan",
        args = {"filepath": os.path.join(os.path.dirname(__file__), "cube.fbx")},
        after = assert_model_imported
    )
    TESTS.add_operator(
        name="import_dae",
        operator="import_scan",
        args = {"filepath": os.path.join(os.path.dirname(__file__), "cube.dae")},
        after = assert_model_imported
    )
    TESTS.add_operator(
        name="import_x3d",
        operator="import_scan",
        args = {"filepath": os.path.join(os.path.dirname(__file__), "cube.x3d")},
        after = assert_model_imported
    )

    #Clean the object
    TESTS.add_operator(
        name="preprocessing",
        operator="clean_object",
        reset=False
    )

    #Internal remeshing methods
    TESTS.add_operator(
        name="remesh_decimate",
        operator="remesh_decimate",
        before=create_suzanne,
        after=assert_suzanne_remeshed,
        reset=True,
        args={"limit":300}
    )
    TESTS.add_operator(
        name="remesh_quads",
        operator="remesh_quads",
        before=create_suzanne,
        after=assert_suzanne_remeshed,
        reset=True,
        args={"ratio":0.01, "smooth":2}
    )
    TESTS.add_operator(
        name="remesh_iterative",
        operator="remesh_iterative",
        before=create_suzanne,
        after=assert_suzanne_remeshed,
        reset=True,
        args={"limit":500}
    )

    #External remeshing methods
    TESTS.add_operator(
        name="remesh_mmgs",
        operator="remesh_mmgs",
        before=create_suzanne,
        after=assert_suzanne_remeshed,
        reset=True,
        args={"smooth":True, "hausd":0.01}
    )
    TESTS.add_operator(
        name="remesh_instant",
        operator="remesh_instant",
        before=create_suzanne,
        after=assert_suzanne_remeshed,
        reset=True,
        args={"interactive":False, "method":"faces", "facescount":1000}
    )
    TESTS.add_operator(
        name="remesh_meshlab",
        operator="remesh_meshlab",
        before=create_suzanne,
        after=assert_suzanne_remeshed,
        reset=True,
        args={"facescount":1500}
    )

    #Interact with the material library
    TESTS.add_operator(
        name="create_library",
        operator="create_library",
        args={"filepath":os.path.dirname(__file__)},
        after=assert_pbr_library_non_empty,
        reset=True
    )
    TESTS.add_operator(
        name="material_from_library",
        operator="material_from_library",
        args={"enum":"stick"},
        before=create_suzanne,
        after=assert_suzanne_has_material,
        reset=False,
    )
    TESTS.add_operator(
        name="save_json",
        operator="save_json_library",
        args={"filepath":os.path.join(os.path.dirname(__file__),"test.json")},
        after=assert_json_non_empty,
        reset=False
    )
    TESTS.add_operator(
        name="load_json",
        operator="load_json_library",
        args={"filepath":os.path.join(os.path.dirname(__file__),"test.json")},
        before=empty_material_library,
        after=assert_pbr_library_non_empty,
        reset=False
    )
    TESTS.add_operator(
        name="material_from_json",
        operator="material_from_library",
        args={"enum":"stick"},
        before=create_suzanne,
        after=assert_suzanne_has_material,
        reset=False,
    )

    #Other material operations
    TESTS.add_operator(
        name="unwrap",
        operator="unwrap",
        args={"method":"smarter"},
        before=create_suzanne,
        after=assert_suzanne_is_unwrapped,
    )
    TESTS.add_operator(
        name="empty_material",
        operator="create_empty_material",
        before=create_suzanne,
        after=assert_suzanne_has_material,
    )
    TESTS.add_operator(
        name="assign_albedo",
        operator="assign_texture",
        args={"slot":"albedo", "filepath":os.path.join(os.path.dirname(__file__),"stick_albedo.jpg")},
        reset=False,
    )
    TESTS.add_operator(
        name="assign_normals",
        operator="assign_texture",
        args={"slot":"normal", "filepath":os.path.join(os.path.dirname(__file__),"stick_normals.jpg")},
        reset=False,
    )

    #Baking operations

    #Run tests
    TESTS.run()
    err = TESTS.report()
    sys.exit(err)
