import bpy
import os
import time

class full_pipeline(bpy.types.Operator):
    bl_idname = "bakemyscan.full_pipeline"
    bl_label  = "Retopology"
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
            box.prop(self, "quadriflow_resolution", "Resolution")
            box = box.box()
            box.prop(self, "quadriflow_advanced", text="Advanced options")
            if self.quadriflow_advanced:
                box.prop(self, "quadriflow_sharp",   text="Preserve sharp edges")
                box.prop(self, "quadriflow_mincost", text="Use Min-Cost Flow solver")
                if os.name != "nt":
                    box.prop(self, "quadriflow_satflip",   text="SAT Flip Removal")
                    if self.quadriflow_satflip:
                        box.label('"minisat" and "timeout" need to be installed!')

        elif self.remeshing_method == "meshlab":
            box.prop(self, "meshlab_facescount",  text="Number of faces")
            box1 = box.box()
            box1.prop(self, "meshlab_advanced", text="Advanced options")
            if self.meshlab_advanced:
                box1.prop(self, "meshlab_quality", text="Quality threshold")
                box1.prop(self, "meshlab_normals", text="Preserve normals")
                box1.prop(self, "meshlab_topology", text="Preserve topology")
                box1.prop(self, "meshlab_existing", text="Use existing vertices")
                box1.prop(self, "meshlab_planar", text="Planar simplification")
                box1.prop(self, "meshlab_post", text="Post-process (isolated, duplicates...)")
                box1.prop(self, "meshlab_boundaries", text="Preserve boundary")
                if self.meshlab_boundaries:
                    box1.prop(self, "meshlab_weight", text="Boundary preserving weight")

        elif self.remeshing_method == "instant":
            box.prop(self, "instant_interactive", text="Interactive mode")
            if not self.instant_interactive:
                box.prop(self, "instant_method", text="Remesh according to")
                if self.instant_method == "faces":
                    box.prop(self, "instant_facescount",  text="Desired number of faces")
                elif self.instant_method == "verts":
                    box.prop(self, "instant_vertscount",  text="Desired number of vertices")
                elif self.instant_method == "edges":
                    box.prop(self, "instant_edgelength",  text="Desired edge length (ratio)")
                box2 = box.box()
                box2.prop(self, "instant_advanced", text="Advanced options")
                if self.instant_advanced:
                    box2.prop(self, "instant_d", text="Deterministic (slower)")
                    box2.prop(self, "instant_D", text="Tris/quads dominant instead of pure")
                    box2.prop(self, "instant_i", text="Intrinsic mode")
                    box2.prop(self, "instant_b", text="Align to boundaries")
                    box2.prop(self, "instant_C", text="Compatibility mode")
                    box2.prop(self, "instant_c", text="Creases angle threshold")
                    box2.prop(self, "instant_S", text="Smoothing reprojection steps")
                    box2.prop(self, "instant_r", text="Orientation symmetry type")
                    box2.prop(self, "instant_p", text="Position symmetry type")


        elif self.remeshing_method == "mmgs":
            box.prop(self, "mmgs_hausd",  text="Haussdorf distance (ratio)")
            box.prop(self, "mmgs_smooth", text="Ignore angle detection (smooth)")

            box0 = box.box()
            box0.prop(self, "mmgs_advanced", text="Advanced options")
            if self.mmgs_advanced:
                box0.prop(self, "mmgs_angle",  text="Angle detection (°)")
                if not self.mmgs_weight:
                    box0.prop(self, "mmgs_hmin",   text="Minimal edge size (ratio)")
                    box0.prop(self, "mmgs_hmax",   text="Maximal edge size (ratio)")
                box0.prop(self, "mmgs_hgrad",  text="Gradation parameter")
                box0.prop(self, "mmgs_aniso",  text="Enable anisotropy")
                box0.prop(self, "mmgs_nreg",   text="Normal regulation")

            box1 = box.box()
            box1.prop(self, "mmgs_weight", text="Use weight paint")
            if self.mmgs_weight:
                box1.label('Warning!')
                box1.label('Low weights (blue) <-> max size')
                box1.label('High weights (red) <-> min size')
                box1.label('Min size too low -> very long!')
                box1.label('Try defaults first!')
                box1.prop(self, "mmgs_hmin",   text="Minimal edge size (ratio)")
                box1.prop(self, "mmgs_hmax",   text="Maximal edge size (ratio)")

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
            bpy.ops.bakemyscan.remesh_decimate(
                limit=self.decim_limit,
                vertex_group=self.decim_vertex_group,
                factor=self.decim_factor
            )

        elif self.remeshing_method == "iterative":
            bpy.ops.bakemyscan.remesh_iterative(
                limit=self.iter_limit,
                vertex_group=self.iter_vertex_group,
                factor=self.iter_factor
            )

        elif self.remeshing_method == "quads":
            bpy.ops.bakemyscan.remesh_quads(
                nfaces=self.quads_nfaces,
                smooth=self.quads_smooth,
                vertex_group=self.quads_vertex_group,
                factor=self.quads_factor
            )

        elif self.remeshing_method == "quadriflow":
            bpy.ops.bakemyscan.remesh_quadriflow(
                resolution=self.quadriflow_resolution,
                sharp=self.quadriflow_sharp,
                mincost=self.quadriflow_mincost,
                satflip=self.quadriflow_satflip
            )

        elif self.remeshing_method == "meshlab":
            bpy.ops.bakemyscan.remesh_meshlab(
                facescount=self.meshlab_facescount,
                quality=self.meshlab_quality,
                boundaries=self.meshlab_boundaries,
                weight=self.meshlab_weight,
                normals=self.meshlab_normals,
                topology=self.meshlab_topology,
                existing=self.meshlab_existing,
                planar=self.meshlab_planar,
                post=self.meshlab_post,
            )

        elif self.remeshing_method == "instant":
            bpy.ops.bakemyscan.remesh_instant(
                interactive=self.instant_interactive,
                method=self.instant_method,
                facescount=self.instant_facescount,
                vertscount=self.instant_vertscount,
                edgelength=self.instant_edgelength,
                d=self.instant_d,
                D=self.instant_D,
                i=self.instant_i,
                b=self.instant_b,
                C=self.instant_C,
                c=self.instant_c,
                S=self.instant_S,
                r=self.instant_r,
                p=self.instant_p,
            )

        elif self.remeshing_method == "mmgs":
            bpy.ops.bakemyscan.remesh_mmgs(
                smooth=self.mmgs_smooth,
                hausd=self.mmgs_hausd,
                angle=self.mmgs_angle,
                hmin=self.mmgs_hmin,
                hmax=self.mmgs_hmax,
                hgrad=self.mmgs_hgrad,
                aniso=self.mmgs_aniso,
                nreg=self.mmgs_nreg,
                weight=self.mmgs_weight,
            )

        return{'FINISHED'}

def register() :
    bpy.utils.register_class(full_pipeline)

def unregister() :
    bpy.utils.unregister_class(full_pipeline)
