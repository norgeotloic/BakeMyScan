import bpy
import os
from . import fn_soft
import tempfile
import time
from mathutils import Vector
import numpy as np

class BaseRemesher(bpy.types.Operator):
    bl_idname = "bakemyscan.empty_remesher"
    bl_label  = "Empty remersher structure"

    bl_options = {"REGISTER", "UNDO"}

    #For executable remeshers
    tmp        = tempfile.TemporaryDirectory()
    executable = None
    results    = []
    keepMaterials = False

    #For remeshers which need to duplicate the object
    workonduplis = False


    @classmethod
    def poll(self, context):
        if self.executable is not None:
            if executable == "":
                return 0
        if len(context.selected_objects)!=1 or context.active_object is None:
            return 0
        for o in context.selected_objects:
            if o.type != "MESH":
                return 0
        if context.mode!="OBJECT" and context.mode!="SCULPT":
            return 0
        return 1
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    #To be overridden
    def setexe(self, context):
        pass
    def export(self, context):
        pass
    def reimport(self, context):
        pass
    def remesh(self, context):
        pass
    def status(self, context):
        if self.results[2] != 0:
            self.report({"ERROR"}, "Remesh error, look in the console")
            print("OUTPUT:\n%s\nERROR:\n%s\CODE:\n%s" % self.results)
            return{"CANCELLED"}

    def preprocess(self, context):
        self.initialobject   = context.active_object
        self.existingobjects = [o for o in bpy.data.objects]
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        #Operators working on a duplicated object
        if self.workonduplis:
            bpy.ops.object.duplicate()
            self.copiedobject = context.scene.objects.active
            #Apply the modifiers
            for m in self.copiedobject.modifiers:
                bpy.ops.object.modifier_apply(modifier=m.name)
    def postprocess(self, context):
        #Check that there is only one new object
        newObjects = [o for o in bpy.data.objects if o not in self.existingobjects]
        if len(newObjects)==0:
            self.report({'ERROR'}, '0 new objects')
        elif len(newObjects)>1:
            self.report({'ERROR'}, '0 new objects')
        else:
            #Get the new object
            self.new = newObjects[0]
            #Make it selected and active
            bpy.ops.object.select_all(action='DESELECT')
            self.new.select=True
            bpy.context.scene.objects.active = self.new
            #Remove edges marked as sharp, and delete the loose geometry
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.mark_sharp(clear=True)
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.delete_loose()
            bpy.ops.object.editmode_toggle()
            #Shade smooth and rename it
            bpy.ops.object.shade_smooth()
            bpy.context.object.data.use_auto_smooth = False
            context.active_object.name = self.initialobject.name + "." + self.bl_label.lower().replace(" ","")
            #Remove hypothetical material
            if not self.keepMaterials:
                while len(context.active_object.material_slots):
                    context.active_object.active_material_index = 0
                    bpy.ops.object.material_slot_remove()
            #Hide the old object
            self.initialobject.hide = True
    def execute(self, context):
        #Set the executable path
        self.setexe(context)
        #Preprocess
        self.preprocess(context)
        #Export
        if self.executable is not None:
            self.exporttime = time.time()
            self.export(context)
            self.exporttime = time.time() - self.exporttime
        #Remesh
        self.remeshtime = time.time()
        self.remesh(context)
        self.remeshtime = time.time() - self.remeshtime
        #Check the output
        if self.executable is not None:
            self.status(context)
        #Import
        if self.executable is not None:
            self.importtime = time.time()
            try:
                self.reimport(context)
            except:
                self.report({"ERROR"}, "Import error, look in the console")
                print("OUTPUT:\n%s\nERROR:\n%s\CODE:\n%s" % self.results)
            self.importtime = time.time() - self.importtime
        #Post-process
        self.postprocess(context)
        #Show the wireframe (debug)
        #context.object.show_wire = True
        #context.object.show_all_edges = True
        #Report
        self.report({'INFO'}, 'Remeshed to %d polygons' % len(context.active_object.data.polygons))
        return{'FINISHED'}

# External software

class Quadriflow(BaseRemesher):
    bl_idname = "bakemyscan.remesh_quadriflow"
    bl_label  = "Quadriflow"

    resolution = bpy.props.IntProperty( name="resolution", description="Resolution", default=1000, min=10, max=100000 )

    def draw(self, context):
        self.layout.prop(self, "resolution", text="Resolution")
        col = self.layout.column(align=True)

    #Overriden methods
    def setexe(self, context):
        self.executable = context.user_preferences.addons["BakeMyScan"].preferences.quadriflow
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
        )

class Instant(BaseRemesher):
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
        self.executable = context.user_preferences.addons["BakeMyScan"].preferences.instant
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

class Mmgs(BaseRemesher):
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
        self.executable = context.user_preferences.addons["BakeMyScan"].preferences.mmgs
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

class Meshlab(BaseRemesher):
    bl_idname = "bakemyscan.remesh_meshlab"
    bl_label  = "Meshlab"

    facescount = bpy.props.IntProperty( name="facescount", description="Number of faces", default=5000, min=10, max=1000000 )

    def draw(self, context):
        self.layout.prop(self, "facescount", text="Number of faces")
        col = self.layout.column(align=True)

    #Overriden methods
    def setexe(self, context):
        self.executable = context.user_preferences.addons["BakeMyScan"].preferences.meshlabserver
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

class Basic(BaseRemesher):
    bl_idname = "bakemyscan.remesh_decimate"
    bl_label  = "Basic decimate"
    workonduplis = True

    limit    = bpy.props.IntProperty(name="limit",    description="Target faces", default=1500, min=50, max=500000)
    vertex_group = bpy.props.BoolProperty(name="vertex_group", description="Use vertex group", default=True)

    def draw(self, context):
        self.layout.prop(self, "limit", text="target triangles")

    def remesh(self, context):
        lr = self.copiedobject
        hr = self.initialobject
        lr.modifiers.new("decimate", type='DECIMATE')
        lr.modifiers["decimate"].ratio = float(self.limit/len(lr.data.polygons))
        lr.modifiers["decimate"].use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier="decimate")

class Quads(BaseRemesher):
    bl_idname = "bakemyscan.remesh_quads"
    bl_label  = "Dirty quads"
    workonduplis = True

    nfaces = bpy.props.IntProperty(name="nfaces",   description="Decimate ratio",  default=1500, min=50, max=200000)
    smooth = bpy.props.IntProperty(  name="smooth", description="Smoothing steps", default=1, min=0, max=15)

    def draw(self, context):
        self.layout.prop(self, "nfaces",  text="Number of quads (min)")
        self.layout.prop(self, "smooth", text="Relaxation steps")

    def remesh(self, context):
        lr = self.copiedobject
        hr = self.initialobject

        #Guess the resulting number of faces
        ratio = 2 * self.nfaces / ( 4 * len(lr.data.polygons) )

        #Decimate it
        print("Decimating with ratio %.4f" % ratio)
        bpy.ops.object.modifier_add(type='DECIMATE')
        if len(bpy.context.object.vertex_groups)>0:
            bpy.context.object.modifiers["Decimate"].vertex_group = bpy.context.object.vertex_groups[0].name
            bpy.context.object.modifiers["Decimate"].vertex_group_factor = 1
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


class Iterative(BaseRemesher):
    bl_idname = "bakemyscan.remesh_iterative"
    bl_label  = "Iterative method"
    workonduplis = True

    limit    = bpy.props.IntProperty(name="limit",    description="Target faces", default=1500, min=50, max=500000)
    manifold = bpy.props.BoolProperty(name="manifold", description="Make manifold", default=False)
    vertex_group = bpy.props.BoolProperty(name="vertex_group", description="Use vertex group", default=True)

    def draw(self, context):
        self.layout.prop(self, "limit", text="target triangles")
        self.layout.prop(self, "manifold", text="make manifold")

    def do_one_iteration(self):
        print("  -- Planar decimation")
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
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
        bpy.context.object.modifiers["Decimate"].ratio = 0.8
        if len(bpy.context.object.vertex_groups)>0 and self.vertex_group:
            bpy.context.object.modifiers["Decimate"].vertex_group = bpy.context.object.vertex_groups[0].name
            bpy.context.object.modifiers["Decimate"].vertex_group_factor = 0.75
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
        bpy.ops.object.modifier_apply(modifier="decimate")

        #Remove hypothetical material
        while len(context.active_object.material_slots):
            context.active_object.active_material_index = 0
            bpy.ops.object.material_slot_remove()

        # 6 - Remove non manifold and doubles
        print("-- Making manifold")
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.mesh.dissolve_degenerate(threshold=0.0001)
        bpy.ops.mesh.vert_connect_nonplanar()
        if self.manifold:
            addon_utils.enable("object_print3d_utils")
            bpy.ops.mesh.print3d_clean_non_manifold()
        bpy.ops.object.editmode_toggle()


#Make a model symetrical on the x axis
class Symmetry(BaseRemesher):
    bl_idname = "bakemyscan.symetrize"
    bl_label  = "Symmetry"

    workonduplis  = True
    keepMaterials = True

    center = bpy.props.EnumProperty(
        items= (
            ('bbox','bbox','bbox'),
            ('cursor','cursor','cursor'),
            #Maybe more to come in the future depending on user feedbacks!
        ),
        description="center",
        default="bbox"
    )
    axis = bpy.props.EnumProperty(
        items= (
            ('-X','-X','-X'),
            ('+X','+X','+X'),
            ('-Y','-Y','-Y'),
            ('+Y','+Y','+Y'),
            ('-Z','-Z','-Z'),
            ('+Z','+Z','+Z')
        ),
        description="axis",
        default="-X"
    )

    def remesh(self, context):
        lr = self.copiedobject
        hr = self.initialobject

        #Get the symmetry center depending on the method (maybe apply obj.matrix_world?)
        cursor = bpy.context.scene.cursor_location

        center, dim = None, None
        if self.center == "bbox":
            localBb = 0.125 * sum((Vector(b) for b in lr.bound_box), Vector())
            center  = lr.matrix_world * localBb
            if "X" in self.axis:
                dim = lr.dimensions[0]
            elif "Y" in self.axis:
                dim = lr.dimensions[1]
            elif "Z" in self.axis:
                dim = lr.dimensions[2]
        elif self.center == "cursor":
            center = cursor.copy()
            #Get the maximum distance between 3D cursor and bbox points
            dim = 0
            corners = [lr.matrix_world * Vector(v) for v in lr.bound_box]
            #Find the distance
            for corner in corners:
                #Get the corner projected on the desired axis
                cornProj, cursProj = 0, 0
                if "X" in self.axis:
                    cornProj, cursProj = corner[0], cursor[0]
                elif "Y" in self.axis:
                    cornProj, cursProj = corner[1], cursor[1]
                elif "Z" in self.axis:
                    cornProj, cursProj = corner[2], cursor[2]
                #Compute the distance
                dist   = np.sqrt((cornProj - cursProj)**2)
                if dist > dim:
                    dim = dist

        #Compute the cube translation so that its face is on the center
        offset = center.copy()
        if self.axis=="-X":
            offset[0] = offset[0] + 5*dim/2
        if self.axis=="+X":
            offset[0] = offset[0] - 5*dim/2
        if self.axis=="-Y":
            offset[1] = offset[1] +5* dim/2
        if self.axis=="+Y":
            offset[1] = offset[1] -5* dim/2
        if self.axis=="-Z":
            offset[2] = offset[2] + 5*dim/2
        if self.axis=="+Z":
            offset[2] = offset[2] - 5*dim/2

        bpy.ops.mesh.primitive_cube_add(radius=5*dim / 2 , view_align=False, enter_editmode=False, location=offset)
        cube = context.active_object

        #Make the original object active once again
        bpy.ops.object.select_all(action='DESELECT')
        context.scene.objects.active = lr
        lr.select = True

        #boolean cut
        bpy.ops.object.modifier_add(type='BOOLEAN')
        lr.modifiers["Boolean"].operation = 'DIFFERENCE'
        lr.modifiers["Boolean"].object    = cube
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean")

        #Remove the cube
        bpy.data.objects.remove(cube)

        #Make the original object active once again
        bpy.ops.object.select_all(action='DESELECT')
        context.scene.objects.active = lr
        lr.select             = True

        #Add a mirror modifier
        bpy.ops.object.modifier_add(type='MIRROR')
        mod = bpy.context.object.modifiers["Mirror"]
        mod.use_clip = True
        #Set the correct axis
        if "Y" in self.axis:
            mod.use_x = False
            mod.use_y = True
        if "Z" in self.axis:
            mod.use_x = False
            mod.use_z = True
        #Add an empty at the cursor or bbox center
        if self.center == "cursor":
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=cursor)
        elif self.center == "bbox":
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=center)
        empty = context.active_object
        mod.mirror_object = empty
        #Make the original object active once again
        bpy.ops.object.select_all(action='DESELECT')
        context.scene.objects.active = lr
        lr.select             = True
        #Apply
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Mirror")
        #Remove the empty
        bpy.data.objects.remove(empty)

        #Remove faces with too big a number of polygons, created because of the boolean
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_face_by_sides(number=8, type='GREATER')
        bpy.ops.mesh.delete(type='ONLY_FACE')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.editmode_toggle()

        #Make the original object active once again
        bpy.ops.object.select_all(action='DESELECT')
        context.scene.objects.active = lr
        lr.select              = True

        return {"FINISHED"}

#Relax the topology
class Relax(BaseRemesher):
    bl_idname = "bakemyscan.relax"
    bl_label  = "Relaxation"

    workonduplis  = True
    keepMaterials = True

    smooth = bpy.props.IntProperty(  name="smooth", description="Relaxation steps", default=2, min=0, max=150)

    def draw(self, context):
        self.layout.prop(self, "smooth", text="Relaxation steps")

    def remesh(self, context):
        lr = self.copiedobject
        hr = self.initialobject

        #Add a few shrinkwrapping / smoothing iterations to relax the surface
        for i in range(self.smooth):
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers["Shrinkwrap"].target = hr
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")
            bpy.ops.object.select_all(action='TOGGLE')
            bpy.ops.object.modifier_add(type='SMOOTH')
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Smooth")

        #With one last small smoothing step
        if self.smooth > 0:
            bpy.ops.object.modifier_add(type='SMOOTH')
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Smooth")

        #Make the original object active once again
        bpy.ops.object.select_all(action='DESELECT')
        context.scene.objects.active = lr
        lr.select              = True

        #Hide the original object?
        hr.hide = True
        #bpy.data.objects.remove(hr)

        return {"FINISHED"}



def register() :
    bpy.utils.register_class(BaseRemesher)
    bpy.utils.register_class(Quadriflow)
    bpy.utils.register_class(Mmgs)
    bpy.utils.register_class(Instant)
    bpy.utils.register_class(Meshlab)
    bpy.utils.register_class(Basic)
    bpy.utils.register_class(Iterative)
    bpy.utils.register_class(Quads)
    bpy.utils.register_class(Symmetry)
    bpy.utils.register_class(Relax)

def unregister() :
    bpy.utils.unregister_class(BaseRemesher)
    bpy.utils.unregister_class(Quadriflow)
    bpy.utils.unregister_class(Mmgs)
    bpy.utils.unregister_class(Instant)
    bpy.utils.unregister_class(Meshlab)
    bpy.utils.unregister_class(Basic)
    bpy.utils.unregister_class(Iterative)
    bpy.utils.unregister_class(Quads)
    bpy.utils.unregister_class(Symmetry)
    bpy.utils.unregister_class(Relax)
