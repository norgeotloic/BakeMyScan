import bpy
import os
import time

class full_pipeline(bpy.types.Operator):
    bl_idname = "bakemyscan.full_pipeline"
    bl_label  = "Optimize the model"
    bl_options = {"REGISTER", "UNDO"}

    #Quadriflow
    quadriflow_resolution = bpy.props.IntProperty(description="Resolution", default=1000, min=10, max=100000 )
    quadriflow_advanced = bpy.props.BoolProperty(description="advanced properties", default=False)
    quadriflow_mincost  = bpy.props.BoolProperty(description="Min-Cost Flow Solver", default=False )
    quadriflow_sharp    = bpy.props.BoolProperty(description="Preserve sharp edges", default=False )
    quadriflow_satflip  = bpy.props.BoolProperty(description="SAT Flip Removal", default=False )

    #Instant
    instant_interactive = bpy.props.BoolProperty(description="Interactive", default=False)
    instant_method      = bpy.props.EnumProperty(items= ( ('faces', 'Number of faces', 'Number of faces'), ("verts", "Number of verts", "Number of verts"), ("edges", "Edge length", "Edge length")), description="Remesh according to", default="faces")
    instant_facescount  = bpy.props.IntProperty(description="Number of faces", default=5000, min=10, max=10000000 )
    instant_vertscount  = bpy.props.IntProperty(description="Number of verts", default=5000, min=10, max=10000000 )
    instant_edgelength  = bpy.props.FloatProperty(description="Edge length (ratio)", default=0.05, min=0.001, max=1 )
    instant_advanced = bpy.props.BoolProperty(description="advanced properties", default=False)
    instant_d = bpy.props.BoolProperty(description="Deterministic (slower)", default=False)
    instant_D = bpy.props.BoolProperty(description="Tris/quads dominant instead of pure", default=False)
    instant_i = bpy.props.BoolProperty(description="Intrinsic mode", default=False)
    instant_b = bpy.props.BoolProperty(description="Align to boundaries", default=False)
    instant_C = bpy.props.BoolProperty(description="Compatibility mode", default=False)
    instant_c = bpy.props.FloatProperty(description="Creases angle threshold", default=30, min=0, max=180 )
    instant_S = bpy.props.IntProperty(description="Smoothing reprojection steps", default=2, min=0, max=100 )
    instant_r = bpy.props.EnumProperty(items= ( ('r0', 'none', 'none'), ("2", "2", "2"), ("4", "4", "4"), ("6", "6", "6")) ,description="Orientation symmetry type", default="r0")
    instant_p = bpy.props.EnumProperty(items= ( ('p0', 'none', 'none'), ("4", "4", "4"), ("6", "6", "6")) ,description="Position symmetry type", default="p0")

    #mmgs
    mmgs_smooth = bpy.props.BoolProperty(description="Ignore angle detection (smooth)", default=True)
    mmgs_hausd  = bpy.props.FloatProperty(description="Haussdorf distance (ratio)", default=0.01, min=0.0001, max=1)
    mmgs_advanced = bpy.props.BoolProperty(description="advanced properties", default=False)
    mmgs_angle  = bpy.props.FloatProperty(description="Angle detection (°)", default=30, min=0.01, max=180.)
    mmgs_hmin   = bpy.props.FloatProperty(description="Minimal edge size (ratio)", default=0.005, min=0.0001, max=1)
    mmgs_hmax   = bpy.props.FloatProperty(description="Maximal edge size (ratio)", default=0.05, min=0.0001, max=5)
    mmgs_hgrad  = bpy.props.FloatProperty(description="Gradation parameter", default=1.3, min=1., max=5.)
    mmgs_aniso  = bpy.props.BoolProperty(description="Enable anisotropy", default=False)
    mmgs_nreg   = bpy.props.BoolProperty(description="Normal regulation", default=False)
    mmgs_weight   = bpy.props.BoolProperty(description="weight as edge length", default=False)

    #meshlab
    meshlab_facescount = bpy.props.IntProperty(description="Number of faces", default=5000, min=10, max=1000000 )
    meshlab_advanced = bpy.props.BoolProperty(description="advanced properties", default=False)
    meshlab_quality    = bpy.props.FloatProperty(description="Quality threshold", default=0.3, min=0., max=1. )
    meshlab_boundaries = bpy.props.BoolProperty(description="Preserve boundary", default=False)
    meshlab_weight     = bpy.props.FloatProperty(description="Boundary preserving weight", default=1., min=0., max=1. )
    meshlab_normals  = bpy.props.BoolProperty(description="Preserve normals", default=False)
    meshlab_topology = bpy.props.BoolProperty(description="Preserve topology", default=False)
    meshlab_existing = bpy.props.BoolProperty(description="Use existing vertices", default=False)
    meshlab_planar   = bpy.props.BoolProperty(description="Planar simplification", default=False)
    meshlab_post     = bpy.props.BoolProperty(description="Post-process (isolated, duplicates...)", default=True)

    #Decimate
    decim_limit    = bpy.props.IntProperty(description="Target faces", default=1500, min=50, max=500000)
    decim_vertex_group = bpy.props.BoolProperty(description="Use vertex group", default=False)
    decim_factor = bpy.props.FloatProperty(description="Weight factor", default=0.5, min=0., max=1.)

    #Iterative
    iter_limit    = bpy.props.IntProperty(description="Target faces", default=1500, min=50, max=500000)
    iter_vertex_group  = bpy.props.BoolProperty(description="Use vertex group", default=False)
    iter_factor = bpy.props.FloatProperty(description="Weight factor", default=0.5, min=0., max=1.)

    #Quads
    quads_nfaces = bpy.props.IntProperty(description="Decimate ratio",  default=1500, min=50, max=200000)
    quads_smooth = bpy.props.IntProperty(description="Smoothing steps", default=1, min=0, max=15)
    quads_vertex_group  = bpy.props.BoolProperty(description="Use vertex group", default=False)
    quads_factor = bpy.props.FloatProperty(description="Weight factor", default=0.5, min=0., max=1.)

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
        description="Remeshing method",
        default="decimate"
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def check(self, context):
        return True

    def draw(self, context):
        box = self.layout.box()
        box.prop(self, "remeshing_method", text="Retopology method")

        box = self.layout.box()

        if self.remeshing_method == "decimate":
            box.prop(self, "decim_limit", text="Number of faces")
            box.prop(self, "decim_vertex_group", text="Use weights")
            if self.decim_vertex_group:
                box.prop(self, "decim_factor", text="Weight factor")

        elif self.remeshing_method == "iterative":
            box.prop(self, "iter_limit", text="Number of faces")
            box.prop(self, "iter_vertex_group", text="Use weights")
            if self.iter_vertex_group:
                box.prop(self, "iter_factor", text="Weight factor")

        elif self.remeshing_method == "quads":
            box.prop(self, "quads_nfaces",  text="Number of quads (min)")
            box.prop(self, "quads_smooth", text="Relaxation steps")
            box.prop(self, "quads_vertex_group", text="Use weights")
            if self.quads_vertex_group:
                box.prop(self, "quads_factor", text="Weight factor")

        elif self.remeshing_method == "quadriflow":
            op_REMESHERS.Quads.draw(self, context)

        elif self.remeshing_method == "meshlab":
            op_REMESHERS.Quads.draw(self, context)

        elif self.remeshing_method == "instant":
            op_REMESHERS.Quads.draw(self, context)

        elif self.remeshing_method == "mmgs":
            op_REMESHERS.Quads.draw(self, context)

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
        return 1

    def execute(self, context):

        if self.remeshing_method == "decimate":
            bpy.ops.bakemyscan.remesh_decimate(limit=self.decim_limit, vertex_group=self.decim_vertex_group, factor=self.decim_factor)

        elif self.remeshing_method == "iterative":
            bpy.ops.bakemyscan.remesh_iterative(limit=self.iter_limit, vertex_group=self.iter_vertex_group, factor=self.iter_factor)

        elif self.remeshing_method == "quads":
            bpy.ops.bakemyscan.remesh_quads(nfaces=self.quads_nfaces, smooth=self.quads_smooth, vertex_group=self.quads_vertex_group, factor=self.quads_factor)

        elif self.remeshing_method == "quadriflow":
            op_REMESHERS.Quads.draw(self, context)

        elif self.remeshing_method == "meshlab":
            op_REMESHERS.Quads.draw(self, context)

        elif self.remeshing_method == "instant":
            op_REMESHERS.Quads.draw(self, context)

        elif self.remeshing_method == "mmgs":
            op_REMESHERS.Quads.draw(self, context)

        return{'FINISHED'}

def register() :
    bpy.utils.register_class(full_pipeline)

def unregister() :
    bpy.utils.unregister_class(full_pipeline)
