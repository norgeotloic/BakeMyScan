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
        self.layout.operator("bakemyscan.import_material", icon="TEXTURE",  text="Create PBR library")
        self.layout.operator("bakemyscan.import_material", icon="IMPORT",   text="Load a JSON library"))
        self.layout.operator("bakemyscan.import_material", icon="EXPORT",   text="Save library to JSON"))
        self.layout.operator("bakemyscan.import_material", icon="MATERIAL", text="Load material from library")
        #Other operations on materials
        self.layout.label("Other operations")
        self.layout.operator("bakemyscan.create_empty_material", icon="MATERIAL",     text="Assign an empty material")
        self.layout.operator("bakemyscan.assign_texture",        icon="TEXTURE",      text="Assign PBR textures")
        self.layout.operator("bakemyscan.assign_texture",        icon="TEXTURE",      text="Assign PBR textures")
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
    bpy.utils.register_class(TexturePanel)
    bpy.utils.register_class(BakingPanel)
def unregister():
    bpy.utils.unregister_class(MyCustomProperties)
    del bpy.types.Scene.textures_path
    bpy.utils.unregister_class(ImportPanel)
    bpy.utils.unregister_class(RemeshPanel)
    bpy.utils.unregister_class(TexturePanel)
    bpy.utils.unregister_class(BakingPanel)
