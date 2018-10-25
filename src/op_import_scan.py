import bpy
from   bpy_extras.io_utils import ImportHelper
import os
import addon_utils

from . import fn_nodes
from . import fn_match

class import_scan(bpy.types.Operator, ImportHelper):
    bl_idname = "bakemyscan.import_scan"
    bl_label  = "Import your scan"
    bl_options = {"REGISTER", "UNDO"}
    filter_glob = bpy.props.StringProperty(
        default="*.obj;*.ply;*.stl;*.fbx;*.dae;*.x3d;*.wrl",
        options={'HIDDEN'},
    )

    centerscale = bpy.props.BoolProperty(name="centerscale", description="Scale and center", default=True)
    clean       = bpy.props.BoolProperty(name="clean", description="Clean mesh (normals, sharp, duplicates...)", default=True)
    rmmaterial  = bpy.props.BoolProperty(name="rmmaterial", description="Empty material", default=True)
    manifold    = bpy.props.BoolProperty(name="manifold", description="Make manifold", default=False)

    @classmethod
    def poll(cls, context):
        if context.mode!="OBJECT":
            return 0
        return 1

    def execute(self, context):

        #Get the model path
        path = self.properties.filepath

        #Check that it is valid, and make it absolute to avoid any problem
        if not os.path.exists(path):
            return {'CANCELLED'}
        path = os.path.abspath(path)

        #Get the name of the model and its extension
        filename = os.path.basename(path)
        name, ext = os.path.splitext(filename)
        name, ext = name.lower(), ext.lower()

        #Get a list of the current objects in the scene, to remove the unused ones later
        oldObjects = [o for o in bpy.data.objects]

        #Import the object with the appropriate function
        if ext==".obj":
            bpy.ops.import_scene.obj(filepath=path)
        elif ext==".ply":
            bpy.ops.import_mesh.ply(filepath=path)
        elif ext==".stl":
            bpy.ops.import_mesh.stl(filepath=path)
        elif ext==".fbx":
            bpy.ops.import_scene.fbx(filepath=path)
        elif ext==".dae":
            bpy.ops.wm.collada_import(filepath=path)
        elif ext==".wrl" or ext==".x3d":
            bpy.ops.import_scene.x3d(filepath=path)
        else:
            return {'CANCELLED'}

        #Remove the new objects which are not a mesh
        newObjects = [o for o in bpy.data.objects if o not in oldObjects]
        for o in newObjects:
            if o.type != "MESH":
                bpy.data.objects.remove(o)
        newObjects = [o for o in bpy.data.objects if o not in oldObjects]

        #Don't treat the case in which there are multiple meshes
        obj = newObjects[0]

        #Select the new mesh, and make it the active object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        context.scene.objects.active = obj

        #Remove the material if one was assigned
        if self.rmmaterial:
            if len(obj.material_slots)>0:
                for slot in obj.material_slots:
                    if slot.material is not None:
                        slot.material = None

        #Clear the custom split normals, sharp edges, doubles and loose
        if self.clean:
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.mark_sharp(clear=True)
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
            bpy.ops.mesh.remove_doubles()
            bpy.ops.mesh.delete_loose()
            bpy.ops.object.editmode_toggle()

        #Clean the problematic normals: non manifolds and smooth
        if self.manifold:
            addon_utils.enable("object_print3d_utils")
            bpy.ops.mesh.print3d_clean_non_manifold()
            bpy.ops.object.modifier_add(type='SMOOTH')
            bpy.context.object.modifiers["Smooth"].iterations = 1
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Smooth")

        #Center and scale it to one
        if self.centerscale:
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
            s = 1.0/(max(max(obj.dimensions[0], obj.dimensions[1]), obj.dimensions[2]))
            obj.scale = [s,s,s]
            bpy.ops.object.transform_apply(location=False, rotation=True)

        #Zoom on it
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                override = {'area': area, 'region': area.regions[-1]}
                bpy.ops.view3d.view_selected(override, use_all_regions=False)

        #Give it the name of the file
        obj.name = name

        return{'FINISHED'}

def register() :
    bpy.utils.register_class(import_scan)

def unregister() :
    bpy.utils.unregister_class(import_scan)
