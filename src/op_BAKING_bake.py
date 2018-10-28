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
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.data.screens['UV Editing'].areas[1].spaces[0].image = image
    bpy.context.object.active_material.use_textures[0] = False
    bpy.context.scene.render.bake_type = "NORMALS"
    bpy.ops.object.bake_image()
    image.save()
    bpy.ops.object.editmode_toggle()
    mat.use_nodes = restore
    bpy.context.scene.render.engine=engine

def copy_material(mat):
    tmpMat = mat.copy()
    for n in tmpMat.node_tree.nodes:
        if n.type=="GROUP":
            if n.node_tree.users>1:
                n.node_tree = n.node_tree.copy()
    return tmpMat

class bake_cycles_textures(bpy.types.Operator, ExportHelper):
    bl_idname = "bakemyscan.bake_textures"
    bl_label  = "Bake textures"
    bl_options = {"REGISTER", "UNDO"}

    filepath  = bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype='DIR_PATH',
        default="")
    filename_ext=''
    use_filter=True
    use_filter_folder=True

    resolution     = bpy.props.IntProperty( name="resolution",     description="image resolution", default=1024, min=128, max=8192)
    imgFormat      = bpy.props.EnumProperty(items= ( ('PNG', 'PNG', 'PNG'), ("JPEG", "JPEG", "JPEG")) , name="imgFormat", description="image format", default="JPEG")
    cageRatio      = bpy.props.FloatProperty(name="cageRatio", description="baking cage size as a ratio", default=0.1, min=0.00001, max=5)
    bake_albedo    = bpy.props.BoolProperty(name="bake_albedo",    description="albedo", default=True)
    bake_geometry  = bpy.props.BoolProperty(name="bake_geometry",   description="geometric normals", default=False)
    bake_surface   = bpy.props.BoolProperty(name="bake_surface",   description="material normals", default=False)
    bake_metallic  = bpy.props.BoolProperty(name="bake_metallic",  description="metalness", default=False)
    bake_roughness = bpy.props.BoolProperty(name="bake_roughness", description="roughness", default=False)
    bake_emission  = bpy.props.BoolProperty(name="bake_emission", description="emission", default=False)
    bake_opacity   = bpy.props.BoolProperty(name="bake_opacity",   description="opacity", default=False)

    @classmethod
    def poll(self, context):
        #Render engine must be cycles
        if bpy.context.scene.render.engine!="CYCLES":
            return 0
        #If more than two objects are selected
        if len(context.selected_objects)>2:
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
        #it must have slots
        if len(source.material_slots)==0:
            return 0
        #Each material must be not None and have nodes
        for slot in source.material_slots:
            if slot.material is None:
                return 0
            if slot.material.use_nodes == False:
                return 0
        if context.mode!="OBJECT":
            return 0
        #mmgs must be installed
        if context.user_preferences.addons["BakeMyScan"].preferences.convert == "":
            return 0
        return 1

    def execute(self, context):
        #Get the directory to save the images to
        self.directory = os.path.abspath(os.path.dirname(self.properties.filepath))

        #Find which object is the source and which is the target
        source, target = None, None
        if len(context.selected_objects) == 1:
            source = target = context.selected_objects[0]
        if len(context.selected_objects) == 2:
            target = [o for o in context.selected_objects if o==context.active_object][0]
            source = [o for o in context.selected_objects if o!=target][0]

        #Get the source material
        material  = source.material_slots[0].material

        # Set the baking parameters
        if source != target:
            bpy.data.scenes["Scene"].render.bake.use_selected_to_active = True
        bpy.data.scenes["Scene"].cycles.bake_type = 'EMIT'
        bpy.data.scenes["Scene"].cycles.samples   = 1
        bpy.data.scenes["Scene"].render.bake.margin = 8
        dims = source.dimensions
        bpy.data.scenes["Scene"].render.bake.use_cage = True
        bpy.data.scenes["Scene"].render.bake.cage_extrusion = self.cageRatio * max(max(dims[0], dims[1]), dims[2])
        bpy.data.scenes["Scene"].render.bake.use_clear = True

        #Proceed to the different channels baking
        toBake = {
            "Base Color": self.bake_albedo,
            "Metallic": self.bake_metallic,
            "Roughness": self.bake_roughness,
            "Normal": self.bake_surface,
            "Emission": self.bake_emission,
            "Opacity": self.bake_opacity
        }

        #Bake the Principled shader slots by transforming them to temporary emission shaders
        for baketype in toBake:
            if toBake[baketype]:

                #Copy the active material, and assign it
                tmpMat = copy_material(material)
                tmpMat.name = material.name + "_" + baketype
                source.material_slots[0].material = tmpMat

                #Get the material output node
                _matOut = [_n for _n in tmpMat.node_tree.nodes if _n.type == 'OUTPUT_MATERIAL' and _n.is_active_output][0]

                #Convert the node tree to an emission shader with the texture
                if baketype != "Emission" and baketype!= "Opacity":
                    fn_nodes.convert(tmpMat.node_tree, baketype)

                #Connect the correct group to the material output
                else:
                    #If we bake the emission, the shader should be good as it is
                    if baketype == "Emission":
                        pass
                    #If we bake the opacity, look for a mix factor for a transparent shader
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

                #Add a new material called "baking" to the target
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
                suffix   = baketype.replace(" ", "").lower()
                imgNode = addImageNode(targetMat, "baked_" + suffix, self.resolution, self.directory, self.imgFormat)

                #Do the baking and save the image
                bpy.ops.object.bake(type="EMIT")
                imgNode.image.save()

                #Remove the material and reassign the original one
                targetMat.node_tree.nodes.remove(imgNode)
                source.material_slots[0].material = material
                bpy.data.materials.remove(tmpMat)

        #Bake the geometric normals with blender render
        if source != target and self.bake_geometry:

            #Bake the normals with blender
            GEOM = os.path.join(os.path.abspath(self.directory), "baked_normal_geometric." + self.imgFormat.lower())
            NORM = os.path.join(os.path.abspath(self.directory), "baked_normal." + self.imgFormat.lower())
            bakeWithBlender(targetMat, "baked_normal_geometric", self.resolution, self.directory, self.imgFormat)

            #Merging the normal maps with Imagemagick
            if self.bake_surface:
                #Removing the blue channel from the material image
                TMP  = os.path.join(self.directory, "baked_normal_noblue." + self.imgFormat.lower())
                ARGS = "-channel Blue -evaluate set 0"
                output, error, code = fn_soft.convert(NORM, TMP, ARGS, executable=context.user_preferences.addons["BakeMyScan"].preferences.convert)
                #And appending the two images together
                OUT  = os.path.join(self.directory, "baked_normals." + self.imgFormat.lower())
                ARGS = "-compose overlay -composite"
                output, error, code = fn_soft.convert(GEOM, OUT, ARGS, input2=TMP, executable=context.user_preferences.addons["BakeMyScan"].preferences.convert)
                #Remove the old normal images (no blue channel, geometric normals...)
                os.remove(GEOM)
                os.remove(TMP)
                os.rename(OUT, NORM)
            else:
                os.rename(GEOM, NORM)

        # Import the resulting material
        def getbaked(baketype):
            return os.path.join(self.directory, "baked_" + baketype.replace(" ", "").lower() + "." + self.imgFormat.lower())

        importSettings = {
            "albedo":    getbaked("Base Color") if self.bake_albedo else None,
            "metallic":  getbaked("Metallic")   if self.bake_metallic else None,
            "roughness": getbaked("Roughness")  if self.bake_roughness else None,
            "normal":    getbaked("Normal")     if self.bake_geometry or self.bake_surface else None,
            "emission":  getbaked("Emission")   if self.bake_emission else None,
            "opacity":   getbaked("Opacity")    if self.bake_opacity else None
        }

        #Init the material
        for o in context.selected_objects:
            if o!=context.active_object:
                o.select=False
        bpy.ops.bakemyscan.create_empty_material()
        for _type in importSettings:
            if importSettings[_type] is not None:
                bpy.ops.bakemyscan.assign_texture(slot=_type, filepath=importSettings[_type])
        """
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
        """
        return{'FINISHED'}

def register() :
    bpy.utils.register_class(bake_cycles_textures)

def unregister() :
    bpy.utils.unregister_class(bake_cycles_textures)



"""
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
    _normal_geometric.image = bpy.data.images.load(os.path.join(self.directory, "baked_normal_geometric." + self.imgFormat.lower()), check_existing=False)
    _normal_surface = AN(type="ShaderNodeTexImage")
    _normal_surface.color_space = "NONE"
    _normal_surface.image = bpy.data.images.load(os.path.join(self.directory, "baked_normal." + self.imgFormat.lower()), check_existing=False)
    #Add a mixing group
    _mix = AN(type="ShaderNodeGroup")
    _mix.label = "Mix Normals"
    _mix.node_tree = fn_nodes.node_tree_combine_normals_2()
    _mix.inputs["Factor"].default_value=1.0
    #Add a normal map node
    _nmap = AN(type="ShaderNodeNormalMap")
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
    LN(_mix.outputs["Color"], _nmap.inputs["Color"])
    LN(_nmap.outputs["Normal"], _normal_to_color.inputs["Normal"])
    LN(_normal_to_color.outputs["Color"], _emission.inputs["Color"])
    LN(_emission.outputs["Emission"], normalMat.node_tree.nodes["Material Output"].inputs["Surface"])
    #Add the image for the baking
    imgNode = addImageNode(normalMat, "baked_normal_combined", self.resolution, self.directory, self.imgFormat)
    #Bake, save and restore
    bpy.ops.object.bake(type="EMIT")
    imgNode.image.save()
    #bpy.data.materials.remove(normalMat)
"""
