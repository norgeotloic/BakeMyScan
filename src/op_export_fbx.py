import bpy
from bpy_extras.io_utils import ExportHelper
import os

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
        print(directory, name)

        #Move and update the textures
        bpy.ops.export_scene.fbx(filepath = self.filepath, use_selection=True)
        mat = obj.material_slots[0].material
        for slot in mat.texture_slots:
            if slot is not None:
                if slot.texture is not None:
                    img = slot.texture.image
                    if img is not None:
                        img.name = name + "_" + img.name.split("_")[-1]
                        ext = '.jpg' if self.imgFormat == "JPEG" else ".png"
                        img.filepath_raw = os.path.join(directory, img.name + ext)
                        img.file_format = self.imgFormat
                        img.save()

        return {'FINISHED'}

def register() :
    bpy.utils.register_class(export_fbx)

def unregister() :
    bpy.utils.unregister_class(export_fbx)
