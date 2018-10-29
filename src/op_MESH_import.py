import bpy
from bpy_extras.io_utils import ImportHelper
import bmesh
import colorsys
import numpy as np
import os
import sys
import mathutils

from . import fn_msh

class import_mesh(bpy.types.Operator, ImportHelper):
    """Import a Mesh file"""
    bl_idname = "bakemyscan.import_mesh"
    bl_label  = "Imports a .mesh file"
    filter_glob = bpy.props.StringProperty(
        default="*.mesh",
        options={'HIDDEN'},
    )
    check_extension = True
    filename_ext = ".mesh"

    @classmethod
    def poll(cls, context):
        if context.mode!="OBJECT":
            return 0
        return 1

    def execute(self, context):
        keywords = self.as_keywords(ignore=('filter_glob','check_existing'))
        err = meshImport(self, context, **keywords)
        if err:
            return {'CANCELLED'}
        else:
            return {'FINISHED'}

def meshImport(operator, context, filepath):
    MESH = fn_msh.Mesh(filepath)
    if os.path.exists(filepath[:-5]+".sol"):
        MESH.readSol()
    MESH.tets = fn_msh.np.array([])
    MESH.discardUnused()

    meshes = []
    rTris = MESH.tris[:,-1].tolist() if len(MESH.tris)>0 else []
    rQuads = MESH.quads[:,-1].tolist() if len(MESH.quads)>0 else []
    tris = [t.tolist() for t in MESH.tris]
    quads = [q.tolist() for q in MESH.quads]
    verts = [v.tolist()[:-1] for v in MESH.verts]
    REFS = set(rTris + rQuads)

    for i,r in enumerate(REFS):
        refFaces = [t[:-1] for t in tris + quads if t[-1]==r]
        #refFaces = refFaces + [[q[:-1] for q in quads if q[-1] == r]]
        mesh_name = bpy.path.display_name_from_filepath(filepath)
        mesh = bpy.data.meshes.new(name=mesh_name)
        meshes.append(mesh)
        mesh.from_pydata(verts, [], refFaces)
        mesh.validate()
        mesh.update()

    if not meshes:
        return 1

    scene = context.scene

    objects = []
    for i,m in enumerate(meshes):
        obj = bpy.data.objects.new(m.name, m)
        bpy.ops.object.select_all(action='DESELECT')
        scene.objects.link(obj)
        scene.objects.active = obj
        mat = bpy.data.materials.new(m.name+"_material_"+str(i))
        if i==0:
            mat.diffuse_color = colorsys.hsv_to_rgb(0,0,1)
        else:
            mat.diffuse_color = colorsys.hsv_to_rgb(float(i/len(meshes)),1,1)
        obj.data.materials.append(mat)
        objects.append(obj)
    del meshes

    scene.update()
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:
        o.select=True
    if len(objects)>1:
        bpy.ops.object.join()

    remove_doubles = False
    if remove_doubles:
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.editmode_toggle()

    #Solutions according to the weight paint mode (0 to 1 by default)
    if len(MESH.vectors) > 0:
        bpy.ops.object.vertex_group_add()
        vgrp = bpy.context.active_object.vertex_groups[0]
        for X in tris+quads:
            for x in X:
                vgrp.add([x],fn_msh.np.linalg.norm(MESH.vectors[x]),"REPLACE")
    elif len(MESH.scalars) > 0:
        bpy.ops.object.vertex_group_add()
        vgrp = bpy.context.active_object.vertex_groups[0]
        for X in tris+quads:
            for x in X:
                vgrp.add([x],MESH.scalars[x],"REPLACE")

    #Transform weight to vertex colors
    if len(MESH.vectors) > 0 or len(MESH.scalars) > 0:

        #Normalize weight paint color
        bpy.ops.paint.weight_paint_toggle()
        bpy.ops.object.vertex_group_normalize()
        bpy.ops.paint.weight_paint_toggle()

        me=context.active_object
        verts=me.data.vertices

        col=mathutils.Color()
        col.h=0
        col.s=1
        col.v=1

        try:
            assert bpy.context.active_object.vertex_groups
            if not bpy.context.active_object.data.vertex_colors:
                bpy.context.active_object.data.vertex_colors.new()
            assert bpy.context.active_object.data.vertex_colors

        except AssertionError:
            print('you need at least one vertex group and one color group')
            return

        vgrp=bpy.context.active_object.vertex_groups.keys()
        vcolgrp=bpy.context.active_object.data.vertex_colors

        colored = False
        #Colored
        if colored:
            for poly in me.data.polygons:
                for loop in poly.loop_indices:
                    vertindex=me.data.loops[loop].vertex_index
                    #Check to see if the vertex has any geoup association
                    try:
                        weight=me.vertex_groups.active.weight(vertindex)
                    except:
                       continue
                    #col=Color ((r, g, b ))
                    col.h=0.66*weight
                    col.s=1
                    col.v=1
                    me.data.vertex_colors.active.data[loop].color = (col.b, col.g, col.r)


        if not colored:
            for poly in me.data.polygons:
                for loop in poly.loop_indices:
                    vertindex=me.data.loops[loop].vertex_index
                    #weight=me.vertex_groups['Group'].weight(vertindex)
                    #Check to see if the vertex has any geoup association
                    try:
                        weight=me.vertex_groups.active.weight(vertindex)
                    except:
                        continue
                    col.r=weight
                    col.g=col.r
                    col.b=col.r
                    me.data.vertex_colors.active.data[loop].color = (col.b, col.g, col.r)

        #update
        context.active_object.data.update()

    del MESH
    del verts, tris, quads

    return 0

def import_func(self, context):
    self.layout.operator("bakemyscan.import_mesh", text="MESH (.mesh)")

def register():
    bpy.utils.register_class(import_mesh)
    bpy.types.INFO_MT_file_import.append(import_func)

def unregister():
    bpy.utils.unregister_class(import_mesh)
    bpy.types.INFO_MT_file_import.remove(import_func)
