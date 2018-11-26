import bpy
import os
from . import fn_soft
import tempfile
import time
from mathutils import Vector
import numpy as np

import addon_utils

from . import op_REMESHERS_BASE as base

#Make a model symetrical on the x axis
class Symmetry(base.BaseRemesher):
    bl_idname = "bakemyscan.symetrize"
    bl_label  = "Symmetry"

    workonduplis  = True
    keepMaterials = True
    hide_old      = True

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
class Relax(base.BaseRemesher):
    bl_idname = "bakemyscan.relax"
    bl_label  = "Relaxation"

    workonduplis  = True
    keepMaterials = True
    hide_old      = True

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
        #hr.hide = True
        #bpy.data.objects.remove(hr)

        return {"FINISHED"}

#Make an object manifold
class Manifold(base.BaseRemesher):
    bl_idname = "bakemyscan.manifold"
    bl_label  = "Make manifold"

    workonduplis  = True
    keepMaterials = True
    hide_old      = True

    manifold_method = bpy.props.EnumProperty(
        items= (
            ('print3d', '3D print toolbox', ''),
            ('manifold', 'Manifold', ''),
            ('fill', 'Fill non manifold', ''),
            ("meshlab", "Meshlab", "")
        ),
        name="manifold_method",
        description="Manifold method",
        default="fill"
    )

    def draw(self, context):
        self.layout.prop(self, "manifold_method", text="Method")

    def remesh(self, context):
        lr = self.copiedobject
        hr = self.initialobject

        if self.manifold_method == "print3d":
            isloaded = addon_utils.check("object_print3d_utils")[0]
            if not isloaded:
                addon_utils.enable("object_print3d_utils")
            bpy.ops.mesh.print3d_clean_non_manifold()
            if not isloaded:
                addon_utils.disable("object_print3d_utils")

        elif self.manifold_method == "fill":
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_mode(type="EDGE")
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.mesh.fill()
            bpy.ops.object.editmode_toggle()

        elif self.manifold_method == "manifold":
            self.report({"ERROR"}, "Manifold is not implemented yet")
            return {"CANCELLED"}

        elif self.manifold_method == "meshlab":
            self.report({"ERROR"}, "Meshlab manifolding is not implemented yet")
            return {"CANCELLED"}

        return {"FINISHED"}

def register() :
    bpy.utils.register_class(Symmetry)
    bpy.utils.register_class(Relax)
    bpy.utils.register_class(Manifold)

def unregister() :
    bpy.utils.unregister_class(Symmetry)
    bpy.utils.unregister_class(Relax)
    bpy.utils.unregister_class(Manifold)
