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

    imgFormat = bpy.props.EnumProperty(items= ( ('PNG', 'PNG', 'PNG'), ("JPEG", "JPEG", "JPEG")) , name="imgFormat", description="image format", default="JPEG")

    filepath = bpy.props.StringProperty(
        name="Export fbx file",
        description="New fbx file to export to",
        maxlen= 1024,
        default= ""
    )

    def execute(self, context):
        obj = context.active_object

        #Get the parameters
        directory = os.path.dirname(os.path.abspath(self.properties.filepath))
        name      = os.path.splitext(os.path.basename(os.path.abspath(self.properties.filepath)))[0]

        #
        def save_images(tree, directory, name, fmt):
            for node in tree.nodes:
                if node.type=="TEX_IMAGE":
                    if node.image is not None:
                        shutil.copyfile(node.image.filepath_raw, os.path.abspath(os.path.join(directory, name + "_" + node.image.name.split("_")[-1])))
                        os.remove(node.image.filepath_raw)
                elif node.type == "GROUP":
                    save_images(node.node_tree, directory, name, fmt)

        #Move and update the textures
        bpy.ops.export_scene.fbx(filepath = self.filepath, use_selection=True)
        mat = obj.material_slots[0].material
        save_images(mat.node_tree, directory, name, self.imgFormat)

        return {'FINISHED'}

def register() :
    bpy.utils.register_class(export_fbx)

def unregister() :
    bpy.utils.unregister_class(export_fbx)
