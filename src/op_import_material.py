# coding: utf8
import bpy
from . import fn_nodes

def PBRMaterial(settings, name):
    """Returns a new PBR material from the given settings"""
    #Init the material
    _material = bpy.data.materials.new(name)
    _material.use_nodes = True
    _materialOutput = [_n for _n in _material.node_tree.nodes if _n.type=='OUTPUT_MATERIAL'][0]
    for _n in _material.node_tree.nodes:
        if _n!=_materialOutput:
            _material.node_tree.nodes.remove(_n)
    _group = _material.node_tree.nodes.new(type="ShaderNodeGroup")
    _group.label = name
    _group.node_tree = PBRTree(settings)
    _group.inputs[0].default_value = 1.0
    _material.node_tree.links.new(_group.outputs[0], _materialOutput.inputs[0] )
    return _material

def PBRGroup(settings, material, name):
    """Inserts a new PBR group into the specified material"""
    #Init the material
    _group = material.node_tree.nodes.new(type="ShaderNodeGroup")
    _group.node_tree = PBRTree(settings)
    _group.inputs[0].default_value = 1.0
    _group.label = name
    return _group

def my_callback(scene, context):
    mats = [m for m in bpy.types.Scene.pbrtextures.keys()]
    mats.sort()
    return [(m, m, "", i) for i,m in enumerate(mats)]

class import_material(bpy.types.Operator):
    bl_idname = "bakemyscan.import_material"
    bl_label  = "Import a PBR material"
    bl_options = {"REGISTER", "UNDO"}
    bl_property = "enum"

    enum = bpy.props.EnumProperty(
        name="PBR textures",
        description="",
        items=my_callback
        )

    @classmethod
    def poll(self, context):
        if len(bpy.types.Scene.pbrtextures.keys())==0:
            return 0
        return 1

    def invoke(self, context, event):
        if context.area.type == "NODE_EDITOR":
            context.space_data.cursor_location_from_region(event.mouse_region_x, event.mouse_region_y)
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

    def execute(self, context):

        self.report({'INFO'}, 'Selected %s' % (self.enum))

        materials = bpy.types.Scene.pbrtextures

        print("SELECTED_MATERIAL")
        for key in materials[self.enum]:
            print(materials[self.enum][key])

        #If we are in view_3d, import the material and add it to active object
        if context.area.type == "VIEW_3D":
            material = PBRMaterial(materials[self.enum], name=self.enum)
            obj = context.active_object
            if obj is not None:
                if len(obj.material_slots)==0:
                    bpy.ops.object.material_slot_add()
                if len(obj.data.uv_layers) == 0:
                     bpy.ops.uv.smart_project()
                obj.material_slots[0].material = material
        #If we are in material mode, we just add a group
        if context.area.type == "NODE_EDITOR":
            mat = context.active_object.material_slots[0].material
            group = PBRGroup(materials[self.enum], mat, name=self.enum)
            for n in mat.node_tree.nodes:
                n.select = False
            group.select = True
            group.location = context.space_data.cursor_location
            mat.node_tree.nodes.active = group
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        return{'FINISHED'}

def register() :
    bpy.utils.register_class(import_material)

def unregister() :
    bpy.utils.unregister_class(import_material)
