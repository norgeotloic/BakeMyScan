import bpy
from bpy_extras.io_utils import ExportHelper
import bmesh
import colorsys
import numpy as np
import os
import sys

from . import fn_msh

class export_mesh(bpy.types.Operator, ExportHelper):
    """Export a Mesh file"""
    bl_idname = "bakemyscan.export_mesh"
    bl_label  = "Exports a .mesh file"

    filter_glob = bpy.props.StringProperty(
        default="*.mesh",
        options={'HIDDEN'},
    )
    check_extension = True
    filename_ext = ".mesh"
    refAtVerts = bpy.props.BoolProperty(name="refAtVerts", description="reference at vertices", default=False)
    triangulate = bpy.props.BoolProperty(name="triangulate", description="triangulate the mesh", default=True)
    miniSol = bpy.props.FloatProperty(name="miniSol", description="Minimum value for the scalar field", default=0.01, subtype="FACTOR")
    maxiSol = bpy.props.FloatProperty(name="maxiSol", description="Maximum value for the scalar field", default=1, subtype="FACTOR")

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and len(context.selected_objects)==1
            and context.mode=="OBJECT"
        )

    def execute(self, context):
        keywords = self.as_keywords(ignore=('filter_glob','check_existing'))
        err = export(self, context, **keywords)
        if err:
            return {'CANCELLED'}
        else:
            return {'FINISHED'}
def export(operator, context, filepath, refAtVerts, triangulate, miniSol, maxiSol):
    #Get the selected object
    APPLY_MODIFIERS = True
    scene = context.scene
    bpy.ops.object.duplicate()
    obj = scene.objects.active

    #Convert the big n-gons in triangles if necessary
    bpy.context.tool_settings.mesh_select_mode=(False,False,True)
    bpy.ops.object.convert(target='MESH')

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
    if triangulate:
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_face_by_sides(number=3, type='GREATER')
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
    bpy.ops.object.editmode_toggle()

    mesh = obj.to_mesh(scene, APPLY_MODIFIERS, 'PREVIEW')
    mesh.transform(obj.matrix_world)

    #Get the info
    verts = [[v.co[0], v.co[1], v.co[2], 0] for v in mesh.vertices[:]]
    triangles = [ [v for v in f.vertices] + [f.material_index + 1] for f in mesh.polygons if len(f.vertices) == 3 ]
    quads = [ [v for v in f.vertices] + [f.material_index + 1]  for f in mesh.polygons if len(f.vertices) == 4 ]
    edges = [[e.vertices[0], e.vertices[1], 0] for e in mesh.edges if e.use_edge_sharp]

    if refAtVerts:
        for i in range(len(obj.data.materials[:])):
            for f in mesh.polygons:
                if f.material_index == i:
                    for v in f.vertices:
                        verts[v][3] = f.material_index + 1

    exportMesh = fn_msh.Mesh()
    exportMesh.verts = fn_msh.np.array(verts)
    exportMesh.tris  = fn_msh.np.array(triangles)
    exportMesh.quads = fn_msh.np.array(quads)
    exportMesh.edges = fn_msh.np.array(edges)
    exportMesh.write(filepath)

    #Solutions according to the weight paint mode (0 to 1 by default)
    vgrp = bpy.context.active_object.vertex_groups.keys()
    if(len(vgrp)>0):
        GROUP = bpy.context.active_object.vertex_groups.active
        cols = [0.0] * len(verts)
        for i,t in enumerate(mesh.polygons):
            for j,v in enumerate(t.vertices):
                try:
                    cols[v] = float(GROUP.weight(v))
                except:
                    continue
        try:
            mini = bpy.context.scene["mmgsMini"]
            maxi = bpy.context.scene["mmgsMaxi"]
            exportMesh.scalars = fn_msh.np.array(cols)*(maxi - mini) + mini
            print("Min and max values taken from the scene property")
        except:
            exportMesh.scalars = fn_msh.np.array(cols)*(maxiSol - miniSol) + miniSol
            print("Min and max values taken from the operator property")
        exportMesh.writeSol(filepath[:-5] + ".sol")

    bpy.ops.object.delete()
    bpy.data.meshes.remove(mesh)
    del exportMesh

    return 0

def export_func(self, context):
    self.layout.operator("bakemyscan.export_mesh", text="MESH (.mesh)")
def register():
    bpy.utils.register_class(export_mesh)
    bpy.types.INFO_MT_file_export.append(export_func)
def unregister():
    bpy.utils.unregister_class(export_mesh)
    bpy.types.INFO_MT_file_export.remove(export_func)
