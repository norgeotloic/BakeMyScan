import bpy
import os
import time

from . import op_REMESHERS

class full_pipeline(bpy.types.Operator):
    bl_idname = "bakemyscan.full_pipeline"
    bl_label  = "Optimize the model"
    bl_options = {"REGISTER", "UNDO"}

    #Remeshing options
    remeshing_method = bpy.props.EnumProperty(
        items= (
            ('decimate', 'Decimate', ''),
            ('iterative', 'Iterative', ''),
            ('quads', 'Quick quads', ''),
            ('mmgs', 'Mmgs', ''),
            ('meshlab', 'Meshlab', ''),
            ('instant', 'Instant Meshes', ''),
            ('quadriflow', 'Quadriflow', ''),
        ),
        name="remeshing_method",
        description="Remeshing method",
        default="decimate"
    )

    #Decimate options
    limit    = bpy.props.IntProperty(name="limit",    description="Target faces", default=1500, min=50, max=500000)
    vertex_group = bpy.props.BoolProperty(name="vertex_group", description="Use vertex group", default=True)

    #Iterative options
    limit    = bpy.props.IntProperty(name="limit",    description="Target faces", default=1500, min=50, max=500000)
    manifold = bpy.props.BoolProperty(name="manifold", description="Make manifold", default=False)
    #vertex_group = bpy.props.BoolProperty(name="vertex_group", description="Use vertex group", default=True)

    #Quads options
    nfaces = bpy.props.IntProperty(name="nfaces",   description="Decimate ratio",  default=1500, min=50, max=200000)
    smooth = bpy.props.IntProperty(  name="smooth", description="Smoothing steps", default=1, min=0, max=15)


    """
    resolution     = bpy.props.IntProperty( name="resolution",     description="image resolution", default=1024, min=128, max=8192)
    cageRatio      = bpy.props.FloatProperty(name="cageRatio",     description="baking cage size as a ratio", default=0.1, min=0.00001, max=5)
    bake_albedo    = bpy.props.BoolProperty(name="bake_albedo",    description="albedo", default=True)
    bake_ao        = bpy.props.BoolProperty(name="bake_ao",        description="ambient occlusion", default=False)
    bake_geometry  = bpy.props.BoolProperty(name="bake_geometry",  description="geometric normals", default=True)
    bake_surface   = bpy.props.BoolProperty(name="bake_surface",   description="material normals", default=False)
    bake_metallic  = bpy.props.BoolProperty(name="bake_metallic",  description="metalness", default=False)
    bake_roughness = bpy.props.BoolProperty(name="bake_roughness", description="roughness", default=False)
    bake_transmission = bpy.props.BoolProperty(name="bake_transmission",  description="transmission", default=False)
    bake_subsurface = bpy.props.BoolProperty(name="bake_subsurface",  description="subsurface", default=False)
    bake_emission  = bpy.props.BoolProperty(name="bake_emission",  description="emission", default=False)
    bake_opacity   = bpy.props.BoolProperty(name="bake_opacity",   description="opacity", default=False)
    """

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def check(self, context):
        return True

    def draw(self, context):
        box = self.layout.box()
        box.prop(self, "remeshing_method", text="Retopology method")
        if self.remeshing_method == "decimate":
            op_REMESHERS.Basic.draw(self, context)
        elif self.remeshing_method == "iterative":
            op_REMESHERS.Iterative.draw(self, context)
        elif self.remeshing_method == "quads":
            op_REMESHERS.Quads.draw(self, context)
        else:
            pass

    @classmethod
    def poll(self, context):
        #Render engine must be cycles
        if bpy.context.scene.render.engine!="CYCLES":
            return 0
        #Object mode
        if context.mode!="OBJECT":
            return 0
        #If more than two objects are selected
        if len(context.selected_objects)!=1:
            return 0
        #If no object is active
        if context.active_object is None:
            return 0
        #If something other than a MESH is selected
        for o in context.selected_objects:
            if o.type != "MESH":
                return 0
        #Each material must be not None and have nodes
        if context.active_object.active_material is None:
            return 0
        if context.active_object.active_material.use_nodes == False:
            return 0
        return 1

    def execute(self, context):

        """
        method = bpy.props.EnumProperty(
            items= (
                ('iterative', 'iterative', 'iterative'),
                ("2", "2", "2"),
                ("4", "4", "4"), ("6", "6", "6")) , name="r", description="Orientation symmetry type", default="r0")
            """
        return{'FINISHED'}

def register() :
    bpy.utils.register_class(full_pipeline)

def unregister() :
    bpy.utils.unregister_class(full_pipeline)
