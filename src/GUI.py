import bpy
import os
from   bpy_extras.io_utils import ImportHelper

import addon_utils


class BakeMyScanPanel(bpy.types.Panel):
    """A base class for panels to inherit"""
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category    = "BakeMyScan"
    bl_options     = {"DEFAULT_CLOSED"}
    bl_context     = "objectmode"

class ScanningProperties(bpy.types.PropertyGroup):
    def create_images_variable(self, context):
        bpy.types.Scene.imgpaths = self.imgpaths
    imgpaths =  bpy.props.StringProperty(
        name="texturepath",
        description="Filepath used for importing the file",
        maxlen=1024,
        subtype='DIR_PATH',
        update = create_images_variable
    )
class ScanPanel(BakeMyScanPanel):
    """A panel for the scanning methods"""
    bl_label       = "Structure from Motion"
    def draw(self, context):
        box = self.layout
        box.label("Images directory")
        box.prop(context.scene.images_directory, "imgpaths", text="")
        box.label("Structure from motion")
        box.operator("bakemyscan.colmap_auto", icon="CAMERA_DATA", text="Colmap auto")
        box.operator("bakemyscan.colmap_openmvs", icon="CAMERA_DATA", text="Colmap + OpenMVS")

class ImportPanel(BakeMyScanPanel):
    """A panel for importing and pre-processing"""
    bl_label       = "Import / Export"
    def draw(self, context):
        self.layout.operator("bakemyscan.import_scan",  icon="IMPORT",       text="Import")
        self.layout.operator("bakemyscan.export",                  icon="EXPORT", text="Export model and textures")
        self.layout.operator("bakemyscan.export_orthoview",        icon="RENDER_STILL", text="Ortho View")
        self.layout.operator("bakemyscan.remove_all_but_selected", icon="ERROR", text="Clean non selected data")

class PipelinePanel(BakeMyScanPanel):
    bl_label = "Pipeline"
    def draw(self, context):
        self.layout.operator("bakemyscan.clean_object", icon="PARTICLEMODE", text="Pre-process")

        self.layout.label("Retopology")
        self.layout.operator("bakemyscan.full_pipeline", icon="MOD_DECIM", text="Remesh")
        self.layout.operator("bakemyscan.unwrap",            icon="GROUP_UVS",  text="Unwrap")

        self.layout.label("Post-process")
        self.layout.operator("bakemyscan.symetrize",         icon="MOD_MIRROR", text='Symmetry')
        self.layout.operator("bakemyscan.relax",             icon="MOD_SMOKE",  text='Relax!')
        self.layout.operator("bakemyscan.manifold",          icon="MOD_SMOKE",  text='Manifold')

        self.layout.label("Baking")
        self.layout.operator("bakemyscan.bake_textures",         icon="TEXTURE", text="Textures to textures")
        self.layout.operator("bakemyscan.bake_to_vertex_colors", icon="COLOR", text="Albedo to vertex color")

class MyCustomProperties(bpy.types.PropertyGroup):
    def updatepath(self, context):
        print(self.texturepath)
        bpy.ops.bakemyscan.create_library(filepath=self.texturepath)
        return None
    texturepath =  bpy.props.StringProperty(
        name="texturepath",
        description="Filepath used for importing the file",
        maxlen=1024,
        subtype='DIR_PATH',
        update=updatepath
    )

def clean(tree, type):
    GET = tree.nodes.get
    NEW = tree.links.new
    PR  = GET("BakeMyScan PBR")

    node = GET(type)
    if node is not None:

        if type=="albedo":
            if node.image is not None:
                if GET("delight") is not None:
                    NEW(GET(type).outputs["Color"], GET("delight").inputs["Color"])
                    NEW(GET("delight").outputs["Color"], GET("ao_mix").inputs[1])
                else:
                    NEW(GET(type).outputs["Color"], GET("ao_mix").inputs[1])
                NEW(GET("ao_mix").outputs["Color"], PR.inputs["Base Color"])
            else:
                for l in GET("ao_mix").inputs[1].links:
                    tree.links.remove(l)

        if type=="ao":
            if node.image is not None:
                NEW(GET(type).outputs["Color"], GET("ao_mix").inputs[2])
                NEW(GET("ao_mix").outputs["Color"], PR.inputs["Base Color"])
                """
                if GET("delight") is not None:
                    node2 = GET("delight").node_tree.nodes["ao"]
                    node2.image.filepath_raw = node.image.filepath_raw
                    node2.image.reload()
                """
            else:
                pass
                for l in GET("ao_mix").inputs[2].links:
                    tree.links.remove(l)

        if type=="normal":
            if node.image is not None:
                NEW(GET(type).outputs["Color"], GET("nmap").inputs["Color"])
            else:
                for l in GET("nmap").inputs["Color"].links:
                    tree.links.remove(l)

        if type=="height":
            if node.image is not None:
                NEW(GET(type).outputs["Color"], GET("bump").inputs["Height"])
            else:
                for l in GET("bump").inputs["Height"].links:
                    tree.links.remove(l)

        if type=="metallic":
            if node.image is not None:
                NEW(GET(type).outputs["Color"], PR.inputs["Metallic"])
            else:
                for l in PR.inputs["Metallic"].links:
                    tree.links.remove(l)

        if type=="roughness":
            if node.image is not None:
                NEW(GET(type).outputs["Color"], PR.inputs["Roughness"])
            else:
                for l in PR.inputs["Roughness"].links:
                    tree.links.remove(l)
def link_material(tree):
    clean(tree, "ao")
    clean(tree, "albedo")
    clean(tree, "normal")
    clean(tree, "height")
    clean(tree, "metallic")
    clean(tree, "roughness")
    pass


class MaterialProperties(bpy.types.PropertyGroup):
    def update_delight_invert(self, context):
        nodes = context.active_object.active_material.node_tree.nodes.get("PBR").node_tree.nodes
        nodes["delight"].inputs["Invert"].default_value = self.delight_invert_factor
        return None
    delight_invert_factor = bpy.props.FloatProperty(description="Inversion factor for delighting", default=0.3, min=0.,max=1., update=update_delight_invert)

    def update_delight_ao(self, context):
        nodes = context.active_object.active_material.node_tree.nodes.get("PBR").node_tree.nodes
        nodes["delight"].inputs["AO"].default_value = self.delight_ao_factor
        return None
    delight_ao_factor = bpy.props.FloatProperty(description="Ambient Occlusion factor for delighting", default=0.15, min=0.,max=1., update=update_delight_ao)

    def update_ao(self, context):
        nodes = context.active_object.active_material.node_tree.nodes.get("PBR").node_tree.nodes
        nodes["ao_mix"].inputs["Fac"].default_value = self.ao_factor
        return None
    ao_factor = bpy.props.FloatProperty(description="Ambient Occlusion factor", default=0.5, min=0.,max=1., update=update_ao)

    def update_UV_scale(self, context):
        nodes = context.active_object.active_material.node_tree.nodes
        group = [g for g in nodes if g.type=="GROUP"][0]
        group.inputs["UV scale"].default_value = self.uv_scale
        return None
    uv_scale = bpy.props.FloatProperty(description="UV scale", default=1, min=0.,max=1000., update=update_UV_scale)

    def update_height(self, context):
        nodes = context.active_object.active_material.node_tree.nodes
        group = [g for g in nodes if g.type=="GROUP"][0]
        group.inputs["Height"].default_value = self.height
        return None
    height = bpy.props.FloatProperty(description="Height", default=0.005, min=-1.,max=1., update=update_height)

    def toggle_delight(self, context):
        if self.delight:
            bpy.ops.bakemyscan.delight()
        else:
            nodes = context.active_object.active_material.node_tree.nodes.get("PBR").node_tree.nodes
            nodes.remove(nodes.get("delight"))

    delight = bpy.props.BoolProperty(description="Delighting", default=False, update=toggle_delight)

class MaterialPanel(BakeMyScanPanel):
    bl_label       = "Material / Textures"

    @classmethod
    def poll(self, context):
        #Render engine must be cycles
        if bpy.context.scene.render.engine!="CYCLES":
            return 0
        return 1

    def check(self, context):
        return True

    def draw(self, context):

        def create_image_UI(layout, name, node):
            row = layout.row()
            lab = row.row()
            lab.scale_x = 1.0
            lab.label(name)
            sub=row.row()
            sub.scale_x=4.0
            sub.template_ID(data=node,property="image",open="image.open")

        #Do we display the textures and delighting options?
        display = False
        nodes   = None
        ob = context.active_object
        if ob is not None and len(context.selected_objects)>0:
            if len(ob.material_slots)>0:
                mat = ob.active_material
                if mat is not None:
                    if mat.use_nodes:
                        groups = [g for g in mat.node_tree.nodes if g.type=="GROUP"]
                        if len(groups)==1:
                            if mat.node_tree.nodes.get("PBR") is not None:
                                nodes = mat.node_tree.nodes.get("PBR").node_tree.nodes
                                display = True

        #Display the material selector widget
        if ob is not None and len(context.selected_objects)>0:
            self.layout.template_ID(
                data=ob,
                property="active_material",
                new="bakemyscan.create_empty_material",
                open="bakemyscan.material_from_library"
            )

        if display:
            #Display the texture slots
            box = self.layout.box()
            create_image_UI(box, "Albedo", nodes["albedo"])
            create_image_UI(box, "AO", nodes["ao"])
            if nodes["ao"].image is not None:
                row = box.row()
                lab = row.row()
                lab.scale_x = 1.0
                lab.label("")
                sub=row.row()
                sub.scale_x=4.0
                sub.prop(context.scene.bakemyscan_properties, "ao_factor", text="Factor")
            create_image_UI(box, "Normal", nodes["normal"])
            create_image_UI(box, "Height", nodes["height"])
            create_image_UI(box, "Metallic", nodes["metallic"])
            create_image_UI(box, "Roughness", nodes["roughness"])

            #Delighting box
            if nodes.get("albedo") is not None:
                if nodes["albedo"].image is not None:
                    box = self.layout.box()
                    box.prop(context.scene.bakemyscan_properties, "delight", text="Delight")
                    if nodes.get("delight"):
                        box.prop(context.scene.bakemyscan_properties, "delight_invert_factor", text="Invert factor")
                        box.prop(context.scene.bakemyscan_properties, "delight_ao_factor", text="AO factor")

            #Correct the links in the material
            try:
                if bpy.context.space_data.viewport_shade != 'RENDERED':
                    link_material(ob.active_material.node_tree.nodes.get("PBR").node_tree)
            except:
                link_material(ob.active_material.node_tree.nodes.get("PBR").node_tree)

        else:
            #If there is a material, which comes from the library
            if len(ob.material_slots)>0:
                mat = ob.active_material
                if mat is not None:
                    if mat.use_nodes:
                        groups = [g for g in mat.node_tree.nodes if g.type=="GROUP"]
                        if len(groups)==1:
                            g = groups[0]
                            if "Height" in g.inputs and "UV scale" in g.inputs:
                                self.layout.prop(context.scene.bakemyscan_properties, "uv_scale", text="UV scale")
                                self.layout.prop(context.scene.bakemyscan_properties, "height",   text="Height")

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

class currentVersion(bpy.types.Operator):
    bl_idname = "bakemyscan.current_version"
    bl_label  = "Current version"
    @classmethod
    def poll(self, context):
        return 0

import asyncio
import requests
import functools
import json
async def do_request():
    loop     = asyncio.get_event_loop()
    future   = loop.run_in_executor(None, requests.get, 'https://api.github.com/repos/norgeotloic/BakeMyScan/releases')
    response = await future
    object = json.loads(response.text)
    bpy.types.Scene.newVersion = object[0]["tag_name"]
    for mod in addon_utils.modules():
        if mod.bl_info.get("name") == "BakeMyScan":
            bpy.types.Scene.currentVersion = ".".join([str(x) for x in mod.bl_info.get("version")])
            if bpy.types.Scene.currentVersion == bpy.types.Scene.newVersion:
                print("No new updates")
            else:
                print("Oh yeah, a new update!")

class checkUpdates(bpy.types.Operator):
    bl_idname = "bakemyscan.check_updates"
    bl_label  = "Check for updates"
    @classmethod
    def poll(self, context):
        return 1
    def execute(self, context):
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(do_request())
        if response is not None:

            return {"FINISHED"}
        else:
            return {"CANCELLED"}

class AboutPanel(BakeMyScanPanel):
    bl_label       = "Updates / Documentation"

    def draw(self, context):

        self.layout.operator("wm.url_open", text="bakemyscan.org", icon_value=bpy.types.Scene.custom_icons["bakemyscan"].icon_id).url = "http://bakemyscan.org"
        row = self.layout.row(align=True)
        row.operator("bakemyscan.check_updates", text='Check for updates', icon="FILE_REFRESH")
        for mod in addon_utils.modules():
            if mod.bl_info.get("name") == "BakeMyScan":
                row.operator("bakemyscan.current_version", icon="QUESTION", text='Version: %s' % ".".join([str(x) for x in mod.bl_info.get("version")]))

        self.layout.label("Development")
        self.layout.operator("wm.url_open", text="Github",         icon_value=bpy.types.Scene.custom_icons["github"].icon_id).url = "http://github.com/norgeotloic/BakeMyScan"
        self.layout.operator("wm.url_open", text="Build status",   icon_value=bpy.types.Scene.custom_icons["travis"].icon_id).url = "https://travis-ci.org/norgeotloic/BakeMyScan"
        self.layout.operator("wm.url_open", text="Roadmap",   icon_value=bpy.types.Scene.custom_icons["github"].icon_id).url = "http://github.com/norgeotloic/BakeMyScan/milestones"
        self.layout.operator("wm.url_open", text='"Blog"',    icon="WORDWRAP_ON").url = "http://bakemyscan.org/blog"

        self.layout.label("Social")
        self.layout.operator("wm.url_open", text="Sketchfab", icon_value=bpy.types.Scene.custom_icons["sketchfab"].icon_id).url = "https://sketchfab.com/norgeotloic"
        self.layout.operator("wm.url_open", text="Twitter",   icon_value=bpy.types.Scene.custom_icons["tweeter"].icon_id).url = "https://twitter.com/norgeotloic"
        self.layout.operator("wm.url_open", text="Youtube",   icon_value=bpy.types.Scene.custom_icons["youtube"].icon_id).url = "https://youtube.com/norgeotloic"

        self.layout.label("External software")
        self.layout.operator("wm.url_open", text="MMGtools", icon_value=bpy.types.Scene.custom_icons["mmg"].icon_id).url = "https://www.mmgtools.org/"
        self.layout.operator("wm.url_open", text="Instant Meshes", icon_value=bpy.types.Scene.custom_icons["instant"].icon_id).url = "https://github.com/wjakob/instant-meshes"
        self.layout.operator("wm.url_open", text="Quadriflow", icon="MOD_DECIM").url = "https://github.com/hjwdzh/QuadriFlow"
        self.layout.operator("wm.url_open", text="Meshlab", icon_value=bpy.types.Scene.custom_icons["meshlab"].icon_id).url = "http://www.meshlab.net/"
        self.layout.operator("wm.url_open", text="Colmap", icon="CAMERA_DATA").url = "https://colmap.github.io/"
        self.layout.operator("wm.url_open", text="OpenMVS", icon="CAMERA_DATA").url = "http://cdcseacave.github.io/openMVS/"



def register():
    bpy.utils.register_class(currentVersion)
    bpy.utils.register_class(checkUpdates)
    bpy.types.Scene.newVersion = None
    bpy.types.Scene.currentVersion = None

    bpy.utils.register_class(ScanPanel)
    bpy.utils.register_class(ImportPanel)
    bpy.utils.register_class(MaterialPanel)
    bpy.utils.register_class(RemeshFromSculptPanel)

    bpy.utils.register_class(PipelinePanel)
    bpy.utils.register_class(AboutPanel)
    bpy.utils.register_class(ExperimentalPanel)

    #Add the custom intensity slider
    bpy.utils.register_class(IntensityProperty)
    bpy.types.Scene.intensity = bpy.props.PointerProperty(type=IntensityProperty)
    #Add the custom path to texture library
    bpy.utils.register_class(MyCustomProperties)
    bpy.types.Scene.textures_path = bpy.props.PointerProperty(type=MyCustomProperties)
    #
    bpy.utils.register_class(ScanningProperties)
    bpy.types.Scene.images_directory = bpy.props.PointerProperty(type=ScanningProperties)
    bpy.types.Scene.imgpaths = ""

    bpy.types.Scene.my_image = bpy.props.PointerProperty(name="Image", type=bpy.types.Image)

    bpy.types.Scene.oldlinks = {}

    bpy.utils.register_class(MaterialProperties)
    bpy.types.Scene.bakemyscan_properties = bpy.props.PointerProperty(type=MaterialProperties)

def unregister():
    bpy.utils.unregister_class(currentVersion)
    bpy.utils.unregister_class(checkUpdates)

    bpy.utils.unregister_class(ScanPanel)
    bpy.utils.unregister_class(ImportPanel)
    bpy.utils.unregister_class(MaterialPanel)
    bpy.utils.unregister_class(RemeshFromSculptPanel)
    bpy.utils.unregister_class(PipelinePanel)
    bpy.utils.unregister_class(AboutPanel)
    bpy.utils.unregister_class(ExperimentalPanel)
    #Clear the custom intensity slider
    bpy.utils.unregister_class(IntensityProperty)
    del bpy.types.Scene.intensity
    #Clear the custom path to textures
    bpy.utils.unregister_class(MyCustomProperties)
    del bpy.types.Scene.textures_path

    bpy.utils.unregister_class(ScanningProperties)
    del bpy.types.Scene.images_directory
    del bpy.types.Scene.imgpaths

    del bpy.types.Scene.my_image
    del bpy.types.Scene.oldlinks
    del bpy.types.Scene.newVersion
    del bpy.types.Scene.currentVersion

    bpy.utils.unregister_class(MaterialProperties)
    del bpy.types.Scene.bakemyscan_properties
