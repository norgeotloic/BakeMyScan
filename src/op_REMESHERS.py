import bpy
import os
from . import fn_soft
import tempfile
import time
from mathutils import Vector
import numpy as np

from . import op_REMESHERS_BASE as base

# External software

class Quadriflow(base.BaseRemesher):
    bl_idname = "bakemyscan.remesh_quadriflow"
    bl_label  = "Quadriflow"

    resolution = bpy.props.IntProperty( name="resolution", description="Resolution", default=1000, min=10, max=100000 )

    advanced = bpy.props.BoolProperty(  name="advanced", description="advanced properties", default=False)
    mincost  = bpy.props.BoolProperty( name="mincost", description="Min-Cost Flow Solver", default=False )
    sharp    = bpy.props.BoolProperty( name="sharp", description="Preserve sharp edges", default=False )
    satflip  = bpy.props.BoolProperty( name="satflip", description="SAT Flip Removal", default=False )

    def check(self, context):
        return True
    def draw(self, context):
        self.layout.prop(self, "resolution", text="Resolution")

        box = self.layout.box()
        box.prop(self, "advanced", text="Advanced options")
        if self.advanced:
            box.prop(self, "sharp",   text="Preserve sharp edges")
            box.prop(self, "mincost", text="Use Min-Cost Flow solver")
            if os.name != "nt":
                box.prop(self, "satflip",   text="SAT Flip Removal")
                if self.satflip:
                    box.label('"minisat" and "timeout" need to be installed!')

    #Overriden methods
    def setexe(self, context):
        self.executable = bpy.types.Scene.executables["quadriflow"]
    def export(self, context):
        bpy.ops.export_scene.obj(
            filepath      = os.path.join(self.tmp.name, "tmp.obj"),
            use_selection = True
        )
    def reimport(self, context):
        bpy.ops.import_scene.obj(filepath=os.path.join(self.tmp.name, "tmp.o.obj"))
    def remesh(self, context):
        self.results = fn_soft.quadriflow(
            executable  = self.executable,
            input_mesh  = os.path.join(self.tmp.name, "tmp.obj"),
            output_mesh = os.path.join(self.tmp.name, "tmp.o.obj"),
            face_count = self.resolution,
            mincost = self.mincost,
            sharp = self.sharp,
            satflip = self.satflip,
        )

class Instant(base.BaseRemesher):
    bl_idname = "bakemyscan.remesh_instant"
    bl_label  = "Instant Meshes"

    interactive = bpy.props.BoolProperty(  name="interactive", description="Interactive", default=False)
    method      = bpy.props.EnumProperty(items= ( ('faces', 'Number of faces', 'Number of faces'), ("verts", "Number of verts", "Number of verts"), ("edges", "Edge length", "Edge length")) , name="Remesh according to", description="Remesh according to", default="faces")
    facescount  = bpy.props.IntProperty(   name="facescount",  description="Number of faces", default=5000, min=10, max=10000000 )
    vertscount  = bpy.props.IntProperty(   name="vertscount",  description="Number of verts", default=5000, min=10, max=10000000 )
    edgelength  = bpy.props.FloatProperty( name="edgelength",  description="Edge length (ratio)", default=0.05, min=0.001, max=1 )

    d = bpy.props.BoolProperty( name="d", description="Deterministic (slower)", default=False)
    D = bpy.props.BoolProperty( name="D", description="Tris/quads dominant instead of pure", default=False)
    i = bpy.props.BoolProperty( name="i", description="Intrinsic mode", default=False)
    b = bpy.props.BoolProperty( name="b", description="Align to boundaries", default=False)
    C = bpy.props.BoolProperty( name="C", description="Compatibility mode", default=False)

    c = bpy.props.FloatProperty( name="c",  description="Creases angle threshold", default=30, min=0, max=180 )
    S = bpy.props.IntProperty(   name="S",  description="Smoothing reprojection steps", default=2, min=0, max=100 )
    r = bpy.props.EnumProperty(items= ( ('r0', 'none', 'none'), ("2", "2", "2"), ("4", "4", "4"), ("6", "6", "6")) , name="r", description="Orientation symmetry type", default="r0")
    p = bpy.props.EnumProperty(items= ( ('p0', 'none', 'none'), ("4", "4", "4"), ("6", "6", "6")) , name="r", description="Position symmetry type", default="p0")

    advanced = bpy.props.BoolProperty(  name="advanced", description="advanced properties", default=False)

    def check(self, context):
        return True
    def draw(self, context):
        box = self.layout.box()
        box.prop(self, "interactive", text="Interactive mode")

        if not self.interactive:
            box.label('Basic options')
            box.prop(self, "method", text="Remesh according to")
            if self.method == "faces":
                box.prop(self, "facescount",  text="Desired number of faces")
            elif self.method == "verts":
                box.prop(self, "vertscount",  text="Desired number of vertices")
            elif self.method == "edges":
                box.prop(self, "edgelength",  text="Desired edge length (ratio)")

            box = self.layout.box()
            box.prop(self, "advanced", text="Advanced options")
            if self.advanced:
                box.prop(self, "d", text="Deterministic (slower)")
                box.prop(self, "D", text="Tris/quads dominant instead of pure")
                box.prop(self, "i", text="Intrinsic mode")
                box.prop(self, "b", text="Align to boundaries")
                box.prop(self, "C", text="Compatibility mode")
                box.prop(self, "c", text="Creases angle threshold")
                box.prop(self, "S", text="Smoothing reprojection steps")
                box.prop(self, "r", text="Orientation symmetry type")
                box.prop(self, "p", text="Position symmetry type")

        col = self.layout.column(align=True)

    #Overriden methods
    def setexe(self, context):
        self.executable = bpy.types.Scene.executables["instant"]
    def export(self, context):
        bpy.ops.export_scene.obj(
            filepath      = os.path.join(self.tmp.name, "tmp.obj"),
            use_selection = True
        )
    def reimport(self, context):
        #Get the mesh the user saved
        toreimport = ""
        if self.interactive:
            for l in self.results[0].split("\n"):
                if "Writing" in l:
                    toreimport = l.split('"')[1]
        else:
            toreimport = os.path.join(self.tmp.name, "tmp.o.obj")
        bpy.ops.import_scene.obj(filepath=toreimport)
        os.remove(toreimport)
    def remesh(self, context):
        obj    = context.active_object
        maxDim = max( max( obj.dimensions[0], obj.dimensions[1]) , obj.dimensions[2] )
        if self.interactive:
            self.results = fn_soft.instant_meshes_gui(
                executable  = self.executable,
                input_mesh  = os.path.join(self.tmp.name, "tmp.obj"),
            )
        else:
            self.results = fn_soft.instant_meshes_cmd(
                executable  = self.executable,
                input_mesh  = os.path.join(self.tmp.name, "tmp.obj"),
                output_mesh = os.path.join(self.tmp.name, "tmp.o.obj"),
                face_count   = self.facescount if self.method=="faces" else None,
                vertex_count = self.vertscount if self.method=="verts" else None,
                edge_length  = self.edgelength*maxdim if self.method=="edges" else None,
                d = self.d,
                D = self.D,
                i = self.i,
                b = self.b,
                C = self.C,
                c = self.c,
                S = self.S,
                p = self.p if self.p!="p0" else None,
                r = self.r if self.r!="r0" else None
            )

class Mmgs(base.BaseRemesher):
    bl_idname = "bakemyscan.remesh_mmgs"
    bl_label  = "Mmgs"

    #Basic options
    smooth = bpy.props.BoolProperty(  name="smooth", description="Ignore angle detection (smooth)", default=True)
    hausd  = bpy.props.FloatProperty( name="hausd", description="Haussdorf distance (ratio)", default=0.01, min=0.0001, max=1)
    #Advanced options
    advanced = bpy.props.BoolProperty(  name="advanced", description="advanced properties", default=False)
    angle  = bpy.props.FloatProperty( name="hausd",  description="Angle detection (°)", default=30, min=0.01, max=180.)
    hmin   = bpy.props.FloatProperty( name="hmin",   description="Minimal edge size (ratio)", default=0.005, min=0.0001, max=1)
    hmax   = bpy.props.FloatProperty( name="hmax",   description="Maximal edge size (ratio)", default=0.05, min=0.0001, max=5)
    hgrad  = bpy.props.FloatProperty( name="hgrad",  description="Gradation parameter", default=1.3, min=1., max=5.)
    aniso  = bpy.props.BoolProperty(  name="aniso",  description="Enable anisotropy", default=False)
    nreg   = bpy.props.BoolProperty(  name="nreg",   description="Normal regulation", default=False)
    weight   = bpy.props.BoolProperty(  name="weight", description="weight as edge length", default=False)

    def check(self, context):
        return True
    def draw(self, context):
        box = self.layout.box()
        box.label('Basic options')
        box.prop(self, "hausd",  text="Haussdorf distance (ratio)")
        box.prop(self, "smooth", text="Ignore angle detection (smooth)")

        box = self.layout.box()
        box.prop(self, "weight", text="Use weight paint")
        if self.weight:
            box.label('Warning!')
            box.label('Low weights (blue) <-> max size')
            box.label('High weights (red) <-> min size')
            box.label('Min size too low -> very long!')
            box.label('Try defaults first!')
            box.prop(self, "hmin",   text="Minimal edge size (ratio)")
            box.prop(self, "hmax",   text="Maximal edge size (ratio)")

        box = self.layout.box()
        box.prop(self, "advanced", text="Advanced options")
        if self.advanced:
            box.prop(self, "angle",  text="Angle detection (°)")
            if not self.weight:
                box.prop(self, "hmin",   text="Minimal edge size (ratio)")
                box.prop(self, "hmax",   text="Maximal edge size (ratio)")
            box.prop(self, "hgrad",  text="Gradation parameter")
            box.prop(self, "aniso",  text="Enable anisotropy")
            box.prop(self, "nreg",   text="Normal regulation")

        col = self.layout.column(align=True)

    #Overriden methods
    def setexe(self, context):
        self.executable = bpy.types.Scene.executables["mmgs"]
    def export(self, context):
        obj    = context.active_object
        self.maxDim = max( max( obj.dimensions[0], obj.dimensions[1]) , obj.dimensions[2] )
        bpy.ops.bakemyscan.export_mesh(
            filepath=os.path.join(self.tmp.name, "tmp.mesh"),
            writeSol=self.weight,
            miniSol=self.hmin * self.maxDim,
            maxiSol=self.hmax * self.maxDim
        )
    def reimport(self, context):
        bpy.ops.bakemyscan.import_mesh(filepath=os.path.join(self.tmp.name, "tmp.o.mesh"))
    def remesh(self, context):
        self.results = fn_soft.mmgs(
            executable  = self.executable,
            input_mesh  = os.path.join(self.tmp.name, "tmp.mesh"),
            output_mesh = os.path.join(self.tmp.name, "tmp.o.mesh"),
            hausd       = self.hausd * self.maxDim,
            hgrad       = self.hgrad,
            hmin        = self.hmin * self.maxDim,
            hmax        = self.hmax * self.maxDim,
            ar          = self.angle,
            nr          = self.smooth,
            aniso       = self.aniso,
            nreg        = self.nreg,
        )
    def status(self, context):
        pass

class Meshlab(base.BaseRemesher):
    bl_idname = "bakemyscan.remesh_meshlab"
    bl_label  = "Meshlab"

    facescount = bpy.props.IntProperty( name="facescount", description="Number of faces", default=5000, min=10, max=1000000 )
    advanced = bpy.props.BoolProperty(  name="advanced", description="advanced properties", default=False)
    quality    = bpy.props.FloatProperty( name="quality", description="Quality threshold", default=0.3, min=0., max=1. )
    boundaries = bpy.props.BoolProperty( name="boundaries", description="Preserve boundary", default=False)
    weight     = bpy.props.FloatProperty( name="weight", description="Boundary preserving weight", default=1., min=0., max=1. )
    normals  = bpy.props.BoolProperty( name="normals", description="Preserve normals", default=False)
    topology = bpy.props.BoolProperty( name="topology", description="Preserve topology", default=False)
    existing = bpy.props.BoolProperty( name="existing", description="Use existing vertices", default=False)
    planar   = bpy.props.BoolProperty( name="planar", description="Planar simplification", default=False)
    post     = bpy.props.BoolProperty( name="post", description="Post-process (isolated, duplicates...)", default=True)

    def check(self, context):
        return True
    def draw(self, context):
        box = self.layout.box()
        box.label('Basic options')
        box.prop(self, "facescount",  text="Number of faces")

        box = self.layout.box()
        box.prop(self, "advanced", text="Advanced options")
        if self.advanced:
            box.prop(self, "quality", text="Quality threshold")
            box.prop(self, "normals", text="Preserve normals")
            box.prop(self, "topology", text="Preserve topology")
            box.prop(self, "existing", text="Use existing vertices")
            box.prop(self, "planar", text="Planar simplification")
            box.prop(self, "post", text="Post-process (isolated, duplicates...)")
            box.prop(self, "boundaries", text="Preserve boundary")
            if self.boundaries:
                box.prop(self, "weight", text="Boundary preserving weight")


    #Overriden methods
    def setexe(self, context):
        self.executable = bpy.types.Scene.executables["meshlabserver"]
    def export(self, context):
        bpy.ops.export_scene.obj(
            filepath      = os.path.join(self.tmp.name, "tmp.obj"),
            use_selection = True
        )
    def remesh(self, context):
        #Create a temporary meshlab script with custom variables
        original_script = os.path.join(os.path.dirname(__file__), os.path.pardir, "scripts_meshlab", "quadricedgecollapse.mlx")
        new_script      = os.path.join(self.tmp.name, "tmp.mlx")
        with open(original_script, 'r') as infile :
            filedata = infile.read()
            newdata  = filedata.replace("FACESCOUNT", str(self.facescount))
            newdata  = newdata.replace("QUALITY", str(self.quality))
            newdata  = newdata.replace("BOUNDS", str(self.boundaries).lower())
            newdata  = newdata.replace("WEIGHT", str(self.weight))
            newdata  = newdata.replace("NORMALS", str(self.normals).lower())
            newdata  = newdata.replace("TOPO", str(self.topology).lower())
            newdata  = newdata.replace("OPTIM", str(not self.existing).lower())
            newdata  = newdata.replace("PLANAR", str(self.planar).lower())
            newdata  = newdata.replace("CLEAN", str(self.post).lower())
            if os.name == "nt":
                newdata = newdata.replace("FILTERNAME", "Simplification: Quadric Edge Collapse Decimation")
            else:
                newdata = newdata.replace("FILTERNAME", "Quadric Edge Collapse Decimation")
            with open(new_script, 'w') as outfile:
                outfile.write(newdata)
        #remesh
        self.results  = fn_soft.meshlabserver(
            executable  = self.executable,
            input_mesh  = os.path.join(self.tmp.name, "tmp.obj"),
            output_mesh = os.path.join(self.tmp.name, "tmp.o.obj"),
            script_file = new_script,
        )
    def reimport(self, context):
        bpy.ops.import_scene.obj(filepath=os.path.join(self.tmp.name, "tmp.o.obj"))

# Custom methods

class Basic(base.BaseRemesher):
    bl_idname = "bakemyscan.remesh_decimate"
    bl_label  = "Basic decimate"
    workonduplis = True

    limit    = bpy.props.IntProperty(description="Target faces", default=1500, min=50, max=500000)
    vertex_group = bpy.props.BoolProperty(description="Use vertex group", default=True)
    factor = bpy.props.FloatProperty(description="Weight factor", default=0.5, min=0., max=1.)

    def draw(self, context):
        self.layout.prop(self, "limit", text="Number of faces")
        self.layout.prop(self, "vertex_group", text="Use weights")

    def remesh(self, context):
        lr = self.copiedobject
        hr = self.initialobject
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].ratio = float(self.limit/len(lr.data.polygons))
        bpy.context.object.modifiers["Decimate"].use_collapse_triangulate = True
        if len(bpy.context.object.vertex_groups)>0 and self.vertex_group:
            bpy.context.object.modifiers["Decimate"].vertex_group = bpy.context.object.vertex_groups[0].name
            bpy.context.object.modifiers["Decimate"].vertex_group_factor = self.factor
            bpy.context.object.modifiers["Decimate"].invert_vertex_group = True
        bpy.ops.object.modifier_apply(modifier="Decimate")

class Quads(base.BaseRemesher):
    bl_idname = "bakemyscan.remesh_quads"
    bl_label  = "Dirty quads"
    workonduplis = True

    nfaces = bpy.props.IntProperty(name="nfaces",   description="Decimate ratio",  default=1500, min=50, max=200000)
    smooth = bpy.props.IntProperty(  name="smooth", description="Smoothing steps", default=1, min=0, max=15)
    vertex_group = bpy.props.BoolProperty(name="vertex_group", description="Use vertex group", default=True)
    factor = bpy.props.FloatProperty(description="Weight factor", default=0.5, min=0., max=1.)

    def draw(self, context):
        self.layout.prop(self, "nfaces",  text="Number of quads (min)")
        self.layout.prop(self, "smooth", text="Use weights")
        self.layout.prop(self, "smooth", text="Relaxation steps")

    def remesh(self, context):
        lr = self.copiedobject
        hr = self.initialobject

        #Guess the resulting number of faces
        ratio = 2 * self.nfaces / ( 4 * len(lr.data.polygons) )

        #Decimate it
        print("Decimating with ratio %.4f" % ratio)
        bpy.ops.object.modifier_add(type='DECIMATE')
        if len(bpy.context.object.vertex_groups)>0 and self.vertex_group:
            bpy.context.object.modifiers["Decimate"].vertex_group = bpy.context.object.vertex_groups[0].name
            bpy.context.object.modifiers["Decimate"].vertex_group_factor = self.factor
            bpy.context.object.modifiers["Decimate"].invert_vertex_group = True
        bpy.context.object.modifiers["Decimate"].ratio = ratio
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

        #Tris to quads
        print("Converting triangles to quadrilaterals")
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.tris_convert_to_quads(face_threshold=3.14159, shape_threshold=3.14159)
        bpy.ops.object.editmode_toggle()

        #Subdivision
        print("Subdividing")
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels = 1
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")

        #Relaxation steps
        print("Relaxation steps")
        for i in range(self.smooth):
            print("Smoothing: %d/%d" % (i+1, self.smooth))
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.vertices_smooth()
            bpy.ops.object.editmode_toggle()

            #Shrinkwrap to the original
            print("Shrinkwrapping: %d/%d" % (i+1, self.smooth))
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers["Shrinkwrap"].target = hr
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")

        #Smoothing
        print("Ultimate smoothing?")
        """
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.vertices_smooth()
        bpy.ops.object.editmode_toggle()
        """

class Iterative(base.BaseRemesher):
    bl_idname = "bakemyscan.remesh_iterative"
    bl_label  = "Iterative method"
    workonduplis = True

    limit    = bpy.props.IntProperty(name="limit",    description="Target faces", default=1500, min=50, max=500000)
    vertex_group = bpy.props.BoolProperty(name="vertex_group", description="Use vertex group", default=False)
    factor = bpy.props.FloatProperty(description="Weight factor", default=0.5, min=0., max=1.)

    def draw(self, context):
        self.layout.prop(self, "limit", text="target triangles")
        self.layout.prop(self, "vertex_group", text="use weight paint")

    def do_one_iteration(self):
        print("  -- Planar decimation")
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
        if len(bpy.context.object.vertex_groups)>0 and self.vertex_group:
            bpy.context.object.modifiers["Decimate"].vertex_group = bpy.context.object.vertex_groups[0].name
            bpy.context.object.modifiers["Decimate"].vertex_group_factor = self.factor
            bpy.context.object.modifiers["Decimate"].invert_vertex_group = True
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
        print("  -- Ensuring triangles only")
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.object.editmode_toggle()
        print("  -- Initial smoothing")
        bpy.ops.object.modifier_add(type='SMOOTH')
        bpy.context.object.modifiers["Smooth"].iterations = 1
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Smooth")
        print("  -- Initial decimation")
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].ratio = 0.75
        if len(bpy.context.object.vertex_groups)>0 and self.vertex_group:
            bpy.context.object.modifiers["Decimate"].vertex_group = bpy.context.object.vertex_groups[0].name
            bpy.context.object.modifiers["Decimate"].vertex_group_factor = self.factor
            bpy.context.object.modifiers["Decimate"].invert_vertex_group = True
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
        print("  -- Shrinkwrap")
        bpy.ops.object.modifier_add(type='SHRINKWRAP')
        bpy.context.object.modifiers["Shrinkwrap"].target = bpy.types.Scene.hr
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")

    def remesh(self, context):
        lr = self.copiedobject
        hr = self.initialobject

        #First coarse decimate to get a medium poly model
        if len(lr.data.polygons) > 50 * self.limit:
            print("-- First decimation because nTris > 50 x target")
            target = min(50 * self.limit, len(lr.data.polygons)/5)
            lr.modifiers.new("decimate", type='DECIMATE')
            lr.modifiers["decimate"].ratio = float(target/len(lr.data.polygons))
            lr.modifiers["decimate"].use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(modifier="decimate")

        #Iteration process to reach 1.5 x limit
        bpy.types.Scene.hr = hr
        iterate = True
        i = 0
        while(iterate):
            i+=1
            print("-- Iteration %d:" % i)
            lr = context.scene.objects.active
            bpy.ops.object.duplicate()
            self.do_one_iteration()
            tmp = context.scene.objects.active
            print("-- Iteration %d: %d tris -> %d tris" % (i, len(lr.data.polygons), len(tmp.data.polygons)) )
            if len(tmp.data.polygons) < self.limit:
                print("-- We went far enough, cancel the last iteration")
                iterate=False
                bpy.data.objects.remove(tmp)
                bpy.context.scene.objects.active = lr
                lr.select = True
            else:
                bpy.data.objects.remove(lr)
        del bpy.types.Scene.hr

        #Final decimation to stick to the limit
        print("-- Last decimate to be as exact as possible")
        lr.modifiers.new("decimate", type='DECIMATE')
        lr.modifiers["decimate"].ratio = float(self.limit/len(lr.data.polygons))
        lr.modifiers["decimate"].use_collapse_triangulate = True
        if len(bpy.context.object.vertex_groups)>0 and self.vertex_group:
            lr.modifiers["decimate"].vertex_group = bpy.context.object.vertex_groups[0].name
            lr.modifiers["decimate"].vertex_group_factor = self.factor
            lr.modifiers["decimate"].invert_vertex_group = True
        bpy.ops.object.modifier_apply(modifier="decimate")

        #Remove hypothetical material
        while len(context.active_object.material_slots):
            context.active_object.active_material_index = 0
            bpy.ops.object.material_slot_remove()

        # 6 - Remove doubles
        print("-- Removing degenerates")
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.mesh.dissolve_degenerate(threshold=0.0001)
        bpy.ops.mesh.vert_connect_nonplanar()
        bpy.ops.object.editmode_toggle()


def register() :
    bpy.utils.register_class(Quadriflow)
    bpy.utils.register_class(Mmgs)
    bpy.utils.register_class(Instant)
    bpy.utils.register_class(Meshlab)
    bpy.utils.register_class(Basic)
    bpy.utils.register_class(Iterative)
    bpy.utils.register_class(Quads)

def unregister() :
    bpy.utils.unregister_class(Quadriflow)
    bpy.utils.unregister_class(Mmgs)
    bpy.utils.unregister_class(Instant)
    bpy.utils.unregister_class(Meshlab)
    bpy.utils.unregister_class(Basic)
    bpy.utils.unregister_class(Iterative)
    bpy.utils.unregister_class(Quads)
