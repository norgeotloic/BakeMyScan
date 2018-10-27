# coding: utf8
import os
import bpy
from   bpy_extras.io_utils import ImportHelper

from . import fn_match

class list_textures(bpy.types.Operator, ImportHelper):
    bl_idname = "bakemyscan.list_textures"
    bl_label  = "List available materials"
    bl_options = {"REGISTER", "UNDO"}

    filter_glob = bpy.props.StringProperty(
        default="*" + ";*".join(bpy.path.extensions_image),
        options={'HIDDEN'},
    )

    def execute(self, context):

        materials = fn_match.findMaterials(os.path.dirname(self.properties.filepath))
        settings  = findMaterialFromTexture(texture)
        if settings is not None:
            #If we are in view_3d, import the material and add it to active object
            if context.area.type == "VIEW_3D":
                #Init the material
                _material = bpy.data.materials.new("IMPORTED")
                _material.use_nodes = True
                _materialOutput = [_n for _n in _material.node_tree.nodes if _n.type=='OUTPUT_MATERIAL'][0]
                for _n in _material.node_tree.nodes:
                    if _n!=_materialOutput:
                        _material.node_tree.nodes.remove(_n)
                #Create and link the PBR group node
                _group = _material.node_tree.nodes.new(type="ShaderNodeGroup")
                _group.label = "IMPORTED"
                _group.node_tree = fn_nodes.node_tree_pbr(settings, name="IMPORTED")
                #Set the default height to 2% of the object size and the UV scale factor to 1
                _group.inputs["UV scale"].default_value = 1.0
                if obj is not None:
                    _group.inputs["Height"].default_value = 0.02 * max( max(obj.dimensions[0], obj.dimensions[1]), obj.dimensions[2] )
                else:
                    _group.inputs["Height"].default_value = 0.02
                _material.node_tree.links.new(_group.outputs["BSDF"], _materialOutput.inputs[0] )
                #Assign the object after unwrapping and adding a material if none is present
                if obj is not None:
                    if len(obj.material_slots)==0:
                        bpy.ops.object.material_slot_add()
                    if len(obj.data.uv_layers) == 0:
                         bpy.ops.uv.smart_project()
                    obj.material_slots[0].material = _material
            return{'FINISHED'}
        else:
            print("Did not manage to find a matching material")
            return{'CANCELLED'}

def register() :
    bpy.utils.register_class(list_textures)
    bpy.types.Scene.pbrtextures = {}

def unregister() :
    bpy.utils.unregister_class(list_textures)
    del bpy.types.Scene.pbrtextures
