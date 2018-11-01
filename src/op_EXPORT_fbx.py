import bpy
from bpy_extras.io_utils import ExportHelper
import os
import shutil

class export_fbx(bpy.types.Operator, ExportHelper):
    bl_idname = "bakemyscan.export_fbx"
    bl_label  = "Exports the model to a .fbx"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".fbx"
    filter_glob = bpy.props.StringProperty(default="*.fbx", options={'HIDDEN'})
    filepath = bpy.props.StringProperty(
        name="Export fbx file",
        description="New fbx file to export to",
        maxlen= 1024,
        default= ""
    )

    @classmethod
    def poll(self, context):
        #Render engine must be cycles
        if bpy.context.scene.render.engine!="CYCLES":
            return 0
        #Must have only one selected object
        if len(context.selected_objects)!=1:
            return 0
        #If no object is active
        if context.active_object is None:
            return 0
        #If something other than a MESH is selected
        for o in context.selected_objects:
            if o.type != "MESH":
                return 0
        #Each material must be not None and have nodes
        if context.active_object.active_material is None:
                return 0
        if context.active_object.active_material.use_nodes == False:
            return 0
        if context.mode!="OBJECT":
            return 0
        return 1

    def execute(self, context):
        obj = context.active_object

        #Get the parameters
        directory = os.path.dirname(os.path.abspath(self.properties.filepath))
        name      = os.path.splitext(os.path.basename(os.path.abspath(self.properties.filepath)))[0]

        #function to recursively save all images in a tree
        def save_images(tree, directory, name):
            for node in tree.nodes:
                if node.type=="TEX_IMAGE":
                    img = node.image
                    if img is not None:
                        path = os.path.abspath(os.path.join(directory, name + "_" + img.name.split("_")[-1].split(".")[0]))
                        #If the image is a file
                        if img.source=="FILE":
                            img.save()
                            shutil.copyfile(img.filepath_raw, path)
                            #os.remove(node.image.filepath_raw)
                        else:
                            img.filepath_raw = path
                            img.save()
                elif node.type == "GROUP":
                    save_images(node.node_tree, directory, name)

        #Move and update the textures
        bpy.ops.export_scene.fbx(filepath = self.filepath, use_selection=True)
        save_images(obj.active_material.node_tree, directory, name)

        return {'FINISHED'}

def register() :
    bpy.utils.register_class(export_fbx)

def unregister() :
    bpy.utils.unregister_class(export_fbx)
