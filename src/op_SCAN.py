# coding: utf8
import bpy
import os
import imghdr
from . import fn_soft

class colmap_auto(bpy.types.Operator):
    bl_idname = "bakemyscan.colmap_auto"
    bl_label  = "Use colmap"
    bl_options = {"REGISTER"}


    mesher  = bpy.props.EnumProperty(items= ( ('delaunay', 'delaunay', 'delaunay'), ("poisson", "poisson", "poisson")) , description="Mesher", default="delaunay")
    quality = bpy.props.EnumProperty(items= ( ('low', 'low', 'low'), ("medium", "medium", "medium"), ("high", "high", "high")) , description="Quality", default="medium")

    sparse = bpy.props.BoolProperty(description="Sparse", default=True)
    dense  = bpy.props.BoolProperty(description="Dense", default=True)
    single = bpy.props.BoolProperty(description="Single Camera", default=True)
    gpu    = bpy.props.BoolProperty(description="GPU", default=True)

    def check(self, context):
        return True
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    def draw(self, context):
        self.layout.prop(self, "mesher",  text="Mesher")
        self.layout.prop(self, "quality", text="Quality")
        self.layout.prop(self, "sparse",  text="Sparse")
        self.layout.prop(self, "dense",   text="Dense")
        self.layout.prop(self, "single",  text="Single Camera")
        self.layout.prop(self, "gpu",  text="GPU")
        col = self.layout.column(align=True)

    @classmethod
    def poll(self, context):
        #Need to be in Cycles render mode
        D = bpy.types.Scene.imgpaths
        if D=="":
            return 0
        if not os.path.exists(D):
            return 0
        if len([imghdr.what(os.path.join(D,x)) for x in os.listdir(D) if not os.path.isdir(os.path.join(D,x))]) == 0:
            return 0
        if bpy.types.Scene.executables["colmap"] == "":
            return 0
        return 1

    def execute(self, context):
        if True:
            D = bpy.types.Scene.imgpaths
            self.results = fn_soft.colmap_auto(
                colmap        = bpy.types.Scene.executables["colmap"],
                workspace     = D,
                images        = D,
                mesher        = self.mesher,
                quality       = self.quality,
                sparse        = 1 if self.sparse else 0,
                dense         = 1 if self.sparse else 0,
                single_camera = 1 if self.single else 0,
                gpu           = self.gpu
            )
            return{'FINISHED'}
        else:
            print("Did not manage to run colmap")
            return{'CANCELLED'}


class colmap_openmvs(bpy.types.Operator):
    bl_idname = "bakemyscan.colmap_openmvs"
    bl_label  = "Colmap + OpenMVS"
    bl_options = {"REGISTER"}


    mesher  = bpy.props.EnumProperty(items= ( ('delaunay', 'delaunay', 'delaunay'), ("poisson", "poisson", "poisson")) , description="Mesher", default="delaunay")
    quality = bpy.props.EnumProperty(items= ( ('low', 'low', 'low'), ("medium", "medium", "medium"), ("high", "high", "high")) , description="Quality", default="medium")

    sparse = bpy.props.BoolProperty(description="Sparse", default=True)
    dense  = bpy.props.BoolProperty(description="Dense", default=True)
    single = bpy.props.BoolProperty(description="Single Camera", default=True)

    def check(self, context):
        return True
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    def draw(self, context):
        self.layout.prop(self, "mesher",  text="Mesher")
        self.layout.prop(self, "quality", text="Quality")
        self.layout.prop(self, "sparse",  text="Sparse")
        self.layout.prop(self, "dense",   text="Dense")
        self.layout.prop(self, "single",  text="Single Camera")
        col = self.layout.column(align=True)

    @classmethod
    def poll(self, context):
        #Need to be in Cycles render mode
        D = bpy.types.Scene.imgpaths
        if D=="":
            return 0
        if not os.path.exists(D):
            return 0
        if len([imghdr.what(os.path.join(D,x)) for x in os.listdir(D) if not os.path.isdir(os.path.join(D,x))]) == 0:
            return 0
        if bpy.types.Scene.executables["colmap"] == "":
            return 0
        if bpy.types.Scene.executables["densifypointcloud"] == "":
            return 0
        if bpy.types.Scene.executables["interfacevisualsfm"] == "":
            return 0
        if bpy.types.Scene.executables["reconstructmesh"] == "":
            return 0
        if bpy.types.Scene.executables["texturemesh"] == "":
            return 0
        if bpy.types.Scene.executables["meshlabserver"] == "":
            return 0
        return 1

    def execute(self, context):
        if True:
            D = bpy.types.Scene.imgpaths
            self.results = fn_soft.colmap_openmvs(
                workspace     = D,
                images        = D,
                mesher        = self.mesher,
                quality       = self.quality,
                sparse        = 1 if self.sparse else 0,
                dense         = 1 if self.sparse else 0,
                single_camera = 1 if self.single else 0,
                colmap=bpy.types.Scene.executables["colmap"],
                interfacevisualsfm = bpy.types.Scene.executables["interfacevisualsfm"],
                densifypointcloud = bpy.types.Scene.executables["densifypointcloud"],
                reconstructmesh = bpy.types.Scene.executables["reconstructmesh"],
                texturemesh = bpy.types.Scene.executables["texturemesh"],
                meshlabserver = bpy.types.Scene.executables["meshlabserver"],
            )
            return{'FINISHED'}
        else:
            print("Did not manage to run colmap")
            return{'CANCELLED'}



def register() :
    bpy.utils.register_class(colmap_auto)
    bpy.utils.register_class(colmap_openmvs)
def unregister() :
    bpy.utils.unregister_class(colmap_auto)
    bpy.utils.unregister_class(colmap_openmvs)
