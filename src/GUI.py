import bpy

class BakeMyScanPanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "BakeMyScan"
    bl_options     = {"DEFAULT_CLOSED"}
    bl_context     = "objectmode"

class ImportPanel(BakeMyScanPanel):
    bl_label       = "Import"
    def draw(self, context):
        self.layout.operator("bakemyscan.import_scan",  icon="IMPORT",       text="Import")
        self.layout.operator("bakemyscan.clean_object", icon="PARTICLEMODE", text="Pre-process")

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
class MaterialPanel(BakeMyScanPanel):
    bl_label       = "Materials"

    @classmethod
    def poll(self, context):
        #Render engine must be cycles
        if bpy.context.scene.render.engine!="CYCLES":
            return 0
        return 1

    def draw(self, context):

        self.layout.label("Material from scratch")
        self.layout.operator("bakemyscan.create_empty_material", icon="MATERIAL", text="New empty material")
        self.layout.operator("bakemyscan.assign_texture", icon="TEXTURE",  text="Assign PBR textures")

        self.layout.label("Material from texture")
        self.layout.operator("bakemyscan.material_from_texture", icon="MATERIAL",  text="Load material from texture")

        self.layout.label("PBR library")
        self.layout.prop(context.scene.textures_path, "texturepath", text="Path", icon="FILE_FOLDER")
        self.layout.operator("bakemyscan.load_json_library",     icon="IMPORT",   text="Load from .JSON")
        self.layout.operator("bakemyscan.save_json_library",     icon="EXPORT",   text="Save to .JSON")
        self.layout.operator("bakemyscan.material_from_library", icon="MATERIAL", text="Load material from library")

class RemeshPanel(BakeMyScanPanel):
    bl_label       = "Remesh"

    def draw(self, context):
        self.layout.label("Triangles")
        self.layout.operator("bakemyscan.remesh_decimate",   icon="MOD_DECIM", text="Simple decimate")
        self.layout.operator("bakemyscan.remesh_iterative",  icon="MOD_DECIM", text="Iterative method")
        self.layout.operator("bakemyscan.remesh_mmgs",       icon_value=bpy.types.Scene.custom_icons["mmg"].icon_id, text="MMGS")
        self.layout.operator("bakemyscan.remesh_meshlab",    icon_value=bpy.types.Scene.custom_icons["meshlab"].icon_id, text="Meshlab")
        self.layout.label("Quadrilaterals")
        self.layout.operator("bakemyscan.remesh_quads",      icon="MOD_DECIM", text='"Dirty" quads')
        self.layout.operator("bakemyscan.remesh_instant",    icon_value=bpy.types.Scene.custom_icons["instant"].icon_id, text="InstantMeshes")
        self.layout.operator("bakemyscan.remesh_quadriflow", icon="MOD_DECIM", text="Quadriflow")
        self.layout.label("Post-process")
        self.layout.operator("bakemyscan.unwrap",            icon="GROUP_UVS",  text="Unwrap")
        self.layout.operator("bakemyscan.symetrize",         icon="MOD_MIRROR", text='Symmetry')
        self.layout.operator("bakemyscan.relax",             icon="MOD_SMOKE",  text='Relax!')
class RemeshFromSculptPanel(bpy.types.Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "Tools"
    bl_label       = "BakeMyScan Remesh"
    bl_context     = "sculpt_mode"
    bl_options     = {"DEFAULT_CLOSED"}

    def draw(self, context):
        self.layout.label("Triangles")
        self.layout.operator("bakemyscan.remesh_decimate",   icon="MOD_DECIM", text="Simple decimate")
        self.layout.operator("bakemyscan.remesh_iterative",  icon="MOD_DECIM", text="Iterative method")
        self.layout.operator("bakemyscan.remesh_mmgs",       icon_value=bpy.types.Scene.custom_icons["mmg"].icon_id, text="MMGS")
        self.layout.operator("bakemyscan.remesh_meshlab",    icon_value=bpy.types.Scene.custom_icons["meshlab"].icon_id, text="Meshlab")
        self.layout.label("Quadrilaterals")
        self.layout.operator("bakemyscan.remesh_quads",      icon="MOD_DECIM", text='"Dirty" quads')
        self.layout.operator("bakemyscan.remesh_instant",    icon_value=bpy.types.Scene.custom_icons["instant"].icon_id, text="InstantMeshes")
        self.layout.operator("bakemyscan.remesh_quadriflow", icon="MOD_DECIM", text="Quadriflow")

class BakingPanel(BakeMyScanPanel):
    bl_label       = "Baking"

    @classmethod
    def poll(self, context):
        #Render engine must be cycles
        if bpy.context.scene.render.engine!="CYCLES":
            return 0
        return 1

    def draw(self, context):
        self.layout.operator("bakemyscan.bake_textures",         icon="TEXTURE", text="Textures to textures")
        self.layout.operator("bakemyscan.bake_to_vertex_colors", icon="COLOR", text="Albedo to vertex color")

class ExportPanel(BakeMyScanPanel):
    bl_label       = "Export"

    def draw(self, context):
        self.layout.operator("bakemyscan.export",                  icon="EXPORT", text="Export model and textures")
        self.layout.operator("bakemyscan.export_orthoview",        icon="RENDER_STILL", text="Ortho View")

def setworldintensity(self, context):
    bpy.data.worlds['World'].node_tree.nodes["Background"].inputs[1].default_value = self.intensity
    return None
class IntensityProperty(bpy.types.PropertyGroup):
    intensity =  bpy.props.FloatProperty(name="intensity", description="HDRI intensity", default=1, min=0., max=10000., update=setworldintensity)
class ExperimentalPanel(BakeMyScanPanel):
    """Creates a Panel in the Object properties window"""
    bl_label       = "Experimental"

    @classmethod
    def poll(self, context):
        #Render engine must be cycles
        if bpy.context.scene.render.engine!="CYCLES":
            return 0
        #There must be a world called "World"
        if bpy.data.worlds.get("World") is None:
            return 0
        return 1

    def draw(self, context):
        layout = self.layout
        layout.label('HDRIs "shortcut"')
        #HDRI
        wm = context.window_manager
        row = layout.row()
        row.prop(wm, "my_previews_dir")
        row = layout.row()
        row.template_icon_view(wm, "my_previews")
        layout.prop(context.scene.intensity, "intensity", text="HDRI intensity")

        #Remove all but selected
        layout.label('Cleanup some data')
        layout.operator("bakemyscan.remove_all_but_selected", icon="ERROR", text="Clean non selected data")

class AboutPanel(BakeMyScanPanel):
    bl_label       = "About"

    def draw(self, context):
        self.layout.label("BakeMyScan")
        self.layout.operator("wm.url_open", text="bakemyscan.org", icon_value=bpy.types.Scene.custom_icons["bakemyscan"].icon_id).url = "http://bakemyscan.org"
        self.layout.operator("wm.url_open", text="Github",         icon_value=bpy.types.Scene.custom_icons["github"].icon_id).url = "http://github.com/norgeotloic/BakeMyScan"
        self.layout.operator("wm.url_open", text="Build status",   icon_value=bpy.types.Scene.custom_icons["travis"].icon_id).url = "https://travis-ci.org/norgeotloic/BakeMyScan"

        self.layout.label("External software")
        self.layout.operator("wm.url_open", text="MMGtools", icon_value=bpy.types.Scene.custom_icons["mmg"].icon_id).url = "https://www.mmgtools.org/"
        self.layout.operator("wm.url_open", text="Instant Meshes", icon_value=bpy.types.Scene.custom_icons["instant"].icon_id).url = "https://github.com/wjakob/instant-meshes"
        self.layout.operator("wm.url_open", text="Quadriflow", icon="MOD_DECIM").url = "https://github.com/hjwdzh/QuadriFlow"
        self.layout.operator("wm.url_open", text="Meshlab", icon_value=bpy.types.Scene.custom_icons["meshlab"].icon_id).url = "http://www.meshlab.net/"

        self.layout.label("Yours truly, Loïc")
        self.layout.operator("wm.url_open", text="Sketchfab", icon_value=bpy.types.Scene.custom_icons["sketchfab"].icon_id).url = "https://sketchfab.com/norgeotloic"
        self.layout.operator("wm.url_open", text="Tweeter",   icon_value=bpy.types.Scene.custom_icons["tweeter"].icon_id).url = "https://twitter.com/norgeotloic"
        self.layout.operator("wm.url_open", text="Donate", icon_value=bpy.types.Scene.custom_icons["donate"].icon_id).url = "http://bakemyscan.org/donate"


def register():
    bpy.utils.register_class(ImportPanel)
    bpy.utils.register_class(MaterialPanel)
    bpy.utils.register_class(RemeshPanel)
    bpy.utils.register_class(RemeshFromSculptPanel)
    bpy.utils.register_class(BakingPanel)
    bpy.utils.register_class(ExportPanel)
    bpy.utils.register_class(ExperimentalPanel)
    bpy.utils.register_class(AboutPanel)
    #Add the custom intensity slider
    bpy.utils.register_class(IntensityProperty)
    bpy.types.Scene.intensity = bpy.props.PointerProperty(type=IntensityProperty)
    #Add the custom path to texture library
    bpy.utils.register_class(MyCustomProperties)
    bpy.types.Scene.textures_path = bpy.props.PointerProperty(type=MyCustomProperties)

def unregister():
    bpy.utils.unregister_class(ImportPanel)
    bpy.utils.unregister_class(MaterialPanel)
    bpy.utils.unregister_class(RemeshPanel)
    bpy.utils.unregister_class(RemeshFromSculptPanel)
    bpy.utils.unregister_class(BakingPanel)
    bpy.utils.unregister_class(ExportPanel)
    bpy.utils.unregister_class(ExperimentalPanel)
    bpy.utils.unregister_class(AboutPanel)
    #Clear the custom intensity slider
    bpy.utils.unregister_class(IntensityProperty)
    del bpy.types.Scene.intensity
    #Clear the custom path to textures
    bpy.utils.unregister_class(MyCustomProperties)
    del bpy.types.Scene.textures_path
