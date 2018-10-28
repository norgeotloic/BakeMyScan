import bpy
from   bpy_extras.io_utils import ImportHelper
import os

class import_scan(bpy.types.Operator, ImportHelper):
    bl_idname = "bakemyscan.import_scan"
    bl_label  = "Import your scan"
    bl_options = {"REGISTER", "UNDO"}
    filter_glob = bpy.props.StringProperty(
        default="*.obj;*.ply;*.stl;*.fbx;*.dae;*.x3d;*.wrl",
        options={'HIDDEN'},
    )

    @classmethod
    def poll(cls, context):
        #Object mode
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
