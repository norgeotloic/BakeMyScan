# coding: utf8
import bpy
from . import fn_nodes

class create_empty_material(bpy.types.Operator):
    bl_idname = "bakemyscan.create_empty_material"
    bl_label  = "Import a PBR material"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        #Need to be in Cycles render mode
        if bpy.context.scene.render.engine != "CYCLES":
            return 0
        if bpy.context.area.type != "NODE_EDITOR" and bpy.context.area.type != "VIEW_3D" :
            return 0
        if bpy.context.active_object is None or len(bpy.context.selected_objects)!=1:
            return 0
        return 1

    def execute(self, context):
        #Get the active object if there is one
        obj = context.active_object

        #If we are in material mode, we just add a group to the node editor
        if context.area.type == "NODE_EDITOR":
            #Get the active material
            mat = obj.material_slots[0].material
            #Create the group
            _group = mat.node_tree.nodes.new(type="ShaderNodeGroup")
            _group.node_tree = fn_nodes.node_tree_pbr(settings={}, name="PBR")
            _group.label = "PBR"
            #Set the default height to 2% of the object size and the UV scale factor to 1
            _group.inputs["UV scale"].default_value = 1.0
            _group.inputs["Height"].default_value = 0.02 * max( max(obj.dimensions[0], obj.dimensions[1]), obj.dimensions[2] )
            #Select the group and link it to the mouse for better placement
            for n in mat.node_tree.nodes:
                n.select = False
            _group.select = True
            _group.location = context.space_data.cursor_location
            mat.node_tree.nodes.active = _group
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        #If we are in view_3d, import the material and add it to active object
        else:
            #Init the material
            _material = bpy.data.materials.new("PBR")
            _material.use_nodes = True
            _materialOutput = [_n for _n in _material.node_tree.nodes if _n.type=='OUTPUT_MATERIAL'][0]
            for _n in _material.node_tree.nodes:
                if _n!=_materialOutput:
                    _material.node_tree.nodes.remove(_n)
            #Create and link the PBR group node
            _group = _material.node_tree.nodes.new(type="ShaderNodeGroup")
            _group.label = "PBR"
            _group.node_tree = fn_nodes.node_tree_pbr(settings={}, name="PBR")
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

def register() :
    bpy.utils.register_class(create_empty_material)

def unregister() :
    bpy.utils.unregister_class(create_empty_material)
