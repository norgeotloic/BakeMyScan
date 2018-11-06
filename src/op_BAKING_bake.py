import bpy
import os
from . import fn_nodes
from . import fn_soft
from . import fn_bake
import numpy as np
import collections
import time

def addImageNode(mat, nam, res):
    if bpy.data.images.get(nam):
        bpy.data.images.remove(bpy.data.images.get(nam))
    _image                     = bpy.data.images.new(nam, res, res)
    _imagenode                 = mat.node_tree.nodes.new(type="ShaderNodeTexImage") if not mat.node_tree.nodes.get("img") else mat.node_tree.nodes.get("img")
    _imagenode.name            = "img"
    _imagenode.select          = True
    mat.node_tree.nodes.active = _imagenode
    _imagenode.image           = _image
    return _imagenode

def bakeWithBlender(mat, nam, res, _type="NORMALS"):
    #To blender internal
    restore = mat.use_nodes
    engine  = bpy.context.scene.render.engine
    bpy.context.scene.render.engine="BLENDER_RENDER"
    mat.use_nodes = False
    bpy.context.scene.render.use_bake_to_vertex_color = False


    if bpy.data.images.get(nam):
        bpy.data.images.remove(bpy.data.images.get(nam))
    image = bpy.data.images.new(nam, res, res)

    tex = bpy.data.textures.new( nam, type = 'IMAGE')
    tex.image = image

    for c in range(3):
        if mat.texture_slots[c] is not None:
            mat.texture_slots.clear(c)
    mtex = mat.texture_slots.add()
    mtex.texture = tex
    mtex.texture_coords = 'UV'

    bpy.context.scene.render.use_bake_selected_to_active = True

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.data.screens['UV Editing'].areas[1].spaces[0].image = image
    mat.use_textures[0] = False
    bpy.context.scene.render.bake_type = _type
    bpy.ops.object.bake_image()
    bpy.ops.object.editmode_toggle()

    #Do some clean up
    bpy.data.textures.remove(tex)

    #Back to original
    mat.use_nodes = restore
    bpy.context.scene.render.engine=engine
    return image

class bake_cycles_textures(bpy.types.Operator):
    bl_idname = "bakemyscan.bake_textures"
    bl_label  = "Textures to textures"
    bl_options = {"REGISTER", "UNDO"}

    resolution     = bpy.props.IntProperty( name="resolution",     description="image resolution", default=1024, min=128, max=8192)
    cageRatio      = bpy.props.FloatProperty(name="cageRatio",     description="baking cage size as a ratio", default=0.1, min=0.00001, max=5)
    bake_albedo    = bpy.props.BoolProperty(name="bake_albedo",    description="albedo", default=True)
    bake_ao        = bpy.props.BoolProperty(name="bake_ao",        description="ambient occlusion", default=False)
    bake_geometry  = bpy.props.BoolProperty(name="bake_geometry",  description="geometric normals", default=True)
    bake_surface   = bpy.props.BoolProperty(name="bake_surface",   description="material normals", default=False)
    bake_metallic  = bpy.props.BoolProperty(name="bake_metallic",  description="metalness", default=False)
    bake_roughness = bpy.props.BoolProperty(name="bake_roughness", description="roughness", default=False)
    bake_emission  = bpy.props.BoolProperty(name="bake_emission",  description="emission", default=False)
    bake_opacity   = bpy.props.BoolProperty(name="bake_opacity",   description="opacity", default=False)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        box = self.layout.box()
        box.prop(self, "resolution", text="Image resolution")
        box.prop(self, "cageRatio",  text="Relative cage size")
        box = self.layout.box()
        box.label("PBR channels")
        box.prop(self, "bake_albedo",    text="Albedo")
        box.prop(self, "bake_metallic",  text="Metallic")
        box.prop(self, "bake_roughness", text="Roughness")
        box.label("Other channels")
        box.prop(self, "bake_geometry", text="Geometric normals")
        box.prop(self, "bake_surface",  text="Surface normals")
        box.prop(self, "bake_ao",       text="Ambient occlusion")
        box.prop(self, "bake_emission", text="Emission")
        box.prop(self, "bake_opacity",  text="Opacity")
        col = self.layout.column(align=True)

    @classmethod
    def poll(self, context):
        #Render engine must be cycles
        if bpy.context.scene.render.engine!="CYCLES":
            return 0
        #If more than two objects are selected
        if len(context.selected_objects)!=2:
            return 0
        #If no object is active
        if context.active_object is None:
            return 0
        #If something other than a MESH is selected
        for o in context.selected_objects:
            if o.type != "MESH":
                return 0
        #The source object must have correct materials
        source = [o for o in context.selected_objects if o!=context.active_object][0] if len(context.selected_objects)==2 else context.active_object
        target = context.active_object
        #Each material must be not None and have nodes
        if source.active_material is None:
            return 0
        if source.active_material.use_nodes == False:
            return 0
        if context.mode!="OBJECT":
            return 0
        #The target object must have a UV layout
        if len(target.data.uv_layers) == 0:
            return 0
        return 1

    def execute(self, context):

        #Find which object is the source and which is the target
        source, target = None, None
        if len(context.selected_objects) == 1:
            source = target = context.selected_objects[0]
        if len(context.selected_objects) == 2:
            target = [o for o in context.selected_objects if o==context.active_object][0]
            source = [o for o in context.selected_objects if o!=target][0]

        #Get the source material
        material  = source.active_material

        # Set the baking parameters
        bpy.data.scenes["Scene"].render.bake.use_selected_to_active = True
        bpy.data.scenes["Scene"].cycles.bake_type = 'EMIT'
        bpy.data.scenes["Scene"].cycles.samples   = 1
        bpy.data.scenes["Scene"].render.bake.margin = 8
        dims = source.dimensions
        bpy.data.scenes["Scene"].render.bake.use_cage = True
        bpy.data.scenes["Scene"].render.bake.cage_extrusion = self.cageRatio * max(max(dims[0], dims[1]), dims[2])

        #Proceed to the different channels baking
        toBake = collections.OrderedDict()
        toBake["Base Color"] = self.bake_albedo
        toBake["Metallic"]   = self.bake_metallic
        toBake["Roughness"]  = self.bake_roughness
        toBake["Normal"]     = self.bake_surface
        toBake["Emission"]   = self.bake_emission
        toBake["Opacity"]    = self.bake_opacity

        #Keep track of the baked images
        baked = {}
        #Give a prefix to the image names
        prefix = target.name.replace("_","").replace(" ","").replace(".","").replace("-","").lower() + "_baked"

        t0 = time.time()

        #Bake the Principled shader slots by transforming them to temporary emission shaders
        for baketype in toBake:
            if toBake[baketype]:

                print("Baking the channel: %s" % baketype)

                #Copy the active material, and assign it to the source
                tmpMat      = fn_bake.create_source_baking_material(material, baketype)
                tmpMat.name = material.name + "_" + baketype
                source.active_material = tmpMat

                #Create a material for the target
                targetMat = fn_bake.create_target_baking_material(target)

                #Add an image node to the material with the baked result image assigned
                suffix     = baketype.replace(" ", "").lower()
                imgNode    = addImageNode(targetMat, prefix + "_" + suffix, self.resolution)

                #If we are in normal baking, make the background neutral and do no use clear
                if baketype == "Normal":
                    bpy.data.scenes["Scene"].render.bake.use_clear = False
                    pixels = np.zeros((self.resolution, self.resolution, 4))
                    pixels[:,:,:] = [0.5, 0.5, 1, 1]
                    imgNode.image.pixels = np.ravel(pixels)

                #Do the baking and keep the image
                bpy.ops.object.bake(type="EMIT")
                baked[baketype] = imgNode.image

                #Remove the material and reassign the original one
                targetMat.node_tree.nodes.remove(imgNode)
                source.active_material = material
                bpy.data.materials.remove(tmpMat)
                bpy.data.scenes["Scene"].render.bake.use_clear = True

        #Bake the AO
        if self.bake_ao:
            print("Baking the ao")
            baked["AO"] = bakeWithBlender(targetMat, prefix + "_ao", self.resolution, _type="AO")

        #Bake and mix the normal maps
        if self.bake_geometry:
            print("Baking the geometric normals")
            if self.bake_surface:
                baked["Geometry"] = bakeWithBlender(targetMat, prefix + "_geometry", self.resolution)
                print("Mixing geometric and surface normals")
                baked["Normals"] = fn_bake.overlay_normals(baked["Geometry"], baked["Normal"], prefix + "_normals")
                bpy.data.images.remove(baked["Geometry"])
                bpy.data.images.remove(baked["Normal"])
            else:
                baked["Normals"] = bakeWithBlender(targetMat, prefix + "_normals", self.resolution)
        else:
            if self.bake_surface:
                baked["Normals"] = baked["Normal"]
                baked["Normals"].name = prefix + "_normals"

        importSettings = {
            "albedo":    baked["Base Color"] if self.bake_albedo else None,
            "ao":        baked["AO"]         if self.bake_ao else None,
            "metallic":  baked["Metallic"]   if self.bake_metallic else None,
            "roughness": baked["Roughness"]  if self.bake_roughness else None,
            "normal":    baked["Normals"]    if self.bake_geometry or self.bake_surface else None,
            "emission":  baked["Emission"]   if self.bake_emission else None,
            "opacity":   baked["Opacity"]    if self.bake_opacity else None
        }

        #Init the material
        for o in context.selected_objects:
            if o!=context.active_object:
                o.select=False
        bpy.ops.bakemyscan.create_empty_material(name=prefix+"_material")
        for _type in importSettings:
            if importSettings[_type] is not None:
                bpy.ops.bakemyscan.assign_texture(slot=_type, filepath=importSettings[_type].name, byname=True)

        print("Baking finished in %f seconds." % (time.time() - t0))
        self.report({'INFO'}, "Baking successful")
        return{'FINISHED'}

def register() :
    bpy.utils.register_class(bake_cycles_textures)

def unregister() :
    bpy.utils.unregister_class(bake_cycles_textures)
