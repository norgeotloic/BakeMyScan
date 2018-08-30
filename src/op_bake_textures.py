import bpy
import os
from bpy_extras.io_utils import ExportHelper

from . import fn_nodes
from . import fn_soft

def addImageNode(mat, nam, res, dir, fmt):
    if bpy.data.images.get(nam):
        bpy.data.images.remove(bpy.data.images.get(nam))
    _image                     = bpy.data.images.new(nam, res, res)
    _image.filepath_raw        = os.path.join(os.path.abspath(dir), nam + "." + fmt.lower())
    _image.file_format         = fmt
    _imagenode                 = mat.node_tree.nodes.new(type="ShaderNodeTexImage") if not mat.node_tree.nodes.get("img") else mat.node_tree.nodes.get("img")
    _imagenode.name            = "img"
    _imagenode.select          = True
    mat.node_tree.nodes.active = _imagenode
    _imagenode.image           = _image
    return _imagenode

def bakeWithBlender(mat, nam, res, dir, fmt):
    restore = mat.use_nodes
    engine  = bpy.context.scene.render.engine
    bpy.context.scene.render.engine="BLENDER_RENDER"
    if bpy.data.images.get(nam):
        bpy.data.images.remove(bpy.data.images.get(nam))
    image = bpy.data.images.new(nam, res, res)
    image.filepath_raw = os.path.join(os.path.abspath(dir), nam + "." + fmt.lower())
    image.file_format  = fmt
    tex = bpy.data.textures.new( nam, type = 'IMAGE')
    tex.image = image
    mat.use_nodes = False
    mtex = mat.texture_slots.add()
    mtex.texture = tex
    mtex.texture_coords = 'UV'
    bpy.context.scene.render.use_bake_selected_to_active = True
    bpy.ops.object.editmode_toggle()
    bpy.data.screens['UV Editing'].areas[1].spaces[0].image = image
    bpy.context.object.active_material.use_textures[0] = False
    bpy.context.scene.render.bake_type = "NORMALS"
    bpy.ops.object.bake_image()
    image.save()
    bpy.ops.object.editmode_toggle()
    mat.use_nodes = restore
    bpy.context.scene.render.engine=engine

class bake_textures(bpy.types.Operator, ExportHelper):
    bl_idname = "bakemyscan.bake_textures"
    bl_label  = "Bake textures"
    bl_options = {"REGISTER", "UNDO"}

    directory         = bpy.props.StringProperty(subtype='DIR_PATH')
    filename_ext      = "."
    use_filter_folder = True

    resolution     = bpy.props.IntProperty( name="resolution",     description="image resolution", default=1024, min=128, max=8192)
    imgFormat      = bpy.props.EnumProperty(items= ( ('PNG', 'PNG', 'PNG'), ("JPEG", "JPEG", "JPEG")) , name="imgFormat", description="image format", default="JPEG")
    cageRatio      = bpy.props.FloatProperty(name="cageRation", description="baking cage size as a ratio", default=0.01, min=0.00001, max=0.5)
    bake_albedo    = bpy.props.BoolProperty(name="bake_albedo",    description="albedo", default=True)
    bake_geometry  = bpy.props.BoolProperty(name="bake_geometry",   description="geometric normals", default=True)
    bake_surface   = bpy.props.BoolProperty(name="bake_surface",   description="material normals", default=False)
    bake_metallic  = bpy.props.BoolProperty(name="bake_metallic",  description="metalness", default=False)
    bake_roughness = bpy.props.BoolProperty(name="bake_roughness", description="roughness", default=False)
    bake_emission  = bpy.props.BoolProperty(name="bake_emission", description="emission", default=False)
    bake_opacity   = bpy.props.BoolProperty(name="bake_opacity",   description="opacity", default=False)

    @classmethod
    def poll(self, context):
        if len(context.selected_objects)>2:
            return 0
        if context.active_object is None:
            return 0
        if len(context.selected_objects) == 1:
            obj = context.selected_objects[0]
            if len(obj.material_slots)>0:
                if obj.material_slots[0].material is not None:
                    return 1
        if len(context.selected_objects) == 2:
            target = [o for o in context.selected_objects if o==context.active_object][0]
            source = [o for o in context.selected_objects if o!=target][0]
            if len(source.material_slots)>0:
                if source.material_slots[0].material is not None:
                    return 1
        return 0

    def execute(self, context):
        #Find which is the source and which is the target, plus material
        source, target = None, None
        if len(context.selected_objects) == 1:
            source = target = context.selected_objects[0]
        if len(context.selected_objects) == 2:
            target = [o for o in context.selected_objects if o==context.active_object][0]
            source = [o for o in context.selected_objects if o!=target][0]
        material  = source.material_slots[0].material

        # Set the cycles baking parameters
        if source != target:
            bpy.data.scenes["Scene"].render.bake.use_selected_to_active = True
        bpy.data.scenes["Scene"].cycles.bake_type = 'EMIT'
        bpy.data.scenes["Scene"].cycles.samples   = 1
        bpy.data.scenes["Scene"].render.bake.margin = 8
        dims = source.dimensions
        bpy.data.scenes["Scene"].render.bake.cage_extrusion = self.cageRatio * max(max(dims[0], dims[1]), dims[2])
        bpy.data.scenes["Scene"].render.bake.use_clear = True

        #Proceed to the different channels baking
        toBake = {
            "Base Color": self.bake_albedo,
            "Metallic": self.bake_metallic,
            "Roughness": self.bake_roughness,
            "Normal": self.bake_surface,
            "Emission": self.bake_emission,
            "Opacity": self.bake_opacity}
        for baketype in toBake:
            if toBake[baketype]:
                #Prepare a copy of the material which will be used as baking input
                tmpMat = material.copy()
                tmpMat.name = material.name + "_" + baketype
                source.material_slots[0].material = tmpMat
                for n in tmpMat.node_tree.nodes:
                    if n.type=="GROUP":
                        if n.node_tree.users>1:
                            n.node_tree = n.node_tree.copy()
                group = fn_nodes.createBakingNodeGroup(tmpMat, baketype) if baketype != "Emission" and baketype!= "Opacity" else None
                _matOut = [_n for _n in tmpMat.node_tree.nodes if _n.type == 'OUTPUT_MATERIAL' and _n.is_active_output][0]
                # Create a new image and image node for the baking in the target
                suffix   = baketype.replace(" ", "").lower()
                targetMat = tmpMat
                if target != source:
                    if len(target.material_slots)>0:
                        if target.material_slots[0].material is not None:
                            targetMat = target.material_slots[0].material
                        else:
                            targetMat = bpy.data.materials.new("baking")
                            target.material_slots[0].material = targetMat
                    else:
                        bpy.ops.object.material_slot_add()
                        targetMat = bpy.data.materials.new("baking")
                        target.material_slots[0].material = targetMat
                    targetMat.use_nodes = True
                #Add an image node to the material with the baked result image assigned
                imgNode = addImageNode(targetMat, "baked_" + suffix, self.resolution, self.directory, self.imgFormat)
                #Connect the correct group to the material output
                if baketype == "Emission":
                    pass
                elif baketype == "Opacity":
                    alphaMixNode = None
                    for n in tmpMat.node_tree.nodes:
                        if n.type == 'BSDF_TRANSPARENT':
                            for link in n.outputs["BSDF"].links:
                                if link.to_node.type == "MIX_SHADER":
                                    for l in link.to_node.inputs["Fac"].links:
                                        alphaMixNode = l.from_node
                                        _emission = tmpMat.node_tree.nodes.new(type="ShaderNodeEmission")
                                        tmpMat.node_tree.links.new(alphaMixNode.outputs[0], _emission.inputs["Color"])
                                        tmpMat.node_tree.links.new(_emission.outputs["Emission"], _matOut.inputs["Surface"])
                    if alphaMixNode is None:
                        continue
                else:
                    tmpMat.node_tree.links.new(group.outputs[0], _matOut.inputs[0])
                #bake
                bpy.ops.object.bake(type="EMIT")
                #Save the image
                imgNode.image.save()
                #Remove the material and reassign the original one
                targetMat.node_tree.nodes.remove(imgNode)
                source.material_slots[0].material = material
                bpy.data.materials.remove(tmpMat)


        #Bake the geometric normals with blender render
        if source != target and self.bake_geometry:
            bakeWithBlender(targetMat, "baked_normal_geometric", self.resolution, self.directory, self.imgFormat)

        #Imagemagick... magic : removing the blue channel from the material image
        if fn_soft.convertExe is not None and source != target and self.bake_geometry and self.bake_surface:
            rmBlue  = fn_soft.convertExe
            rmBlue += os.path.join(self.directory, "baked_normal." + self.imgFormat.lower())
            rmBlue += " -channel Blue -evaluate set 0 "
            rmBlue += os.path.join(self.directory, "baked_tmp_normals." + self.imgFormat.lower())
            os.system(rmBlue)
            #And appending the two images together
            overlay  = fn_soft.convertExe
            overlay += os.path.join(self.directory, "baked_normal_geometric." + self.imgFormat.lower())
            overlay += " " + os.path.join(self.directory, "baked_tmp_normals." + self.imgFormat.lower())
            overlay += " -compose overlay -composite "
            overlay += os.path.join(self.directory, "baked_normals." + self.imgFormat.lower())
            os.system(overlay)


        #Bake the geometric and surface normals to one (Imagemagick or node setup)
        if source != target and self.bake_geometry and self.bake_surface:
            bpy.ops.object.select_all(action="DESELECT")
            target.select = True
            context.scene.objects.active = target
            bpy.data.scenes["Scene"].render.bake.use_selected_to_active = False
            #Add a material for the normals mixing
            normalMat = bpy.data.materials.new("normalMat")
            target.material_slots[0].material = normalMat
            normalMat.use_nodes = True
            normalMat.node_tree.nodes.remove(normalMat.node_tree.nodes['Diffuse BSDF'])
            AN = normalMat.node_tree.nodes.new
            #Add the two normal maps
            _normal_geometric = AN(type="ShaderNodeTexImage")
            _normal_geometric.color_space = "NONE"
            _normal_geometric.image = bpy.data.images.load(os.path.join(self.directory, "baked_normal_geometric." + self.imgFormat.lower()))
            _normal_surface = AN(type="ShaderNodeTexImage")
            _normal_surface.color_space = "NONE"
            _normal_surface.image = bpy.data.images.load(os.path.join(self.directory, "baked_normal." + self.imgFormat.lower()))
            #Add a mixing group
            _mix = AN(type="ShaderNodeGroup")
            _mix.label = "Mix Normals"
            _mix.node_tree = fn_nodes.node_tree_mix_normals()
            #Add the normal to color node
            _normal_to_color = AN(type="ShaderNodeGroup")
            _normal_to_color.label = "Normals to color"
            _normal_to_color.node_tree = fn_nodes.node_tree_normal_to_color()
            #And an emission shader
            _emission = AN(type="ShaderNodeEmission")
            #Link everything
            LN = normalMat.node_tree.links.new
            LN(_normal_geometric.outputs["Color"], _mix.inputs["Geometry"])
            LN(_normal_surface.outputs["Color"], _mix.inputs["Surface"])
            LN(_mix.outputs["Normal"], _normal_to_color.inputs["Normal"])
            LN(_normal_to_color.outputs["Color"], _emission.inputs["Color"])
            LN(_emission.outputs["Emission"], normalMat.node_tree.nodes["Material Output"].inputs["Surface"])


            #Add the image for the baking
            imgNode = addImageNode(normalMat, "baked_normal_combined", self.resolution, self.directory, self.imgFormat)
            #Bake, save and restore
            bpy.ops.object.bake(type="EMIT")
            imgNode.image.save()
            bpy.data.materials.remove(normalMat)

        #Import the resulting baked material

        def getbaked(baketype):
            name = "baked_" + baketype.replace(" ", "").lower()
            if baketype == "Normal" and source!=target:
                if os.path.exists( os.path.join(self.directory, "baked_normals." + self.imgFormat.lower()) ):
                    name = "baked_normals"
            image = os.path.join(self.directory, name + "." + self.imgFormat.lower())
            return image

        bakedNormal = None
        if self.bake_geometry and not self.bake_surface:
            bakedNormal = os.path.join(self.directory, "baked_normal_geometric." + self.imgFormat.lower())
        if not self.bake_geometry and self.bake_surface:
            bakedNormal = os.path.join(self.directory, "baked_normal." + self.imgFormat.lower())
        if self.bake_geometry and self.bake_surface:
            bakedNormal = os.path.join(self.directory, "baked_normal_combined." + self.imgFormat.lower())

        importSettings = {
            "albedo":    getbaked("Base Color") if self.bake_albedo else None,
            "metallic":  getbaked("Metallic")   if self.bake_metallic else None,
            "roughness": getbaked("Roughness")  if self.bake_roughness else None,
            "normal":    bakedNormal            if self.bake_geometry or self.bake_surface else None,
            "emission":  getbaked("Emission")   if self.bake_emission else None,
            "opacity":   getbaked("Opacity")    if self.bake_opacity else None
        }
        print(importSettings)

        #Init the material
        if bpy.data.materials.get("baked_result") is not None:
            bpy.data.materials.remove(bpy.data.materials.get("baked_result"))
        _material = bpy.data.materials.new("baked_result")
        _material.use_nodes = True
        _materialOutput = [_n for _n in _material.node_tree.nodes if _n.type=='OUTPUT_MATERIAL'][0]
        for _n in _material.node_tree.nodes:
            if _n!=_materialOutput:
                _material.node_tree.nodes.remove(_n)
        #Create and link the PBR group node
        _group = _material.node_tree.nodes.new(type="ShaderNodeGroup")
        _group.label = "baked_result"
        _group.node_tree = fn_nodes.node_tree_pbr(settings = importSettings, name="baking_result")
        #Set the default height to 2% of the object size and the UV scale factor to 1
        _group.inputs["UV scale"].default_value = 1.0
        _group.inputs["Height"].default_value = 0.02 * max( max(target.dimensions[0], target.dimensions[1]), target.dimensions[2] )
        _material.node_tree.links.new(_group.outputs["BSDF"], _materialOutput.inputs[0] )
        #Assign the object after unwrapping and adding a material if none is present
        if len(target.material_slots)==0:
            bpy.ops.object.material_slot_add()
        target.material_slots[0].material = _material

        return{'FINISHED'}

def register() :
    bpy.utils.register_class(bake_textures)

def unregister() :
    bpy.utils.unregister_class(bake_textures)
