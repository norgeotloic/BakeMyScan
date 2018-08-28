import bpy
import os
from bpy_extras.io_utils import ExportHelper

from . import fn_nodes
from . import fn_soft

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
    bake_metallic  = bpy.props.BoolProperty(name="bake_metallic",  description="metalness", default=True)
    bake_roughness = bpy.props.BoolProperty(name="bake_roughness", description="roughness", default=True)
    bake_normals   = bpy.props.BoolProperty(name="bake_normals",   description="normals", default=True)
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
        #Find which is the source and which is the target
        source, target = None, None
        if len(context.selected_objects) == 1:
            source = target = context.selected_objects[0]
        if len(context.selected_objects) == 2:
            target = [o for o in context.selected_objects if o==context.active_object][0]
            source = [o for o in context.selected_objects if o!=target][0]

        # Set the baking parameters
        if source != target:
            bpy.data.scenes["Scene"].render.bake.use_selected_to_active = True
        bpy.data.scenes["Scene"].cycles.bake_type = 'EMIT'
        bpy.data.scenes["Scene"].cycles.samples   = 1
        bpy.data.scenes["Scene"].render.bake.margin = 8
        dims = source.dimensions
        bpy.data.scenes["Scene"].render.bake.cage_extrusion = self.cageRatio * max(max(dims[0], dims[1]), dims[2])
        bpy.data.scenes["Scene"].render.bake.use_clear = True

        #Which channels do we bake
        toBake = {
            "Base Color": self.bake_albedo,
            "Metallic": self.bake_metallic,
            "Roughness": self.bake_roughness,
            "Normal": self.bake_normals,
            "Emission": self.bake_emission,
            "Opacity": self.bake_opacity
        }

        #Adapt the initial material
        material  = source.material_slots[0].material

        for baketype in toBake:

            if toBake[baketype]:

                tmpMat = material.copy()
                tmpMat.name = material.name + "_" + baketype
                source.material_slots[0].material = tmpMat

                for n in tmpMat.node_tree.nodes:
                    if n.type=="GROUP":
                        if n.node_tree.users>1:
                            n.node_tree = n.node_tree.copy()

                group = createBakingNodeGroup(tmpMat, baketype) if baketype != "Emission" and baketype!= "Opacity" else None
                _matOut = [_n for _n in tmpMat.node_tree.nodes if _n.type == 'OUTPUT_MATERIAL' and _n.is_active_output][0]
                suffix   = baketype.replace(" ", "").lower()

                # Create a new image and image node for the baking in the target
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


                name = "baked_" + suffix
                if bpy.data.images.get(name):
                    bpy.data.images.remove(bpy.data.images.get(name))
                image = bpy.data.images.new(name, self.resolution, self.resolution)
                image.filepath_raw = os.path.join(os.path.abspath(self.directory), name + "." + self.imgFormat.lower())
                image.file_format  = self.imgFormat
                imagenode        = targetMat.node_tree.nodes.new(type="ShaderNodeTexImage") if not tmpMat.node_tree.nodes.get("imageNode") else tmpMat.node_tree.nodes.get("imageNode")
                imagenode.name   = "imageNode"
                imagenode.select = True
                targetMat.node_tree.nodes.active = imagenode
                imagenode.image = image

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

                #Remove the material and reassign the original one
                targetMat.node_tree.nodes.remove(imagenode)
                source.material_slots[0].material = material
                bpy.data.materials.remove(tmpMat)

                #Save the image
                image.save()


                #If selected to active and normals, we do the geometric normals in blender
                #and mix the normal maps with imagemagick
                if source != target and baketype == "Normal":
                    #blender baking
                    context.scene.render.engine="BLENDER_RENDER"
                    name = "baked_normal_geometric"
                    if bpy.data.images.get(name):
                        bpy.data.images.remove(bpy.data.images.get(name))
                    image = bpy.data.images.new(name, self.resolution, self.resolution)
                    image.filepath_raw = os.path.join(os.path.abspath(self.directory), name + "." + self.imgFormat.lower())
                    image.file_format  = self.imgFormat
                    tex = bpy.data.textures.new( name, type = 'IMAGE')
                    tex.image = image
                    targetMat.use_nodes = False
                    mtex = targetMat.texture_slots.add()
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
                    context.scene.render.engine="CYCLES"
                    targetMat.use_nodes = True
                    #Imagemagick... magic : removing the blue channel from the material image
                    rmBlue  = convertExe
                    rmBlue += os.path.join(self.directory, "baked_normal." + self.imgFormat.lower())
                    rmBlue += " -channel Blue -evaluate set 0 "
                    rmBlue += os.path.join(self.directory, "baked_tmp_normals." + self.imgFormat.lower())
                    os.system(rmBlue)
                    #And appending the two images together
                    overlay  = convertExe
                    overlay += os.path.join(self.directory, "baked_normal_geometric." + self.imgFormat.lower())
                    overlay += " " + os.path.join(self.directory, "baked_tmp_normals." + self.imgFormat.lower())
                    overlay += " -compose overlay -composite "
                    overlay += os.path.join(self.directory, "baked_normals." + self.imgFormat.lower())
                    os.system(overlay)

        #Import the resulting baked material
        if bpy.data.materials.get("baked_result") is not None:
            bpy.data.materials.remove(bpy.data.materials.get("baked_result"))
        def getbaked(baketype):
            name = "baked_" + baketype.replace(" ", "").lower()
            if baketype=="Normal":
                if target == source:
                    name = "baked_normal"
                else:
                    name = "baked_normals"
            return os.path.join(self.directory, name + "." + self.imgFormat.lower())
        importSettings = {
            "albedo": getbaked("Base Color") if self.bake_albedo else None,
            "metallic": getbaked("Metallic") if self.bake_metallic else None,
            "roughness": getbaked("Roughness") if self.bake_roughness else None,
            "normal": getbaked("Normal") if self.bake_normals else None,
            "emission": getbaked("Emission") if self.bake_emission else None,
            "opacity": getbaked("Opacity") if self.bake_opacity else None
        }
        print(importSettings)
        bakedMaterial = op_pbr.PBRMaterial(importSettings, name="baked_result")
        target.material_slots[0].material = bakedMaterial

        return{'FINISHED'}

def register() :
    bpy.utils.register_class(bake_textures)

def unregister() :
    bpy.utils.unregister_class(bake_textures)
