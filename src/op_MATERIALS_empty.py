# coding: utf8
import bpy
from . import fn_nodes

def add_empty_group_to_material(_material, obj, name="PBR"):
    #Create and link the PBR group node
    _group = _material.node_tree.nodes.new(type="ShaderNodeGroup")
    _group.node_tree = fn_nodes.node_tree_pbr(settings={}, name=name)
    _group.label = name
    _group.name  = name
    #Set the default height to 2% of the object size and the UV scale factor to 1
    _group.inputs["UV scale"].default_value = 1.0
    _group.inputs["Height"].default_value   = 0.005 * max( max(obj.dimensions[0], obj.dimensions[1]), obj.dimensions[2] )
    return _group

class create_empty_material(bpy.types.Operator):
    bl_idname = "bakemyscan.create_empty_material"
    bl_label  = "Creates an empty PBR material"
    bl_options = {"REGISTER", "UNDO"}

    name = bpy.props.StringProperty(name="name", default="PBR", description="Material name")

    @classmethod
    def poll(self, context):
        #Need to be in Cycles render mode
        if bpy.context.scene.render.engine != "CYCLES":
            return 0
        if bpy.context.active_object is None:
            return 0
        if len([o for o in bpy.context.selected_objects if o.type=="MESH"])!=1:
            return 0
        return 1

    def execute(self, context):
        #Get the active object if there is one
        obj = context.active_object

        #Init the material
        _material = bpy.data.materials.new(self.name)
        _material.use_nodes = True
        _materialOutput = [_n for _n in _material.node_tree.nodes if _n.type=='OUTPUT_MATERIAL'][0]
        for _n in _material.node_tree.nodes:
            if _n!=_materialOutput:
                _material.node_tree.nodes.remove(_n)

        #Create the group
        _group = add_empty_group_to_material(_material, obj, self.name)

        #Link it to the material output
        _material.node_tree.links.new(_group.outputs["BSDF"], _materialOutput.inputs[0] )

        #Assign the object after unwrapping and adding a material if none is present
        obj.active_material = _material

        return{'FINISHED'}

class create_empty_node(bpy.types.Operator):
    bl_idname = "bakemyscan.create_empty_node"
    bl_label  = "Creates an empty PBR node"
    bl_options = {"REGISTER", "UNDO"}

    name = bpy.props.StringProperty(name="name", default="PBR", description="Material name")

    @classmethod
    def poll(self, context):
        #Need to be in Cycles render mode
        if bpy.context.scene.render.engine != "CYCLES":
            return 0
        if context.active_object is None:
            return 0
        if context.active_object.active_material is None:
            return 0
        if len([o for o in bpy.context.selected_objects if o.type=="MESH"])!=1:
            return 0
        return 1

    def execute(self, context):
        mat = context.active_object.active_material

        #Create the group
        _group = add_empty_group_to_material(mat, context.active_object, self.name)

        #Select the group and link it to the mouse for better placement
        for n in mat.node_tree.nodes:
            n.select = False
        _group.select = True
        _group.location = context.space_data.cursor_location
        mat.node_tree.nodes.active = _group
        bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        return{'FINISHED'}

def register() :
    bpy.utils.register_class(create_empty_material)
    bpy.utils.register_class(create_empty_node)

def unregister() :
    bpy.utils.unregister_class(create_empty_material)
    bpy.utils.unregister_class(create_empty_node)
