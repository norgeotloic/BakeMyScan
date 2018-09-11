import bpy

class ImportPanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "NGL"
    bl_label       = "Import"

    def draw(self, context):
        self.layout.operator("bakemyscan.import_scan",      icon="IMPORT",       text="Import")
        self.layout.operator("bakemyscan.export_orthoview", icon="RENDER_STILL", text="Ortho View")

class RemeshPanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "NGL"
    bl_label       = "Remesh"

    def draw(self, context):
        self.layout.operator("bakemyscan.remesh_iterative", icon="MOD_DECIM", text="Decimate")
        self.layout.operator("bakemyscan.remesh_mmgs",      icon="MOD_DECIM", text="MMGS")


class TexturePanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "NGL"
    bl_label       = "Texture"

    def draw(self, context):
        self.layout.prop(context.scene.tototo, "texturepath", text="Path", icon="TEXTURE")
        self.layout.operator("bakemyscan.import_material", icon="MATERIAL", text="Import material")

class BakingPanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "NGL"
    bl_label       = "Baking"

    def draw(self, context):
        self.layout.operator("bakemyscan.bake_textures", icon="OUTLINER_OB_CAMERA", text="Bake textures")
        self.layout.operator("bakemyscan.remove_all_but_selected",  icon="ERROR", text="Clean not used")
        self.layout.operator("bakemyscan.export_fbx",    icon="EXPORT", text="Export to FBX")

def updatepath(self, context):
    print(self.texturepath)
    bpy.ops.bakemyscan.list_textures(filepath=self.texturepath)
    return None
class MyCustomProperties(bpy.types.PropertyGroup):
    texturepath =  bpy.props.StringProperty(
        name="texturepath",
        description="Filepath used for importing the file",
        maxlen=1024,
        subtype='DIR_PATH',
        update=updatepath
    )

def register():
    bpy.utils.register_class(MyCustomProperties)
    bpy.types.Scene.tototo = bpy.props.PointerProperty(type=MyCustomProperties)
    bpy.utils.register_class(ImportPanel)
    bpy.utils.register_class(RemeshPanel)
    bpy.utils.register_class(TexturePanel)
    bpy.utils.register_class(BakingPanel)
def unregister():
    bpy.utils.unregister_class(MyCustomProperties)
    del bpy.types.Scene.tototo
    bpy.utils.unregister_class(ImportPanel)
    bpy.utils.unregister_class(RemeshPanel)
    bpy.utils.unregister_class(TexturePanel)
    bpy.utils.unregister_class(BakingPanel)
