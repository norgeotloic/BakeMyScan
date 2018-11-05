# coding: utf8
import bpy
from   bpy_extras.io_utils import ImportHelper
import os

from . import fn_nodes

class assign_texture(bpy.types.Operator, ImportHelper):
    bl_idname = "bakemyscan.assign_texture"
    bl_label  = "Assign PBR textures to a material"
    bl_options = {"REGISTER", "UNDO"}

    filter_glob = bpy.props.StringProperty(
        default="*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff;*.exr",
        options={'HIDDEN'},
    )
    slot = bpy.props.EnumProperty(
        items= (
            ('albedo', 'albedo', 'albedo'),
            ("normal", "normal", "normal"),
            ("roughness", "roughness", "roughness"),
            ("glossiness", "glossiness", "glossiness"),
            ("metallic", "metallic", "metallic"),
            ("ao", "ao", "ao"),
            ("height", "height", "height"),
            ("opacity", "opacity", "opacity"),
            ("emission", "emission", "emission"),
        ) ,
        name="slot",
        description="image type",
        default="albedo"
    )

    byname = bpy.props.BoolProperty(name="byname", description="pass images by name instead of files", default=False)

    @classmethod
    def poll(self, context):
        #Need to be in Cycles render mode
        if bpy.context.scene.render.engine != "CYCLES":
            return 0
        #Only one selected object
        if context.active_object is None or len(context.selected_objects)!=1:
            return 0
        #With an active material
        if context.active_object.active_material is None:
            return 0
        #Using nodes
        if context.active_object.active_material.use_nodes == False:
            return 0
        #Having a group only
        group   = None
        nGroups = 0
        for node in context.active_object.active_material.node_tree.nodes:
            if node.type=="GROUP":
                group = node
                nGroups += 1
        if group is None:
            return 0
        #Containing a "BakeMyScan PBR" principled node
        nodes = group.node_tree.nodes
        if nodes.get("BakeMyScan PBR") is None:
            return 0
        else:
            return 1

    def execute(self, context):

        #Get the active object and its material
        obj   = context.active_object
        mat   = context.active_object.active_material

        #Get the active group (multiple can arise while adding groups)
        groups = [n for n in mat.node_tree.nodes if n.type=="GROUP"]
        group = None
        if len(groups) == 1:
            group = groups[0]
        else:
            for g in groups:
                if g == mat.node_tree.nodes.active:
                    group = g
                    break
            if group is None:
                group = groups[0]

        nodes = group.node_tree.nodes

        #Load the image in the image node
        imageNode = nodes.get(self.slot)
        if imageNode is None:
            print("Can not find node %s in material %s" % (self.slot, mat.name))
            return {'CANCELLED'}
        else:
            #Pass the images by name
            if self.byname:
                if bpy.data.images.get(self.filepath) is not None:
                    imageNode.image = bpy.data.images.get(self.filepath)
                else:
                    print("No image named %s found" % self.filepath)
            #Pass the images by path
            else:
                if os.path.exists(self.filepath):
                    imageNode.image = bpy.data.images.load(self.filepath, check_existing=True)
                else:
                    print("%s not found" % self.filepath)

        #Get the link function
        LN = group.node_tree.links.new
        PR = nodes.get("BakeMyScan PBR")
        #Make the obvious links
        if self.slot == "albedo" and nodes.get("albedo") is not None:
            LN(nodes.get("albedo").outputs["Color"], nodes.get("ao_mix").inputs[1])
            LN(nodes.get("ao_mix").outputs["Color"], PR.inputs["Base Color"])
        if self.slot == "roughness" and nodes.get("roughness") is not None:
            LN(nodes.get("roughness").outputs["Color"], PR.inputs["Roughness"])
        if self.slot == "metallic" and nodes.get("metallic") is not None:
            LN(nodes.get("metallic").outputs["Color"], PR.inputs["Metallic"])
        #And the less obvious ones
        if self.slot == "ao" and nodes.get("ao") is not None:
            LN(nodes.get("ao").outputs["Color"], nodes.get("ao_mix").inputs[2])
            LN(nodes.get("ao_mix").outputs["Color"], PR.inputs["Base Color"])
        if self.slot == "glossiness" and nodes.get("glossiness") is not None:
            LN(nodes.get("glossiness").outputs["Color"], nodes.get("glossiness_invert").inputs["Color"])
            LN(nodes.get("glossiness_invert").outputs["Color"], PR.inputs["Roughness"])
        #Less obvious with the normals and heights
        if self.slot == "height" or self.slot == "normal":
            LN(nodes.get("bump").outputs["Normal"], PR.inputs["Normal"])
            if self.slot == "height" and nodes.get("height") is not None:
                LN(nodes.get("input").outputs["Height"], nodes.get("bump").inputs["Distance"])
                LN(nodes.get("height").outputs["Color"], nodes.get("bump").inputs["Height"])
            if self.slot == "normal" and nodes.get("nmap") is not None and nodes.get("normal") is not None:
                LN(nodes.get("normal").outputs["Color"], nodes.get("nmap").inputs["Color"])
                LN(nodes.get("nmap").outputs["Normal"], nodes.get("bump").inputs["Normal"])
        #Post shader emission and opacity mix
        if self.slot == "emission" and nodes.get("emission") is not None:
            LN(nodes.get("emission").outputs["Color"], nodes.get("emission_shader").inputs["Color"])
            LN(nodes.get("emission").outputs["Color"], nodes.get("emission_mix").inputs[0])
            LN(nodes.get("emission_shader").outputs["Emission"], nodes.get("emission_mix").inputs[2])
            LN(PR.outputs["BSDF"], nodes.get("emission_mix").inputs[1])
        if self.slot == "opacity" and nodes.get("opacity") is not None:
            #LN(nodes.get("opacity").outputs["Color"], nodes.get("opacity_shader").inputs["Color"])
            LN(nodes.get("opacity").outputs["Color"], nodes.get("opacity_mix").inputs[0])
            LN(nodes.get("opacity_shader").outputs["BSDF"], nodes.get("opacity_mix").inputs[1])
            if nodes.get("emission").image is not None:
                LN(nodes.get("emission_mix").outputs["Shader"], nodes.get("opacity_mix").inputs[2])
            else:
                LN(PR.outputs["BSDF"], nodes.get("opacity_mix").inputs[2])

        #Switch to vertex paint mode
        try:
            bpy.context.space_data.viewport_shade = 'MATERIAL'
        except:
            pass

        self.report({'INFO'}, self.slot + ' slot assigned')
        return{'FINISHED'}

def register() :
    bpy.utils.register_class(assign_texture)

def unregister() :
    bpy.utils.unregister_class(assign_texture)
