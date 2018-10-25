import bpy

class ImportPanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "BakeMyScan"
    bl_label       = "Import"

    def draw(self, context):
        self.layout.operator("bakemyscan.import_scan",           icon="IMPORT",       text="Import")
        self.layout.operator("bakemyscan.create_empty_material", icon="MATERIAL",     text="Assign an empty material")
        self.layout.operator("bakemyscan.assign_texture",        icon="TEXTURE",      text="Assign PBR textures")
        self.layout.operator("bakemyscan.export_orthoview",      icon="RENDER_STILL", text="Ortho View")

class RemeshPanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "BakeMyScan"
    bl_label       = "Remesh"

    def draw(self, context):
        self.layout.operator("bakemyscan.remesh_decimate",   icon="MOD_DECIM", text="Simple decimate")
        self.layout.operator("bakemyscan.remesh_quads",      icon="MOD_DECIM", text="Naive quads")
        self.layout.operator("bakemyscan.remesh_iterative",  icon="MOD_DECIM", text="Iterative method")
        self.layout.operator("bakemyscan.remesh_mmgs",       icon="MOD_DECIM", text="MMGS")
        self.layout.operator("bakemyscan.remesh_meshlab",    icon="MOD_DECIM", text="Meshlab")
        self.layout.operator("bakemyscan.remesh_instant",    icon="MOD_DECIM", text="InstantMeshes")
        self.layout.operator("bakemyscan.remesh_quadriflow", icon="MOD_DECIM", text="Quadriflow")


class TexturePanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "BakeMyScan"
    bl_label       = "Texture"

    def draw(self, context):
        self.layout.prop(context.scene.textures_path, "texturepath", text="Path", icon="TEXTURE")
        self.layout.operator("bakemyscan.import_material", icon="MATERIAL", text="Import material")

class BakingPanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "BakeMyScan"
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
    bpy.types.Scene.textures_path = bpy.props.PointerProperty(type=MyCustomProperties)
    bpy.utils.register_class(ImportPanel)
    bpy.utils.register_class(RemeshPanel)
    bpy.utils.register_class(TexturePanel)
    bpy.utils.register_class(BakingPanel)
def unregister():
    bpy.utils.unregister_class(MyCustomProperties)
    del bpy.types.Scene.textures_path
    bpy.utils.unregister_class(ImportPanel)
    bpy.utils.unregister_class(RemeshPanel)
    bpy.utils.unregister_class(TexturePanel)
    bpy.utils.unregister_class(BakingPanel)
