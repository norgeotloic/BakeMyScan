import bpy
from bpy_extras.io_utils import ExportHelper
import os

class export_blend(bpy.types.Operator, ExportHelper):
    bl_idname = "bakemyscan.export_blend"
    bl_label  = "Exports the model to a .blend"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".blend"
    filter_glob = bpy.props.StringProperty(default="*.blend", options={'HIDDEN'})

    filepath = bpy.props.StringProperty(
        name="Export blend file",
        description="New blend file to export to",
        maxlen= 1024,
        default= ""
    )

    def execute(self, context):
        obj = context.active_object

        #Get the parameters
        directory = os.path.dirname(os.path.abspath(self.properties.filepath))
        name      = os.path.splitext(os.path.basename(os.path.abspath(self.properties.filepath)))[0]
        print(directory, name)

        #Remove all but the selected object
        for o in bpy.data.objects:
            if o!=obj:
                bpy.data.objects.remove(o)

        #Unused materials
        for mat in bpy.data.materials:
            if mat.users==0 or mat != obj.material_slots[0].material:
                bpy.data.materials.remove(mat)
        #Unused textures
        for tex in bpy.data.textures:
            if tex.users==0:
                bpy.data.textures.remove(tex)
        #Unused images
        for img in bpy.data.images:
            if img.users==0:
                bpy.data.images.remove(img)

        #Rename the model and the material
        obj.name = name
        obj.material_slots[0].material.name = name

        #Pack all into file
        bpy.ops.file.pack_all()

        #Save as the blend file, and remove the old one
        if os.path.exists(self.properties.filepath):
            os.remove(self.properties.filepath)
        bpy.ops.wm.save_as_mainfile(filepath=self.properties.filepath, compress=True)

        return {'FINISHED'}

def register() :
    bpy.utils.register_class(export_blend)

def unregister() :
    bpy.utils.unregister_class(export_blend)
