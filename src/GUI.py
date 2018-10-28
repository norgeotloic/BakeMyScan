import bpy

class ImportPanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "BakeMyScan"
    bl_label       = "Import"

    def draw(self, context):
        self.layout.operator("bakemyscan.import_scan",  icon="IMPORT",       text="Import")
        self.layout.operator("bakemyscan.clean_object", icon="PARTICLEMODE", text="Clean")

class MaterialPanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "BakeMyScan"
    bl_label       = "Material"

    def draw(self, context):
        #Manage a material library
        self.layout.label("PBR library")
        self.layout.prop(context.scene.textures_path, "texturepath", text="Textures path", icon="TEXTURE")
        self.layout.operator("bakemyscan.load_json_library",     icon="IMPORT",   text="Load a JSON library")
        self.layout.operator("bakemyscan.save_json_library",     icon="EXPORT",   text="Save library to JSON")
        self.layout.operator("bakemyscan.material_from_library", icon="MATERIAL", text="Load material from library")
        #Other operations on materials
        self.layout.label("Other operations")
        self.layout.operator("bakemyscan.unwrap", icon="GROUP_UVS", text="UV Unwrapping")
        self.layout.operator("bakemyscan.create_empty_material", icon="MATERIAL", text="New empty material")
        self.layout.operator("bakemyscan.assign_texture", icon="TEXTURE",  text="Assign PBR textures")
        self.layout.operator("bakemyscan.material_from_texture", icon="TEXTURE",  text="Load material from texture")


def updatepath(self, context):
    print(self.texturepath)
    bpy.ops.bakemyscan.create_library(filepath=self.texturepath)
    return None
class MyCustomProperties(bpy.types.PropertyGroup):
    texturepath =  bpy.props.StringProperty(
        name="texturepath",
        description="Filepath used for importing the file",
        maxlen=1024,
        subtype='DIR_PATH',
        update=updatepath
    )

class RemeshPanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "BakeMyScan"
    bl_label       = "Remesh"

    def draw(self, context):
        self.layout.label("Internal")
        self.layout.operator("bakemyscan.remesh_decimate",   icon="MOD_DECIM", text="Simple decimate")
        self.layout.operator("bakemyscan.remesh_quads",      icon="MOD_DECIM", text="Naive quads")
        self.layout.operator("bakemyscan.remesh_iterative",  icon="MOD_DECIM", text="Iterative method")
        self.layout.label("External")
        self.layout.operator("bakemyscan.remesh_mmgs",       icon_value=bpy.types.Scene.custom_icons["mmg"].icon_id, text="MMGS")
        self.layout.operator("bakemyscan.remesh_meshlab",    icon_value=bpy.types.Scene.custom_icons["meshlab"].icon_id, text="Meshlab")
        self.layout.operator("bakemyscan.remesh_instant",    icon_value=bpy.types.Scene.custom_icons["instant"].icon_id, text="InstantMeshes")
        self.layout.operator("bakemyscan.remesh_quadriflow", icon="MOD_DECIM", text="Quadriflow")

class BakingPanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "BakeMyScan"
    bl_label       = "Baking"

    def draw(self, context):
        self.layout.operator("bakemyscan.bake_textures", icon="OUTLINER_OB_CAMERA", text="Bake textures")
        self.layout.operator("bakemyscan.bake_to_vertex_colors", icon="OUTLINER_OB_CAMERA", text="Bake textures")

class ExportPanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "BakeMyScan"
    bl_label       = "Export"

    def draw(self, context):
        self.layout.operator("bakemyscan.export_orthoview",      icon="RENDER_STILL", text="Ortho View")
        self.layout.operator("bakemyscan.remove_all_but_selected",  icon="ERROR", text="Clean not used")
        self.layout.operator("bakemyscan.export_fbx",    icon="EXPORT", text="Export to FBX")




def register():
    bpy.utils.register_class(MyCustomProperties)
    bpy.types.Scene.textures_path = bpy.props.PointerProperty(type=MyCustomProperties)
    bpy.utils.register_class(ImportPanel)
    bpy.utils.register_class(RemeshPanel)
    bpy.utils.register_class(MaterialPanel)
    bpy.utils.register_class(BakingPanel)
    bpy.utils.register_class(ExportPanel)
def unregister():
    bpy.utils.unregister_class(MyCustomProperties)
    del bpy.types.Scene.textures_path
    bpy.utils.unregister_class(ImportPanel)
    bpy.utils.unregister_class(RemeshPanel)
    bpy.utils.unregister_class(MaterialPanel)
    bpy.utils.unregister_class(BakingPanel)
    bpy.utils.unregister_class(ExportPanel)
