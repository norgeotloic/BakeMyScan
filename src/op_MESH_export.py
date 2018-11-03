import bpy
from bpy_extras.io_utils import ExportHelper
import bmesh
import os

from . import fn_msh

class export_mesh(bpy.types.Operator, ExportHelper):

    #Operator info
    bl_idname = "bakemyscan.export_mesh"
    bl_label  = "Exports a .mesh file"

    #ExportHelper settings
    filter_glob = bpy.props.StringProperty(
        default="*.mesh",
        options={'HIDDEN'},
    )
    check_extension = True
    filename_ext = ".mesh"
    filepath = bpy.props.StringProperty(
        name="Export mesh file",
        description="New mesh file to export to",
        maxlen= 1024,
        default= ""
    )

    #Operator properties
    writeSol    = bpy.props.FloatProperty(name="writeSol", description="Write the .sol if weight paints are present", default=False)
    miniSol     = bpy.props.FloatProperty(name="miniSol",  description="Minimum scalar", default=0.01, subtype="FACTOR")
    maxiSol     = bpy.props.FloatProperty(name="maxiSol",  description="Maximum scalar", default=1, subtype="FACTOR")


    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and len(context.selected_objects)==1
            and context.mode=="OBJECT"
        )

    def execute(self, context):

        #Duplicate the selected object and make the duplicate active
        bpy.ops.object.duplicate()
        obj = context.scene.objects.active

        #Convert ngons to triangles
        bpy.context.tool_settings.mesh_select_mode=(False,False,True)
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_face_by_sides(number=3, type='GREATER')
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.object.editmode_toggle()

        #Get the mesh, with the modifiers and transformations applied
        mesh = obj.to_mesh(context.scene, True, 'PREVIEW')
        mesh.transform(obj.matrix_world)

        #Get the relevant mesh information
        verts     = [[v.co[0], v.co[1], v.co[2], 0] for v in mesh.vertices[:]]
        triangles = [ [v for v in f.vertices] + [f.material_index + 1] for f in mesh.polygons if len(f.vertices) == 3 ]
        quads     = [ [v for v in f.vertices] + [f.material_index + 1]  for f in mesh.polygons if len(f.vertices) == 4 ]
        edges     = [ [e.vertices[0], e.vertices[1], 0] for e in mesh.edges if e.use_edge_sharp]

        #Prepare the mesh to export
        exportMesh = fn_msh.Mesh()
        exportMesh.verts = fn_msh.np.array(verts)
        exportMesh.tris  = fn_msh.np.array(triangles)
        exportMesh.quads = fn_msh.np.array(quads)
        exportMesh.edges = fn_msh.np.array(edges)
        exportMesh.write(self.filepath)

        #Write a solution file according to the weight paint mode
        vgrp = bpy.context.active_object.vertex_groups.keys()
        if len(vgrp)>0 and self.writeSol:
            GROUP = bpy.context.active_object.vertex_groups.active
            cols = [0.0] * len(verts)
            for i,t in enumerate(mesh.polygons):
                for j,v in enumerate(t.vertices):
                    try:
                        cols[v] = 1.0 - float(GROUP.weight(v))
                    except:
                        cols[v] = 1.0
            exportMesh.scalars = fn_msh.np.array(cols)*(self.maxiSol - self.miniSol) + self.miniSol
            exportMesh.writeSol(self.filepath.replace(".mesh", ".sol"))

        #Delete the copy of the original mesh
        bpy.ops.object.delete()
        bpy.data.meshes.remove(mesh)
        del exportMesh

        return {'FINISHED'}

def export_func(self, context):
    self.layout.operator("bakemyscan.export_mesh", text="MESH (.mesh)")

def register():
    bpy.utils.register_class(export_mesh)
    bpy.types.INFO_MT_file_export.append(export_func)

def unregister():
    bpy.utils.unregister_class(export_mesh)
    bpy.types.INFO_MT_file_export.remove(export_func)
